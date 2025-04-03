"""Basic checks for API query filters."""

from datetime import datetime
from uuid import uuid4

from qnexus.models.annotations import Annotations, PropertiesDict
from qnexus.models.filters import (
    ArchivedFilter,
    CreatorFilter,
    CredentialsFilter,
    DevicesFilter,
    FuzzyNameFilter,
    JobStatusEnum,
    JobStatusFilter,
    JobTypeFilter,
    PaginationFilter,
    ProjectRefFilter,
    PropertiesFilter,
    ScopeFilter,
    ScopeFilterEnum,
    SortFilter,
    SortFilterEnum,
    TimeFilter,
)
from qnexus.models.references import JobType, ProjectRef


def test_all_filter_serialisation() -> None:
    """Test all supported filters and their serialisation."""

    class Params(
        ArchivedFilter,
        CreatorFilter,
        CredentialsFilter,
        DevicesFilter,
        FuzzyNameFilter,
        JobStatusFilter,
        JobTypeFilter,
        PaginationFilter,
        ProjectRefFilter,
        PropertiesFilter,
        ScopeFilter,
        SortFilter,
        TimeFilter,
    ):
        """Test filters class."""

    dummy_project_ref = ProjectRef(
        id=uuid4(), annotations=Annotations(), contents_modified=datetime.now()
    )

    # Mix between strings and enums, both should be supported
    job_status = [JobStatusEnum.COMPLETED, "CANCELLED"]
    job_type = [JobType.EXECUTE, "compile"]
    sort_filters = [SortFilterEnum.CREATED_DESC, "-modified"]
    test_datetime = datetime.now()

    params = Params(
        name_like="test_name",
        creator_email=["test@email.com"],
        project=dummy_project_ref,
        status=(
            JobStatusFilter.convert_status_filters(job_status)  # type: ignore
            if job_status
            else None
        ),
        job_type=job_type,
        properties=PropertiesDict({"hello": 1, "goodbye": False, "how": "yes"}),
        created_before=test_datetime,
        created_after=test_datetime,
        modified_before=test_datetime,
        modified_after=test_datetime,
        sort=SortFilter.convert_sort_filters(sort_filters),  # type: ignore
        page_number=1,
        page_size=100,
        scope=ScopeFilterEnum.ORG_ADMIN,
    ).model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    assert params["filter[name]"] == "test_name"
    assert params["filter[creator][email]"] == ["test@email.com"]
    assert params["filter[project][id]"] == str(dummy_project_ref.id)
    assert sorted(params["filter[properties]"]) == sorted(
        ["(hello,1)", "(goodbye,false)", '(how,"yes")']
    )
    assert sorted(params["filter[status][status]"]) == sorted(
        ["COMPLETED", "CANCELLED"]
    )
    assert sorted(params["filter[job_type]"]) == sorted(["execute", "compile"])
    assert params["filter[timestamps][created][before]"] == test_datetime
    assert params["filter[timestamps][created][after]"] == test_datetime
    assert params["filter[timestamps][modified][before]"] == test_datetime
    assert params["filter[timestamps][modified][after]"] == test_datetime
    assert sorted(params["sort"]) == sorted(
        ["-timestamps.created", "-timestamps.modified"]
    )
    assert params["page[number]"] == 1
    assert params["page[size]"] == 100
    assert params["scope"] == "org_admin"
