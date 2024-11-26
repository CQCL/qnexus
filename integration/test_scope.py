"""Test basic functionality relating to setting 'scope' for API requests."""

import qnexus as qnx
from qnexus.models.filters import ScopeFilterEnum


def test_user_scope(
    _authenticated_nexus: None,
) -> None:
    """Test that we can add a scope filter to our queries,
    but that this is ignored when the user claims to be an
    org_admin or global_admin."""

    all_my_user_projects = qnx.projects.get_all(scope=ScopeFilterEnum.USER)

    assert all_my_user_projects.count() > 1

    all_org_admin_projects = qnx.projects.get_all(scope=ScopeFilterEnum.ORG_ADMIN)

    assert all_org_admin_projects.count() == 0

    all_global_admin_projects = qnx.projects.get_all(scope=ScopeFilterEnum.GLOBAL_ADMIN)

    assert all_global_admin_projects.count() == 0

    all_highest_scope_projects = qnx.projects.get_all(scope=ScopeFilterEnum.HIGHEST)

    assert all_highest_scope_projects.count() == all_my_user_projects.count()
