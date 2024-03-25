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
from qnexus.exceptions import (
    ResourceCreateFailed,
    ResourceFetchFailed,
    ResourceUpdateFailed,
)
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


def circuits(**kwargs: Unpack[ParamsDict]) -> list[CircuitRef]:
    params = Params(**kwargs).model_dump(
        by_alias=True, exclude_unset=True, exclude_none=True
    )

    res = nexus_client.get(
        "/api/circuits/v1beta",
        params=params,
    )

    if res.status_code >= 400:
        raise ResourceFetchFailed(message=res.json(), status_code=res.status_code)

    res_dict = res.json()

    # included_map = normalize_included(res_dict)

    circuit_refs = []

    for circuit_data in res_dict["data"]:

        project_id = circuit_data["relationships"]["project"]["data"]["id"]
        project_details = next(
            proj for proj in res_dict["included"] if proj["id"] == project_id
        )
        project_ref = ProjectRef(
            id=project_id,
            annotations=Annotations(
                name=project_details["attributes"]["name"],
                description=project_details["attributes"].get("description", None),
                properties=project_details["attributes"]["properties"],
            ),
        )

        circuit_refs.append(
            CircuitRef(
                id=UUID(circuit_data["id"]),
                annotations=Annotations(
                    name=circuit_data["attributes"]["name"],
                    description=circuit_data["attributes"].get("description", None),
                    properties=circuit_data["attributes"]["properties"],
                ),
                project=project_ref,
            )
        )

    return circuit_refs


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
    if res.status_code >= 400:
        raise ResourceCreateFailed(message=res.json(), status_code=res.status_code)

    res_data_dict = res.json()["data"]

    return CircuitRef(
        id=UUID(res_data_dict["id"]), annotations=annotations, project=project
    )


def update(ref: CircuitRef, **kwargs: Unpack[AnnotationsDict]) -> None:
    """ """
    ref_annotations = ref.annotations.model_dump()
    annotations = Annotations(**kwargs)
    ref_annotations.update(annotations)

    req_dict = {
        "data": {
            "attributes": ref_annotations,
            "relationships": {},  # TODO maybe this needs to be fixed
            "type": "circuit",
        }
    }

    res = nexus_client.patch(f"/api/circuits/v1beta/{ref.id}", json=req_dict)

    if res.status_code >= 400:
        raise ResourceUpdateFailed(message=res.json(), status_code=res.status_code)

    # res_data_dict = res.json()["data"]

    # TODO return updated ref


def _fetch(circuit_id: UUID | str) -> CircuitRef:
    """ """

    res = nexus_client.get(f"/api/circuits/v1beta/{circuit_id}")

    if res.status_code >= 400:
        raise ResourceUpdateFailed(message=res.json(), status_code=res.status_code)

    res_dict = res.json()

    project_id = res_dict["data"]["relationships"]["project"]["data"]["id"]
    project_details = next(
        proj for proj in res_dict["included"] if proj["id"] == project_id
    )
    project_ref = ProjectRef(
        id=project_id,
        annotations=Annotations(
            name=project_details["attributes"]["name"],
            description=project_details["attributes"].get("description", None),
            properties=project_details["attributes"]["properties"],
        ),
    )

    return CircuitRef(
        id=UUID(res_dict["data"]["id"]),
        annotations=Annotations(
            name=res_dict["data"]["attributes"]["name"],
            description=res_dict["data"]["attributes"].get("description", None),
            properties=res_dict["data"]["attributes"]["properties"],
        ),
        project=project_ref,
    )
