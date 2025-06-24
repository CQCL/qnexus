"""Client API for QIR in Nexus."""

import base64
from datetime import datetime
from typing import Any, Union, cast
from uuid import UUID

import qnexus.exceptions as qnx_exc
from qnexus.client import get_nexus_client
from qnexus.client.nexus_iterator import NexusIterator
from qnexus.client.utils import handle_fetch_errors
from qnexus.context import (
    get_active_project,
    merge_project_from_context,
    merge_properties_from_context,
)
from qnexus.models.annotations import Annotations, CreateAnnotations, PropertiesDict
from qnexus.models.filters import (
    CreatorFilter,
    FuzzyNameFilter,
    PaginationFilter,
    ProjectRefFilter,
    PropertiesFilter,
    ScopeFilter,
    ScopeFilterEnum,
    SortFilter,
    SortFilterEnum,
    TimeFilter,
)
from qnexus.models.references import DataframableList, ProjectRef, QIRRef


class Params(
    SortFilter,
    PaginationFilter,
    FuzzyNameFilter,
    CreatorFilter,
    ProjectRefFilter,
    PropertiesFilter,
    TimeFilter,
    ScopeFilter,
):
    """Params for filtering QIRs."""


@merge_project_from_context
def get_all(
    name_like: str | None = None,
    creator_email: list[str] | None = None,
    project: ProjectRef | None = None,
    properties: PropertiesDict | None = None,
    created_before: datetime | None = None,
    created_after: datetime | None = datetime(day=1, month=1, year=2023),
    modified_before: datetime | None = None,
    modified_after: datetime | None = None,
    sort_filters: list[SortFilterEnum] | None = None,
    page_number: int | None = None,
    page_size: int | None = None,
    scope: ScopeFilterEnum | None = None,
) -> NexusIterator[QIRRef]:
    """Get a NexusIterator over QIRs with optional filters."""

    params = Params(
        name_like=name_like,
        creator_email=creator_email,
        properties=properties,
        project=project,
        created_before=created_before,
        created_after=created_after,
        modified_before=modified_before,
        modified_after=modified_after,
        sort=SortFilter.convert_sort_filters(sort_filters),
        page_number=page_number,
        page_size=page_size,
        scope=scope,
    ).model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    return NexusIterator(
        resource_type="QIR",
        nexus_url="/api/qir/v1beta",
        params=params,
        wrapper_method=_to_qir_ref,
        nexus_client=get_nexus_client(),
    )


def _to_qir_ref(page_json: dict[str, Any]) -> DataframableList[QIRRef]:
    """Convert JSON response dict to a list of QIRRefs."""

    qir_refs: DataframableList[QIRRef] = DataframableList([])

    for qir_data in page_json["data"]:
        project_id = qir_data["relationships"]["project"]["data"]["id"]
        project_details = next(
            proj for proj in page_json["included"] if proj["id"] == project_id
        )
        project = ProjectRef(
            id=project_id,
            annotations=Annotations.from_dict(project_details["attributes"]),
            contents_modified=project_details["attributes"]["contents_modified"],
            archived=project_details["attributes"]["archived"],
        )

        qir_refs.append(
            QIRRef(
                id=UUID(qir_data["id"]),
                annotations=Annotations.from_dict(qir_data["attributes"]),
                project=project,
            )
        )
    return qir_refs


def get(
    *,
    id: Union[UUID, str, None] = None,
    name_like: str | None = None,
    creator_email: list[str] | None = None,
    project: ProjectRef | None = None,
    properties: PropertiesDict | None = None,
    created_before: datetime | None = None,
    created_after: datetime | None = datetime(day=1, month=1, year=2023),
    modified_before: datetime | None = None,
    modified_after: datetime | None = None,
    sort_filters: list[SortFilterEnum] | None = None,
    page_number: int | None = None,
    page_size: int | None = None,
    scope: ScopeFilterEnum | None = None,
) -> QIRRef:
    """
    Get a single QIR using filters. Throws an exception if the filters do
    not match exactly one object.
    """

    if id:
        return _fetch_by_id(qir_id=id, scope=scope)

    return get_all(
        name_like=name_like,
        creator_email=creator_email,
        properties=properties,
        project=project,
        created_before=created_before,
        created_after=created_after,
        modified_before=modified_before,
        modified_after=modified_after,
        sort_filters=sort_filters,
        page_number=page_number,
        page_size=page_size,
        scope=scope,
    ).try_unique_match()


@merge_properties_from_context
def upload(
    qir: bytes,
    name: str,
    project: ProjectRef | None = None,
    description: str | None = None,
    properties: PropertiesDict | None = None,
) -> QIRRef:
    """Upload a QIR to Nexus."""
    project = project or get_active_project(project_required=True)
    project = cast(ProjectRef, project)

    attributes = {"contents": _encode_qir(qir)}

    annotations = CreateAnnotations(
        name=name,
        description=description,
        properties=properties,
    ).model_dump(exclude_none=True)
    attributes.update(annotations)
    relationships = {"project": {"data": {"id": str(project.id), "type": "project"}}}

    req_dict = {
        "data": {
            "attributes": attributes,
            "relationships": relationships,
            "type": "qir",
        }
    }

    res = get_nexus_client().post("/api/qir/v1beta", json=req_dict)

    if res.status_code != 201:
        raise qnx_exc.ResourceCreateFailed(
            message=res.text, status_code=res.status_code
        )

    res_data_dict = res.json()["data"]

    return QIRRef(
        id=UUID(res_data_dict["id"]),
        annotations=Annotations.from_dict(res_data_dict["attributes"]),
        project=project,
    )


@merge_properties_from_context
def update(
    ref: QIRRef,
    name: str | None = None,
    description: str | None = None,
    properties: PropertiesDict | None = None,
) -> QIRRef:
    """Update the annotations on a QIRRef."""
    ref_annotations = ref.annotations.model_dump()
    annotations = Annotations(
        name=name,
        description=description,
        properties=properties if properties else PropertiesDict(),
    ).model_dump(exclude_none=True)
    ref_annotations.update(annotations)

    req_dict = {
        "data": {
            "attributes": annotations,
            "relationships": {},
            "type": "qir",
        }
    }

    res = get_nexus_client().patch(f"/api/qir/v1beta/{ref.id}", json=req_dict)

    if res.status_code != 200:
        raise qnx_exc.ResourceUpdateFailed(
            message=res.text, status_code=res.status_code
        )

    res_dict = res.json()["data"]

    return QIRRef(
        id=UUID(res_dict["id"]),
        annotations=Annotations.from_dict(res_dict["attributes"]),
        project=ref.project,
    )


def _fetch_by_id(qir_id: UUID | str, scope: ScopeFilterEnum | None) -> QIRRef:
    """Utility method for fetching directly by a unique identifier."""

    params = Params(
        scope=scope,
    ).model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    res = get_nexus_client().get(f"/api/qir/v1beta/{qir_id}", params=params)

    handle_fetch_errors(res)

    res_dict = res.json()

    project_id = res_dict["data"]["relationships"]["project"]["data"]["id"]
    project_details = next(
        proj for proj in res_dict["included"] if proj["id"] == project_id
    )
    project = ProjectRef(
        id=project_id,
        annotations=Annotations.from_dict(project_details["attributes"]),
        contents_modified=project_details["attributes"]["contents_modified"],
        archived=project_details["attributes"]["archived"],
    )

    return QIRRef(
        id=UUID(res_dict["data"]["id"]),
        annotations=Annotations.from_dict(res_dict["data"]["attributes"]),
        project=project,
    )


def _fetch_qir(handle: QIRRef) -> bytes:
    """Utility method for fetching QIR bytes from a QIRRef."""
    res = get_nexus_client().get(f"/api/qir/v1beta/{handle.id}")
    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    contents: str = res.json()["data"]["attributes"]["contents"]
    return _decode_qir(contents)


def _encode_qir(qir: bytes) -> str:
    """Utility method for encoding QIR bytes as base64-encoded string"""
    return base64.b64encode(qir).decode("utf-8")


def _decode_qir(contents: str) -> bytes:
    """Utility method for decoding a base64-encoded string into QIR bytes"""
    return base64.b64decode(contents)
