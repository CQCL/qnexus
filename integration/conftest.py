"""Pytest fixtures and settings used in the qnexus integration tests."""

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, cast

import pytest
from hugr.package import Package
from pytket.circuit import Circuit
from pytket.qir import pytket_to_qir  # type: ignore[attr-defined]
from pytket.wasm.wasm import WasmFileHandler
from quantinuum_schemas.models.backend_config import BackendConfig

import qnexus as qnx
from qnexus.config import CONFIG
from qnexus.models.references import CircuitRef


@contextmanager
def make_authenticated_nexus(
    user_email: str = CONFIG.qa_user_email,
    user_password: str = CONFIG.qa_user_password,
) -> Generator[None, None, None]:
    """Authenticate the qnexus client."""
    try:
        qnx.auth._request_tokens(user_email, user_password)
        yield
    finally:
        qnx.auth.logout()


@pytest.fixture(scope="session")
def _authenticated_nexus(
    qa_project_name: str,
    qa_circuit_name: str,
    qa_circuit_name_2: str,
    qa_team_name: str,
    qa_compile_job_name: str,
    qa_execute_job_name: str,
    qa_wasm_module_name: str,
    qa_hugr_name: str,
    qa_qir_name: str,
    circuit: Circuit,
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
            programs=[my_other_circuit],
            name=qa_compile_job_name,
            description=test_desc,
            project=my_proj,
            backend_config=qnx.AerConfig(),
            skip_intermediate_circuits=False,
        )

        execute_job_ref = qnx.start_execute_job(
            programs=[my_new_circuit],
            name=qa_execute_job_name,
            description=test_desc,
            project=my_proj,
            backend_config=qnx.AerConfig(),
            n_shots=[10],
        )

        wasm_path = Path("examples/basics/data/add_one.wasm").resolve()
        wfh = WasmFileHandler(filepath=str(wasm_path))

        qnx.wasm_modules.upload(
            wasm_module_handler=wfh,
            name=qa_wasm_module_name,
            project=my_proj,
        )

        hugr_path = Path("integration/data/hugr_example.hugr").resolve()
        hugr_package = Package.from_bytes(hugr_path.read_bytes())

        qnx.hugr.upload(
            hugr_package=hugr_package,
            name=qa_hugr_name,
            project=my_proj,
        )

        qnx.jobs.wait_for(compile_job_ref)
        qnx.jobs.wait_for(execute_job_ref)

        qir_bitcode = pytket_to_qir(circuit, name=qa_qir_name)
        assert isinstance(qir_bitcode, bytes)
        qnx.qir.upload(qir=qir_bitcode, name=qa_qir_name, project=my_proj)

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
    """A name for uniquely identifying a compile job owned by the Nexus QA user,
    in the project specified by qa_project_name."""
    return f"qnexus_integration_test_compile_{datetime.now()}"


@pytest.fixture(scope="session", name="qa_execute_job_name")
def qa_execute_job_name_fixture() -> str:
    """A name for uniquely identifying an execute job owned by the Nexus QA user,
    in the project specified by qa_project_name."""
    return f"qnexus_integration_test_execute_{datetime.now()}"


@pytest.fixture(scope="session", name="qa_wasm_module_name")
def qa_wasm_module_name_fixture() -> str:
    """A name for uniquely identifying a WASM module owned by the Nexus QA user."""
    return f"qnexus_integration_test_wasm_{datetime.now()}"


@pytest.fixture(scope="session", name="qa_hugr_name")
def qa_hugr_name_fixture() -> str:
    """A name for uniquely identifying a HUGR owned by the Nexus QA user."""
    return f"qnexus_integration_test_hugr_{datetime.now()}"


@pytest.fixture(scope="session", name="qa_qir_name")
def qa_qir_name_fixture() -> str:
    """A name for uniquely identifying a QIR owned by the Nexus QA user."""
    return f"qnexus_integration_test_qir_{datetime.now()}"


def get_backend_config_name(backend_config: qnx.BackendConfig) -> str:
    name = backend_config.__class__.__name__
    if hasattr(backend_config, "backend_name"):
        name += f"({backend_config.backend_name})"
    if hasattr(backend_config, "device_name"):
        name += f"({backend_config.device_name})"
    return name


@pytest.fixture(
    scope="session",
    params=[
        # Nexus-hosted
        qnx.AerConfig(),
        qnx.AerStateConfig(),
        qnx.AerUnitaryConfig(),
        qnx.BraketConfig(local=True),
        qnx.QuantinuumConfig(device_name="H1-1LE"),
        qnx.ProjectQConfig(),
        qnx.QulacsConfig(),
        # Non Nexus-hosted
        qnx.IBMQConfig(
            backend_name="ibm_sherbrooke",
            instance=(
                "crn:v1:bluemix:public:quantum-computing:us-east:"
                "a/18f63f4565ef4a40851959792418cbf2:"
                "37bf946a-6349-47df-a092-3fbd5b92dbf2::"
            ),
        ),
        qnx.IBMQEmulatorConfig(
            backend_name="ibm_sherbrooke",
            instance=(
                "crn:v1:bluemix:public:quantum-computing:us-east:"
                "a/18f63f4565ef4a40851959792418cbf2:"
                "37bf946a-6349-47df-a092-3fbd5b92dbf2::"
            ),
        ),
        qnx.QuantinuumConfig(device_name="H1-1SC"),  # Cluster-hosted
    ],
    ids=get_backend_config_name,
)
def backend_config(request: pytest.FixtureRequest) -> BackendConfig:
    """Fixture to provide an instance of all BackendConfigs for testing."""
    return cast(BackendConfig, request.param)


@pytest.fixture(scope="session")
def circuit() -> Circuit:
    """A pytket circuit"""

    circuit = Circuit(3)
    circuit.H(0)
    for i, j in zip(circuit.qubits[:-1], circuit.qubits[1:]):
        circuit.CX(i, j)
    circuit.measure_all()
    return circuit
