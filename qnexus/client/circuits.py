"""Client API for circuits in Nexus."""

from datetime import datetime
from typing import Any, Union, cast
from uuid import UUID

from httpx import QueryParams
from pytket.circuit import Circuit
from pytket.utils.serialization.migration import circuit_dict_from_pytket1_dict
from quantinuum_schemas.models.backend_config import BackendConfig, QuantinuumConfig

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
from qnexus.models.references import CircuitRef, DataframableList, ProjectRef


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
    """Params for filtering circuits."""


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
) -> NexusIterator[CircuitRef]:
    """Get a NexusIterator over circuits with optional filters."""

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
        resource_type="Circuit",
        nexus_url="/api/circuits/v1beta",
        params=params,
        wrapper_method=_to_circuitref,
        nexus_client=get_nexus_client(),
    )


def _to_circuitref(page_json: dict[str, Any]) -> DataframableList[CircuitRef]:
    """Convert JSON response dict to a list of CircuitRefs."""

    circuit_refs: DataframableList[CircuitRef] = DataframableList([])

    for circuit_data in page_json["data"]:
        project_id = circuit_data["relationships"]["project"]["data"]["id"]
        project_details = next(
            proj for proj in page_json["included"] if proj["id"] == project_id
        )
        project = ProjectRef(
            id=project_id,
            annotations=Annotations.from_dict(project_details["attributes"]),
            contents_modified=project_details["attributes"]["contents_modified"],
            archived=project_details["attributes"]["archived"],
        )

        circuit_refs.append(
            CircuitRef(
                id=UUID(circuit_data["id"]),
                annotations=Annotations.from_dict(circuit_data["attributes"]),
                project=project,
            )
        )
    return circuit_refs


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
) -> CircuitRef:
    """
    Get a single circuit using filters. Throws an exception if the filters do
    not match exactly one object.
    """
    if id:
        return _fetch_by_id(circuit_id=id, scope=scope)

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
    circuit: Circuit,
    project: ProjectRef | None = None,
    name: str | None = None,
    description: str | None = None,
    properties: PropertiesDict | None = None,
) -> CircuitRef:
    """Upload a pytket Circuit to Nexus."""
    project = project or get_active_project(project_required=True)
    project = cast(ProjectRef, project)

    circuit_dict = circuit.to_dict()
    circuit_name = name if name else circuit.name
    if circuit_name is None:
        raise ValueError("Circuit must have a name to be uploaded")

    annotations = CreateAnnotations(
        name=circuit_name,
        description=description,
        properties=properties,
    ).model_dump(exclude_none=True)
    circuit_dict.update(annotations)
    relationships = {"project": {"data": {"id": str(project.id), "type": "project"}}}

    req_dict = {
        "data": {
            "attributes": circuit_dict,
            "relationships": relationships,
            "type": "circuit",
        }
    }

    res = get_nexus_client().post("/api/circuits/v1beta", json=req_dict)

    # https://cqc.atlassian.net/browse/MUS-3054
    if res.status_code != 201:
        raise qnx_exc.ResourceCreateFailed(
            message=res.text, status_code=res.status_code
        )

    res_data_dict = res.json()["data"]

    return CircuitRef(
        id=UUID(res_data_dict["id"]),
        annotations=Annotations.from_dict(res_data_dict["attributes"]),
        project=project,
    )


@merge_properties_from_context
def update(
    ref: CircuitRef,
    name: str | None = None,
    description: str | None = None,
    properties: PropertiesDict | None = None,
) -> CircuitRef:
    """Update the annotations on a CircuitRef."""
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
            "type": "circuit",
        }
    }

    res = get_nexus_client().patch(f"/api/circuits/v1beta/{ref.id}", json=req_dict)

    if res.status_code != 200:
        raise qnx_exc.ResourceUpdateFailed(
            message=res.text, status_code=res.status_code
        )

    res_dict = res.json()["data"]

    return CircuitRef(
        id=UUID(res_dict["id"]),
        annotations=Annotations.from_dict(res_dict["attributes"]),
        project=ref.project,
    )


def _fetch_by_id(circuit_id: UUID | str, scope: ScopeFilterEnum | None) -> CircuitRef:
    """Utility method for fetching directly by a unique identifier."""
    params = Params(
        scope=scope,
    ).model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    res = get_nexus_client().get(f"/api/circuits/v1beta/{circuit_id}", params=params)

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

    return CircuitRef(
        id=UUID(res_dict["data"]["id"]),
        annotations=Annotations.from_dict(res_dict["data"]["attributes"]),
        project=project,
    )


def _fetch_circuit(handle: CircuitRef) -> Circuit:
    """Utility method for fetching a pytket circuit from a CircuitRef."""
    res = get_nexus_client().get(f"/api/circuits/v1beta/{handle.id}")
    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    res_data_attributes_dict = res.json()["data"]["attributes"]
    circuit_dict = {k: v for k, v in res_data_attributes_dict.items() if v is not None}

    return Circuit.from_dict(circuit_dict_from_pytket1_dict(circuit_dict))


def cost(
    circuit_ref: CircuitRef,
    n_shots: int,
    backend_config: BackendConfig,
    syntax_checker: str | None = None,
) -> float | None:
    """Calculate the cost (in HQC) of running a circuit for n_shots
    number of shots on a specific Quantinuum device."""

    if not isinstance(backend_config, QuantinuumConfig):
        raise ValueError("QuantinuumConfig is the only supported backend config")

    params = {
        "n_shots": n_shots,
        "device_name": backend_config.device_name,
    }
    if syntax_checker:
        params["syntax_checker"] = syntax_checker

    res = get_nexus_client().get(
        f"/api/circuits/v1beta/cost/{circuit_ref.id}",
        params=cast(QueryParams, params),
    )

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    circuit_cost: float | None = res.json()
    return circuit_cost
