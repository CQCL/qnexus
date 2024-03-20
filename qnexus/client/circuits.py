from uuid import UUID

from pytket._tket.circuit import Circuit
from typing import Any, cast, Union
from typing_extensions import Unpack
from qnexus.annotations import Annotations, AnnotationsDict, CreateAnnotationsDict, CreateAnnotations

from qnexus.client import nexus_client
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
from qnexus.client.utils import normalize_included
import qnexus.exceptions as qnx_exc
from qnexus.references import CircuitRef, ProjectRef, RefList

from qnexus.client.pagination_iterator import NexusDatabaseIterator

from qnexus.context import merge_project_from_context, get_active_project, get_active_properties, merge_properties_from_context


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
    pass


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

    pass

@merge_project_from_context
def filter(**kwargs: Unpack[ParamsDict]) -> NexusDatabaseIterator:
    """ """

    params = Params(**kwargs).model_dump(
        by_alias=True, exclude_unset=True, exclude_none=True
    )

    return NexusDatabaseIterator(
        resource_type="Circuit",
        nexus_url="/api/circuits/v1beta",
        params=params,
        wrapper_method=_to_CircuitRef
    )


def _to_CircuitRef(page_json: dict[str,Any]) -> RefList[CircuitRef]:
    """ """

    circuit_refs: RefList[CircuitRef] = RefList([])
    
    for circuit_data in page_json["data"]:

        project_id = circuit_data["relationships"]["project"]["data"]["id"]
        project_details = next(proj for proj in page_json["included"] if proj["id"]==project_id)
        project_ref = ProjectRef(
                id=project_id,
                annotations=Annotations(
                    name=project_details["attributes"]["name"],
                    description=project_details["attributes"].get("description", None),
                    properties=project_details["attributes"]["properties"]
                )
        )

        circuit_refs.append(
            CircuitRef(
                id=UUID(circuit_data["id"]), 
                annotations=Annotations(
                    name=circuit_data["attributes"]["name"],
                    description=circuit_data["attributes"].get("description", None),
                    properties=circuit_data["attributes"]["properties"]
                ), 
                project=project_ref
            )
        ) 
    return circuit_refs


def get(id: Union[UUID, str, None] = None, **kwargs: Unpack[ParamsDict]) -> CircuitRef:
    """ """
    if id:
        return _fetch(circuit_id=id)

    filter_call = filter(**kwargs)

    if filter_call.count() > 1:
        raise qnx_exc.NoUniqueMatch()
    if filter_call.count() == 0:
        raise qnx_exc.ZeroMatches()
    return filter_call.all()[0]


@merge_properties_from_context
def create(
    circuit: Circuit, project: ProjectRef | None = None, **kwargs: Unpack[CreateAnnotationsDict]
) -> CircuitRef:
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
        raise qnx_exc.ResourceCreateFailed(message=res.json(), status_code=res.status_code)

    res_data_dict = res.json()["data"]

    return CircuitRef(
        id=UUID(res_data_dict["id"]), annotations=annotations, project=project
    )

@merge_properties_from_context
def update(ref: CircuitRef, **kwargs: Unpack[AnnotationsDict]) -> None:
    """ """
    ref_annotations = ref.annotations.model_dump()
    annotations = Annotations(**kwargs).model_dump(exclude_none=True)
    ref_annotations.update(annotations)

    req_dict = {
        "data": {
            "attributes": ref_annotations,
            "relationships": {}, # TODO maybe this needs to be fixed
            "type": "circuit",
        }
    }
    
    res = nexus_client.patch(f"/api/circuits/v1beta/{ref.id}", json=req_dict)

    if res.status_code != 200:
        raise qnx_exc.ResourceUpdateFailed(message=res.json(), status_code=res.status_code)

    #res_data_dict = res.json()["data"]

    # TODO return updated ref



def _fetch(circuit_id: UUID | str) -> CircuitRef:
    """ """

    res = nexus_client.get(f"/api/circuits/v1beta/{circuit_id}")

    if res.status_code == 404:
        raise qnx_exc.ZeroMatches()

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.json(), status_code=res.status_code)

    res_dict = res.json()

    project_id = res_dict["data"]["relationships"]["project"]["data"]["id"]
    project_details = next(proj for proj in res_dict["included"] if proj["id"]==project_id)
    project_ref = ProjectRef(
            id=project_id,
            annotations=Annotations(
                name=project_details["attributes"]["name"],
                description=project_details["attributes"].get("description", None),
                properties=project_details["attributes"]["properties"]
            )
    )

    return CircuitRef(
            id=UUID(res_dict["data"]["id"]), 
            annotations=Annotations(
                name=res_dict["data"]["attributes"]["name"],
                description=res_dict["data"]["attributes"].get("description", None),
                properties=res_dict["data"]["attributes"]["properties"]
            ), 
            project=project_ref
        )



def _fetch_circuit(handle: CircuitRef) -> Circuit:
    res = nexus_client.get(f"/api/circuits/v1beta/{handle.id}")
    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.json(), status_code=res.status_code)

    res_data_attributes_dict = res.json()["data"]["attributes"]
    circuit_dict = {k: v for k, v in res_data_attributes_dict.items() if v is not None}

    return Circuit.from_dict(circuit_dict)