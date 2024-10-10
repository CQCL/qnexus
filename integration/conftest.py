"""Pytest fixtures and settings used in the qnexus integration tests."""

from contextlib import contextmanager
from datetime import datetime
from typing import Generator

import pytest
from pytket import Circuit

import qnexus as qnx
from qnexus.config import get_config
from qnexus.models.references import CircuitRef


@contextmanager
def make_authenticated_nexus(
    user_email: str = get_config().qa_user_email,
    user_password: str = get_config().qa_user_password,
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
def _authenticated_nexus(  # pylint: disable=too-many-positional-arguments
    qa_project_name: str,
    qa_circuit_name: str,
    qa_circuit_name_2: str,
    qa_team_name: str,
    qa_compile_job_name: str,
    qa_execute_job_name: str,
) -> Generator[None, None, None]:
    """Authenticated nexus instance fixture."""
    with make_authenticated_nexus():
        test_desc = f"This can be safely deleted. Test Run: {datetime.now()}"

        my_proj = qnx.projects.create(name=qa_project_name, description=test_desc)

        qnx.projects.add_property(
            name="QA_test_prop",
            property_type="string",
            project=my_proj,
        )

        qnx.teams.create(name=qa_team_name, description=test_desc)

        my_new_circuit = qnx.circuits.upload(
            circuit=Circuit(2, 2).H(0).CX(0, 1).measure_all(),
            name=qa_circuit_name,
            description=test_desc,
            project=my_proj,
        )

        my_other_circuit = qnx.circuits.upload(
            # re-uploading with a unique name to avoid conflicts
            circuit=Circuit(2, 2).H(0).CX(0, 1).measure_all(),
            name=qa_circuit_name_2,
            description=test_desc,
            project=my_proj,
        )

        compile_job_ref = qnx.start_compile_job(
            circuits=[my_other_circuit],
            name=qa_compile_job_name,
            description=test_desc,
            project=my_proj,
            backend_config=qnx.AerConfig(),
        )

        execute_job_ref = qnx.start_execute_job(
            circuits=[my_new_circuit],
            name=qa_execute_job_name,
            description=test_desc,
            project=my_proj,
            backend_config=qnx.AerConfig(),
            n_shots=[10],
        )

        qnx.jobs.wait_for(compile_job_ref)
        qnx.jobs.wait_for(execute_job_ref)

        yield

        qnx.projects.update(my_proj, archive=True)
        qnx.projects.delete(my_proj)


@pytest.fixture(scope="session")
def _authenticated_nexus_circuit_ref(
    _authenticated_nexus: None,
    qa_project_name: str,
) -> Generator[CircuitRef, None, None]:
    """Starting with authenticated nexus instance, yield a CircuitRef
    for use in tests."""

    my_proj = qnx.projects.get(name_like=qa_project_name)

    my_new_circuit = qnx.circuits.upload(
        circuit=Circuit(2, 2).H(0).CX(0, 1).measure_all(),
        name=f"qnexus_integration_additional_test_circuit_{datetime.now()}",
        description=f"This can be safely deleted. Test Run: {datetime.now()}",
        project=my_proj,
    )

    yield my_new_circuit


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


@pytest.fixture(scope="session", name="qa_circuit_name_2")
def qa_circuit_name2_fixture() -> str:
    """A name for uniquely identifying a circuit owned by the Nexus QA user,
    in the project specified by qa_project_name."""
    return f"qnexus_integration_test_circuit2_{datetime.now()}"


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
