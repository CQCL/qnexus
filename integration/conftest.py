"""Pytest fixtures and settings used in the qnexus integration tests."""

from contextlib import contextmanager
from typing import Generator

import pytest
from constants import NEXUS_QA_USER_EMAIL, NEXUS_QA_USER_PASSWORD

import qnexus as qnx
from qnexus import consts


@contextmanager
def make_authenticated_nexus(
    user_email: str = NEXUS_QA_USER_EMAIL,
    user_password: str = NEXUS_QA_USER_PASSWORD,
) -> Generator:
    """Authenticate the qnexus client."""
    consts.STORE_TOKENS = False
    try:
        qnx.auth._request_tokens(  # pylint: disable=protected-access
            user_email, user_password
        )
        yield
    finally:
        qnx.auth.logout()


@pytest.fixture(scope="session")
def _authenticated_nexus() -> Generator[None, None, None]:
    """Authenticated nexus instance fixture."""
    with make_authenticated_nexus():
        yield


@pytest.fixture()
def qa_project_name() -> str:
    """A name for uniquely identifying a project owned by the Nexus QA user."""
    return "qnexus_integration_test_project_with_unique_name_2024-05-23 16:31:34.230595"


@pytest.fixture()
def qa_team_name() -> str:
    """A name for uniquely identifying a team for the Nexus QA user."""
    return "qnexus_integration_test_team_with_unique_name_2024-05-23 16:31:34.230595"


@pytest.fixture()
def qa_circuit_id() -> str:
    """An id for uniquely identifying a circuit owned by the Nexus QA user,
    in the project specified by qa_project_name."""
    return "d3e1ab7c-efdf-4351-ac59-e5d86e9fae6f"


@pytest.fixture()
def qa_compile_job_name() -> str:
    """An id for uniquely identifying a compile job owned by the Nexus QA user,
    in the project specified by qa_project_name."""
    return "QA_compile_2024-05-23 16:46:48.811761"


@pytest.fixture()
def qa_execute_job_name() -> str:
    """An id for uniquely identifying an execute job owned by the Nexus QA user,
    in the project specified by qa_project_name."""
    return "QA_execute_2024-05-23 16:47:52.637954"
