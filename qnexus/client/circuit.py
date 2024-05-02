"""Client API for circuits in Nexus."""
# pylint: disable=redefined-builtin
from typing import Any, Union, cast
from uuid import UUID

from pytket import Circuit
from typing_extensions import Unpack

import qnexus.exceptions as qnx_exc
from qnexus.client import nexus_client
from qnexus.client.database_iterator import DatabaseIterator
from qnexus.client.models.annotations import (
    Annotations,
    AnnotationsDict,
    CreateAnnotations,
    CreateAnnotationsDict,
)
from qnexus.client.models.filters import (
    CreatorFilter,
    CreatorFilterDict,
    NameFilter,
    NameFilterDict,
    PaginationFilter,
    PaginationFilterDict,
    ProjectIDFilter,
    ProjectIDFilterDict,
    ProjectRefFilter,
    ProjectRefFilterDict,
    PropertiesFilter,
    PropertiesFilterDict,
    SortFilter,
    SortFilterDict,
    TimeFilter,
    TimeFilterDict,
)
from qnexus.client.utils import handle_fetch_errors
from qnexus.context import (
    get_active_project,
    merge_project_from_context,
    merge_properties_from_context,
)
from qnexus.references import CircuitRef, DataframableList, ProjectRef


class Params(
    SortFilter,
    PaginationFilter,
    NameFilter,
    CreatorFilter,
    ProjectIDFilter,
    ProjectRefFilter,
    PropertiesFilter,
    TimeFilter,
):
    """Params for filtering circuits."""


class ParamsDict(
    PaginationFilterDict,
    NameFilterDict,
    CreatorFilterDict,
    PropertiesFilterDict,
    TimeFilterDict,
    SortFilterDict,
    ProjectIDFilterDict,
    ProjectRefFilterDict,
):
    """Params for fetching projects (TypedDict)"""


@merge_project_from_context
def get(**kwargs: Unpack[ParamsDict]) -> DatabaseIterator:
    """Get a DatabaseIterator over circuits with optional filters."""

    params = Params(**kwargs).model_dump(
        by_alias=True, exclude_unset=True, exclude_none=True
    )

    return DatabaseIterator(
        resource_type="Circuit",
        nexus_url="/api/circuits/v1beta",
        params=params,
        wrapper_method=_to_circuitref,
        nexus_client=nexus_client,
    )


def _to_circuitref(page_json: dict[str, Any]) -> DataframableList[CircuitRef]:
    """ """

    circuit_refs: DataframableList[CircuitRef] = DataframableList([])

    for circuit_data in page_json["data"]:
        project_id = circuit_data["relationships"]["project"]["data"]["id"]
        project_details = next(
            proj for proj in page_json["included"] if proj["id"] == project_id
        )
        project_ref = ProjectRef(
            id=project_id,
            annotations=Annotations.from_dict(project_details["attributes"]),
        )

        circuit_refs.append(
            CircuitRef(
                id=UUID(circuit_data["id"]),
                annotations=Annotations.from_dict(circuit_data["attributes"]),
                project=project_ref,
            )
        )
    return circuit_refs


def get_only(
    id: Union[UUID, str, None] = None, **kwargs: Unpack[ParamsDict]
) -> CircuitRef:
    """Attempt to get an exact match on a circuit by using filters
    that uniquely identify one."""
    if id:
        return _fetch(circuit_id=id)

    return get(**kwargs).try_unique_match()


@merge_properties_from_context
def upload(
    circuit: Circuit,
    project: ProjectRef | None = None,
    **kwargs: Unpack[CreateAnnotationsDict],
) -> CircuitRef:
    """Upload a pytket Circuit to Nexus."""
    project = project or get_active_project(project_required=True)
    project = cast(ProjectRef, project)

    circuit_dict = circuit.to_dict()
    kwargs["name"] = kwargs.get("name", circuit.name)

    annotations = CreateAnnotations(**kwargs).model_dump(exclude_none=True)
    circuit_dict.update(annotations)
    relationships = {"project": {"data": {"id": str(project.id), "type": "project"}}}

    req_dict = {
        "data": {
            "attributes": circuit_dict,
            "relationships": relationships,
            "type": "circuit",
        }
    }

    res = nexus_client.post("/api/circuits/v1beta", json=req_dict)

    # https://cqc.atlassian.net/browse/MUS-3054
    if res.status_code != 201:
        raise qnx_exc.ResourceCreateFailed(
            message=res.json(), status_code=res.status_code
        )

    res_data_dict = res.json()["data"]

    return CircuitRef(
        id=UUID(res_data_dict["id"]), annotations=annotations, project=project
    )


@merge_properties_from_context
def update(ref: CircuitRef, **kwargs: Unpack[AnnotationsDict]) -> None:
    """Update the annotations on a CircuitRef."""
    ref_annotations = ref.annotations.model_dump()
    annotations = Annotations(**kwargs).model_dump(exclude_none=True)
    ref_annotations.update(annotations)

    req_dict = {
        "data": {
            "attributes": ref_annotations,
            "relationships": {},  # TODO maybe this needs to be fixed
            "type": "circuit",
        }
    }

    res = nexus_client.patch(f"/api/circuits/v1beta/{ref.id}", json=req_dict)

    if res.status_code != 200:
        raise qnx_exc.ResourceUpdateFailed(
            message=res.json(), status_code=res.status_code
        )

    # res_data_dict = res.json()["data"]

    # TODO return updated ref


def _fetch(circuit_id: UUID | str) -> CircuitRef:
    """Utility method for fetching directly by a unique identifier."""

    res = nexus_client.get(f"/api/circuits/v1beta/{circuit_id}")

    handle_fetch_errors(res)

    res_dict = res.json()

    project_id = res_dict["data"]["relationships"]["project"]["data"]["id"]
    project_details = next(
        proj for proj in res_dict["included"] if proj["id"] == project_id
    )
    project_ref = ProjectRef(
        id=project_id,
        annotations=Annotations.from_dict(project_details["attributes"]),
    )

    return CircuitRef(
        id=UUID(res_dict["data"]["id"]),
        annotations=Annotations.from_dict(res_dict["data"]["attributes"]),
        project=project_ref,
    )


def _fetch_circuit(handle: CircuitRef) -> Circuit:
    """Utility method for fetching a pytket circuit from a CircuitRef."""
    res = nexus_client.get(f"/api/circuits/v1beta/{handle.id}")
    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(
            message=res.json(), status_code=res.status_code
        )

    res_data_attributes_dict = res.json()["data"]["attributes"]
    circuit_dict = {k: v for k, v in res_data_attributes_dict.items() if v is not None}

    return Circuit.from_dict(circuit_dict)
