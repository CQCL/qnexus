"""Client API for compilation passes in Nexus."""

# pylint: disable=redefined-builtin
from datetime import datetime
from typing import Any, Union, cast
from uuid import UUID

from qnexus.client import get_nexus_client
from qnexus.models.annotations import PropertiesDict, Annotations
from qnexus.client.nexus_iterator import NexusIterator
from qnexus.models.references import (
    CompilationRef,
    ProjectRef,
    CircuitRef,
    DataframableList
)
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
    DevicesFilter
)
from qnexus.client.circuits import _fetch_by_id
from qnexus.context import (
    get_active_project,
    merge_project_from_context,
    merge_properties_from_context,
)


class Params(
    SortFilter,
    PaginationFilter,
    FuzzyNameFilter,
    CreatorFilter,
    ProjectRefFilter,
    PropertiesFilter,
    TimeFilter,
    ScopeFilter,
    DevicesFilter
):
    """Params for filtering circuits."""


@merge_project_from_context
def get_all(  # pylint: disable=too-many-positional-arguments
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
) -> NexusIterator[CompilationRef]:
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
        resource_type="Compilation",
        nexus_url="/api/compilations/v1beta",
        params=params,
        wrapper_method=_to_compilationref,
        nexus_client=get_nexus_client(),
    )


def _to_compilationref(page_json: dict[str, Any]) -> DataframableList[CompilationRef]:
    """Convert JSON response dict to a list of CompilationRefs."""

    compilation_refs: DataframableList[CompilationRef] = DataframableList([])

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

        # original_circuit = circuit_data["relationships"]["original_circuit"]
        # input_circuit = _fetch_by_id(
        #     circuit_id=UUID(original_circuit["data"]["id"]),
        #     scope=None
        # )
        # compiled_circuit = circuit_data["relationships"]["compiled_circuit"]
        # output_circuit = _fetch_by_id(
        #     circuit_id=UUID(compiled_circuit["data"]["id"]),
        #     scope=None
        # )

        compilation_refs.append(
            CompilationRef(
                id=UUID(circuit_data["id"]),
                project=project,
                annotations=Annotations.from_dict(circuit_data["attributes"])
            )
        )
    return compilation_refs


def get(  # pylint: disable=too-many-positional-arguments
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
) -> NexusIterator[CompilationRef]: