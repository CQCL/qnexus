"""Pytest fixtures and settings used in the qnexus integration tests."""

from contextlib import contextmanager
from datetime import datetime
from typing import Generator

import pytest
from constants import NEXUS_QA_USER_EMAIL, NEXUS_QA_USER_PASSWORD
from pytket import Circuit

import qnexus as qnx


@contextmanager
def make_authenticated_nexus(
    user_email: str = NEXUS_QA_USER_EMAIL,
    user_password: str = NEXUS_QA_USER_PASSWORD,
) -> Generator:
    """Authenticate the qnexus client."""
    try:
        qnx.auth._request_tokens(  # pylint: disable=protected-access
            user_email, user_password
        )
        yield
    finally:
        qnx.auth.logout()


@pytest.fixture(scope="session")
def _authenticated_nexus(
    qa_project_name: str,
    qa_circuit_name: str,
    qa_team_name: str,
    qa_compile_job_name: str,
    qa_execute_job_name: str,
) -> Generator[None, None, None]:
    """Authenticated nexus instance fixture."""
    with make_authenticated_nexus():
        test_desc = f"This can be safely deleted. Test Run: {datetime.now()}"

        my_proj = qnx.project.create(name=qa_project_name, description=test_desc)

        qnx.project.add_property(
            name="QA_test_prop",
            property_type="string",
            project_ref=my_proj,
        )

        qnx.team.create(name=qa_team_name, description=test_desc)

        my_new_circuit = qnx.circuit.upload(
            circuit=Circuit(2, 2).H(0).CX(0, 1).measure_all(),
            name=qa_circuit_name,
            description=test_desc,
            project=my_proj,
        )

        my_new_circuit_2 = qnx.circuit.upload(
            # The API only supports fuzzy name matching
            # which might cause conflicts as the compilation creates
            # additional circuits with the same substring in the name
            circuit=Circuit(2, 2).H(0).CX(0, 1).measure_all(),
            name=f"qnexus_integration_test_compile_circuit_{datetime.now()}",
            description=test_desc,
            project=my_proj,
        )

        qnx.compile(
            circuits=[my_new_circuit_2],
            name=qa_compile_job_name,
            description=test_desc,
            project=my_proj,
            target=qnx.AerConfig(),
        )

        qnx.execute(
            circuits=[my_new_circuit],
            name=qa_execute_job_name,
            description=test_desc,
            project=my_proj,
            target=qnx.AerConfig(),
            n_shots=[10],
        )

        yield


@pytest.fixture(scope="session", name="qa_project_name")
def qa_project_name_fixture() -> str:
    """A name for uniquely identifying a project owned by the Nexus QA user."""
    return f"qnexus_integration_test_project_{datetime.now()}"


@pytest.fixture(scope="session", name="qa_team_name")
def qa_team_name_fixture() -> str:
    """A name for uniquely identifying a team for the Nexus QA user."""
    return f"qnexus_integration_test_team_{datetime.now()}"


@pytest.fixture(scope="session", name="qa_circuit_name")
def qa_circuit_name_fixture() -> str:
    """A name for uniquely identifying a circuit owned by the Nexus QA user,
    in the project specified by qa_project_name."""
    return f"qnexus_integration_test_circuit_{datetime.now()}"


@pytest.fixture(scope="session", name="qa_compile_job_name")
def qa_compile_job_name_fixture() -> str:
    """An id for uniquely identifying a compile job owned by the Nexus QA user,
    in the project specified by qa_project_name."""
    return f"qnexus_integration_test_compile_{datetime.now()}"


@pytest.fixture(scope="session", name="qa_execute_job_name")
def qa_execute_job_name_fixture() -> str:
    """An id for uniquely identifying an execute job owned by the Nexus QA user,
    in the project specified by qa_project_name."""
    return f"qnexus_integration_test_execute_{datetime.now()}"
