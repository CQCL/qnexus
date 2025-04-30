"""Client API for HUGR in Nexus.

N.B. Nexus support for HUGR is experimental, and any HUGRs programs
uploaded to Nexus before stability is achieved might not work in the future.
"""

import base64
from datetime import datetime
from typing import Any, Union, cast
from uuid import UUID

from hugr.envelope import EnvelopeConfig, EnvelopeFormat
from hugr.package import Package

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
from qnexus.models.references import DataframableList, HUGRRef, ProjectRef


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
    """Params for filtering HUGRs."""


# We can change the format and zstd when HUGR supports more options. Since the
# header in the envelope encodes the config, Package.from_bytes will work
# without changes. We expect HUGR team to make other formats available in 2025.
ENVELOPE_CONFIG = EnvelopeConfig(
    # As of hugr v0.11.3, the only format available is JSON
    format=EnvelopeFormat.JSON,
    zstd=0,
)


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
) -> NexusIterator[HUGRRef]:
    """Get a NexusIterator over HUGRs with optional filters."""

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
        resource_type="HUGR",
        nexus_url="/api/hugr/v1beta",
        params=params,
        wrapper_method=_to_hugr_ref,
        nexus_client=get_nexus_client(),
    )


def _to_hugr_ref(page_json: dict[str, Any]) -> DataframableList[HUGRRef]:
    """Convert JSON response dict to a list of HUGRRefs."""

    hugr_refs: DataframableList[HUGRRef] = DataframableList([])

    for hugr_data in page_json["data"]:
        project_id = hugr_data["relationships"]["project"]["data"]["id"]
        project_details = next(
            proj for proj in page_json["included"] if proj["id"] == project_id
        )
        project = ProjectRef(
            id=project_id,
            annotations=Annotations.from_dict(project_details["attributes"]),
            contents_modified=project_details["attributes"]["contents_modified"],
            archived=project_details["attributes"]["archived"],
        )

        hugr_refs.append(
            HUGRRef(
                id=UUID(hugr_data["id"]),
                annotations=Annotations.from_dict(hugr_data["attributes"]),
                project=project,
            )
        )
    return hugr_refs


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
) -> HUGRRef:
    """
    Get a single HUGR using filters. Throws an exception if the filters do
    not match exactly one object.
    """

    if id:
        return _fetch_by_id(hugr_id=id, scope=scope)

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
    hugr_package: Package,
    name: str,
    project: ProjectRef | None = None,
    description: str | None = None,
    properties: PropertiesDict | None = None,
) -> HUGRRef:
    """Upload a HUGR to Nexus.

    N.B. HUGR support in Nexus is subject to change. Until full support is achieved any
    programs uploaded may not work in the future.
    """
    project = project or get_active_project(project_required=True)
    project = cast(ProjectRef, project)

    attributes = {"contents": _encode_hugr(hugr_package)}

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
            "type": "hugr",
        }
    }

    res = get_nexus_client().post("/api/hugr/v1beta", json=req_dict)

    if res.status_code != 201:
        raise qnx_exc.ResourceCreateFailed(
            message=res.text, status_code=res.status_code
        )

    res_data_dict = res.json()["data"]

    return HUGRRef(
        id=UUID(res_data_dict["id"]),
        annotations=Annotations.from_dict(res_data_dict["attributes"]),
        project=project,
    )


@merge_properties_from_context
def update(
    ref: HUGRRef,
    name: str | None = None,
    description: str | None = None,
    properties: PropertiesDict | None = None,
) -> HUGRRef:
    """Update the annotations on a HUGRRef."""
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
            "type": "hugr",
        }
    }

    res = get_nexus_client().patch(f"/api/hugr/v1beta/{ref.id}", json=req_dict)

    if res.status_code != 200:
        raise qnx_exc.ResourceUpdateFailed(
            message=res.text, status_code=res.status_code
        )

    res_dict = res.json()["data"]

    return HUGRRef(
        id=UUID(res_dict["id"]),
        annotations=Annotations.from_dict(res_dict["attributes"]),
        project=ref.project,
    )


def _fetch_by_id(hugr_id: UUID | str, scope: ScopeFilterEnum | None) -> HUGRRef:
    """Utility method for fetching directly by a unique identifier."""

    params = Params(
        scope=scope,
    ).model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    res = get_nexus_client().get(f"/api/hugr/v1beta/{hugr_id}", params=params)

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

    return HUGRRef(
        id=UUID(res_dict["data"]["id"]),
        annotations=Annotations.from_dict(res_dict["data"]["attributes"]),
        project=project,
    )


def _fetch_hugr_package(handle: HUGRRef) -> Package:
    """Utility method for fetching a HUGR Package from a HUGRRef."""
    res = get_nexus_client().get(f"/api/hugr/v1beta/{handle.id}")
    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    contents: str = res.json()["data"]["attributes"]["contents"]
    return _decode_hugr(contents)


def _encode_hugr(hugr_package: Package) -> str:
    """Utility method for encoding a HUGR Package as base64-encoded string"""
    return base64.b64encode(
        hugr_package.to_bytes(
            config=ENVELOPE_CONFIG,
        )
    ).decode("utf-8")


def _decode_hugr(contents: str) -> Package:
    """Utility method for decoding a base64-encoded string into a HUGR Package"""
    hugr_envelope = base64.b64decode(contents)
    return Package.from_bytes(envelope=hugr_envelope)
