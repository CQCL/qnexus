from uuid import UUID

from pytket._tket.circuit import Circuit
from typing_extensions import Unpack
from qnexus.annotations import Annotations, AnnotationsDict

from qnexus.client.client import nexus_client
from qnexus.client.models.filters import (
    CreatorFilter,
    CreatorFilterDict,
    NameFilter,
    NameFilterDict,
    PaginationFilter,
    PaginationFilterDict,
    ProjectIDFilter,
    ProjectIDFilterDict,
    PropertiesFilter,
    PropertiesFilterDict,
    SortFilter,
    SortFilterDict,
    TimeFilter,
    TimeFilterDict,
)
from qnexus.client.utils import normalize_included
from qnexus.exceptions import ResourceCreateFailed, ResourceFetchFailed
from qnexus.references import CircuitRef, ProjectRef


class Params(
    SortFilter,
    PaginationFilter,
    NameFilter,
    CreatorFilter,
    ProjectIDFilter,
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
    
):
    """Params for fetching projects (TypedDict)"""

    pass


def circuits(**kwargs: Unpack[ParamsDict]):
    params = Params(**kwargs).model_dump(
        by_alias=True, exclude_unset=True, exclude_none=True
    )

    res = nexus_client.get("/api/circuits/v1beta")

    if res.status_code != 200:
        raise ResourceFetchFailed(message=res.json(), status_code=res.status_code)

    res_dict = res.json()

    included_map = normalize_included(res_dict)


    # circuit_refs = []
    # for circuit_data in res_dict["data"]:
    #     CircuitRef(
    #         id=UUID(circuit_data["id"]), 
    #         annotations=annotations, 
    #         project=ProjectRef(
    #             id=circuit_data["relationships"]["project"]["id"],
    #             annotations=Annotations({})
    #         )
    #     )
    return res_dict




def submit(
    circuit: Circuit, project: ProjectRef, **kwargs: Unpack[AnnotationsDict]
) -> CircuitRef:
    circuit_dict = circuit.to_dict()

    kwargs["name"] = kwargs.get("name", circuit.name)

    annotations = Annotations(**kwargs)
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
    if res.status_code != 200:
        raise ResourceCreateFailed(message=res.json(), status_code=res.status_code)

    res_data_dict = res.json()["data"]

    return CircuitRef(
        id=UUID(res_data_dict["id"]), annotations=annotations, project=project
    )
