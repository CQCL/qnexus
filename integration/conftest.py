"""Pytest fixtures and settings used in the qnexus integration tests."""

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Callable, Generator, Literal, cast
import pandas as pd

import pytest
from hugr.package import Package
from pytket.circuit import Circuit
from pytket.qir import pytket_to_qir  # type: ignore[attr-defined]
from pytket.wasm.wasm import WasmFileHandler, WasmModuleHandler
from quantinuum_schemas.models.backend_config import BackendConfig, BaseBackendConfig

import qnexus as qnx
from qnexus.client.auth import login_no_interaction
from qnexus.config import CONFIG
from qnexus.exceptions import NoUniqueMatch, ZeroMatches
from qnexus.models.references import (
    CircuitRef,
    CompileJobRef,
    ExecuteJobRef,
    HUGRRef,
    ProjectRef,
    TeamRef,
    WasmModuleRef,
)


test_run_identifier = ""


def pytest_addoption(parser):
    parser.addoption(
        "--purge-projects",
        action="store_true",
        default=False,
        help="Purge the projects created by the tests.",
    )

    parser.addoption(
        "--run-id",
        action="store",
        default="",
        help="Use this to identify resources created by the tests. If not provided the `testrun_uid` from pytest-xdist is used.",
    )


@pytest.fixture(autouse=True)
def set_test_run_identifier(request: pytest.FixtureRequest, testrun_uid: str) -> None:
    global test_run_identifier

    run_id_option = request.config.getoption("--run-id")
    test_run_identifier = run_id_option if run_id_option else testrun_uid


@pytest.fixture(name="test_case_name")
def fixture_test_case_name(request: pytest.FixtureRequest) -> str:
    test_case_name = f"{request.node.module.__name__}::{request.node.name}"
    return f"qnexus.{test_case_name}, run:{request.node.execution_count}, id:{test_run_identifier}"


@pytest.fixture(name="test_suite_name")
def fixture_test_suite_name(request: pytest.FixtureRequest) -> str:
    test_suite_name = f"{request.node.module.__name__}"
    return f"qnexus.{test_suite_name}, run:{request.node.execution_count}, id:{test_run_identifier}"


@pytest.fixture(scope="session", autouse=True)
def authenticated_nexus(
    user_email: str = CONFIG.qa_user_email,
    user_password: str = CONFIG.qa_user_password,
) -> Generator[None, None, None]:
    """Authenticated nexus instance fixture."""
    try:
        login_no_interaction(user_email, user_password)
        yield
    finally:
        qnx.auth.logout()


@contextmanager
def make_authenticated_nexus(
    user_email: str = CONFIG.qa_user_email,
    user_password: str = CONFIG.qa_user_password,
) -> Generator[None, None, None]:
    """Authenticate the qnexus client."""
    try:
        login_no_interaction(user_email, user_password)
        # qnx.auth._request_tokens(user_email, user_password)
        yield
    finally:
        qnx.auth.logout()


@pytest.fixture(name="create_team")
def fixture_create_team() -> Callable:
    """Returns a `contextmanager` that yields a `TeamRef`
    of an existing/created project with the specified name."""

    @contextmanager
    def make_team_if_needed(
        team_name: str,
    ) -> Generator[TeamRef, None, None]:
        team_ref = None
        try:
            team_ref = qnx.teams.get(team_name)
        except ZeroMatches:
            team_ref = qnx.teams.create(
                name=team_name, description=f"description for {team_name}"
            )
        except Exception as e:
            raise e

        yield team_ref

    return make_team_if_needed


@pytest.fixture(name="create_project")
def fixture_create_project(request) -> Callable:
    """Returns a `contextmanager` that yields a project created
    with the specified name."""

    @contextmanager
    def make_temp_project(
        project_name: str,
    ) -> Generator[ProjectRef, None, None]:
        my_proj = qnx.projects.get_or_create(
            name=project_name, description=f"description for {project_name}"
        )
        yield my_proj

        if request.config.getoption("--purge-projects"):
            qnx.projects.update(my_proj, archive=True)
            qnx.projects.delete(my_proj)

    return make_temp_project


@pytest.fixture(name="create_circuit_in_project")
def fixture_create_circuit_in_project(authenticated_nexus: None) -> Callable:
    """Returns a `contextmanager` that yields a `circuit_ref` of the
    specified `circuit` uploaded to a project with `project_name`."""

    @contextmanager
    def upload_circuit_if_needed(
        circuit: Circuit,
        project_name: str,
        circuit_name: str,
    ) -> Generator[CircuitRef, None, None]:
        circuit_ref = _get_or_create_circuit(
            circuit=circuit, project_name=project_name, circuit_name=circuit_name
        )

        yield circuit_ref

    return upload_circuit_if_needed


@pytest.fixture(name="create_compile_job_in_project")
def fixture_create_compile_job_in_project(
    create_circuit_in_project: Callable,
) -> Callable:
    """Returns a `contextmanager` that yields a `CompileJobRef` of the
    compile job submitted with the specified `CircuitRef` to the project
    with the provided name.

    Notes:
        - The default backend_config is `qnx.AerConfig()`
        - By default `skip_intermediate_circuits` is False

    Warning:
        - Will create the project and upload the circuit if needed.
        - Will not wait for the job to finish before yielding."""

    @contextmanager
    def make_compile_job(
        project_name: str,
        job_name: str,
        circuit: Circuit,
        circuit_name: str,
        backend_config: BaseBackendConfig | None = None,
        skip_intermediate_circuits: bool = False,
    ) -> Generator[CompileJobRef, None, None]:
        with create_circuit_in_project(
            circuit,
            project_name,
            circuit_name,
        ) as circuit_ref:

            config = backend_config if backend_config is not None else qnx.AerConfig()

            try:
                compile_job_ref = qnx.jobs.get(name_like=job_name)
            except ZeroMatches:

                proj_ref = qnx.projects.get(name_like=project_name)

                compile_job_ref = qnx.start_compile_job(
                    programs=[circuit_ref],
                    name=job_name,
                    description=f"description for {job_name}",
                    project=proj_ref,
                    backend_config=config,
                    skip_intermediate_circuits=skip_intermediate_circuits,
                )

            except Exception as e:
                raise e

            yield compile_job_ref

    return make_compile_job


@pytest.fixture(name="create_execute_job_in_project")
def fixture_create_execute_job_in_project(
    create_circuit_in_project: Callable,
) -> Callable:
    """Returns a `contextmanager` that yields a `ExecuteJobRef` of the
    execute job submitted with the specified `CircuitRef` to the project
    with the provided name.

    Notes:
        - A single element/circuit job is created.
        - The default backend_config is `qnx.AerConfig()`.
        - By default 10 shots are executed.

    Warning:
        - Will create the project and upload the circuit if needed.
        - Will not wait for the job to finish before yielding."""

    @contextmanager
    def make_execute_job(
        project_name: str,
        job_name: str,
        circuit: Circuit,
        circuit_name: str,
        backend_config: BaseBackendConfig | None = None,
        n_shots: int = 10,
    ) -> Generator[ExecuteJobRef, None, None]:
        with create_circuit_in_project(
            circuit,
            project_name,
            circuit_name,
        ) as circuit_ref:

            config = backend_config if backend_config is not None else qnx.AerConfig()

            try:
                execute_job_ref = qnx.jobs.get(name_like=job_name)
            except (ZeroMatches, NoUniqueMatch):

                proj_ref = qnx.projects.get(name_like=project_name)

                execute_job_ref = qnx.start_execute_job(
                    programs=[circuit_ref],
                    name=job_name,
                    description=f"description for {job_name}",
                    project=proj_ref,
                    backend_config=config,
                    n_shots=[n_shots],
                )

            yield execute_job_ref

    return make_execute_job


@pytest.fixture(name="create_property_in_project")
def fixture_create_property_in_project(create_project: Callable) -> Callable:
    """Returns a `contextmanager` that yields a `ProjectRef` to the project with
    `project_name` where the specified property was created.

    Notes: will create the project if it does not exist."""

    @contextmanager
    def make_temp_property(
        project_name: str,
        property_name: str,
        property_type: Literal["bool", "int", "float", "string"],
        required: bool = False,
    ) -> Generator[None, None, None]:
        with create_project(project_name) as proj_ref:
            qnx.projects.add_property(
                name=property_name,
                property_type=property_type,
                project=proj_ref,
                required=required,
            )

            yield proj_ref

    return make_temp_property


@pytest.fixture(name="create_qir_in_project")
def fixture_create_qir_in_project(create_project: Callable) -> Callable:
    """Returns a `contextmanager` that yields a `QIRRef` to the `qir_bitcode`
    uploaded to a project with `project_name`.

    Notes: will create the project if it does not exist."""

    @contextmanager
    def upload_qir(
        project_name: str,
        qir_name: str,
        qir: bytes,
    ) -> Generator[HUGRRef, None, None]:
        with create_project(project_name) as proj_ref:
            qir_ref = qnx.qir.upload(qir=qir, name=qir_name, project=proj_ref)

            yield qir_ref

    return upload_qir


@pytest.fixture(name="create_hugr_in_project")
def fixture_create_hugr_in_project(create_project: Callable) -> Callable:
    """Returns a `contextmanager` that yields a `HUGRRef` to the `hugr_package`
    uploaded to a project with `project_name`.

    Notes: will create the project if it does not exist."""

    @contextmanager
    def upload_hugr(
        project_name: str,
        hugr_name: str,
        hugr_package: Package,
    ) -> Generator[HUGRRef, None, None]:
        with create_project(project_name) as proj_ref:
            hugr_ref = qnx.hugr.upload(
                hugr_package=hugr_package,
                name=hugr_name,
                project=proj_ref,
            )

            yield hugr_ref

    return upload_hugr


@pytest.fixture(name="create_wasm_in_project")
def fixture_create_wasm_in_project(create_project: Callable) -> Callable:
    """Returns a `contextmanager` that yields a `WasmModuleRef` to the `wasm_module`
    uploaded to a project with `project_name`.

    Notes: will create the project if it does not exist."""

    @contextmanager
    def upload_wasm(
        project_name: str,
        wasm_module_name: str,
        wasm_module_handler: WasmModuleHandler,
    ) -> Generator[WasmModuleRef, None, None]:
        with create_project(project_name) as proj_ref:
            wasm_ref = qnx.wasm_modules.upload(
                wasm_module_handler=wasm_module_handler,
                name=wasm_module_name,
                project=proj_ref,
            )

            yield wasm_ref

    return upload_wasm


@pytest.fixture(scope="session")
def _authenticated_nexus_hugr(
    qa_project_name: str,
    qa_hugr_name: str,
    qa_property_name: str,
) -> Generator[None, None, None]:
    """Authenticated nexus instance fixture with a project and
    a hugr (with properties)."""
    with make_authenticated_nexus():
        test_desc = f"This can be safely deleted. Test Run: {datetime.now()}"
        my_proj = qnx.projects.get_or_create(
            name=qa_project_name, description=test_desc
        )

        qnx.projects.add_property(
            name=qa_property_name,
            property_type="string",
            project=my_proj,
        )

        hugr_path = Path("integration/data/hugr_example.hugr").resolve()
        hugr_package = Package.from_bytes(hugr_path.read_bytes())
        qnx.hugr.upload(
            hugr_package=hugr_package,
            name=qa_hugr_name,
            project=my_proj,
        )

        yield


@pytest.fixture(scope="session")
def _authenticated_nexus_empty_project(
    qa_project_name: str,
) -> Generator[None, None, None]:
    """Authenticated nexus instance fixture with a project and
    no resources created."""
    with make_authenticated_nexus():
        test_desc = f"This can be safely deleted. Test Run: {datetime.now()}"
        my_proj = qnx.projects.get_or_create(
            name=qa_project_name, description=test_desc
        )

        yield


@pytest.fixture(scope="session")
def _authenticated_nexus(
    qa_project_name: str,
    qa_property_name: str,
    qa_circuit_name: str,
    qa_circuit_name_2: str,
    qa_team_name: str,
    qa_compile_job_name: str,
    qa_execute_job_name: str,
    qa_wasm_module_name: str,
    qa_hugr_name: str,
    qa_qir_name: str,
    test_circuit: Circuit,
) -> Generator[None, None, None]:
    """Authenticated nexus instance fixture."""

    with make_authenticated_nexus():
        test_desc = f"This can be safely deleted. Test Run: {datetime.now()}"

        my_proj = qnx.projects.get_or_create(
            name=qa_project_name, description=test_desc
        )

        qnx.projects.add_property(
            name=qa_property_name,
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

        qir_bitcode = pytket_to_qir(test_circuit, name=qa_qir_name)
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


@pytest.fixture(scope="session", name="qa_property_name")
def qa_property_name_fixture() -> str:
    """A name for uniquely identifying a property created by the Nexus QA user."""
    return f"qnexus_integration_test_property_{datetime.now()}"


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


@pytest.fixture(scope="session", name="qa_hugr_package")
def qa_hugr_package_fixture() -> Package:
    hugr_path = Path("integration/data/hugr_example.hugr").resolve()
    return Package.from_bytes(hugr_path.read_bytes())


@pytest.fixture(scope="session", name="qa_wasm_module")
def qa_wasm_module_fixture() -> WasmFileHandler:
    wasm_path = Path("examples/basics/data/add_one.wasm").resolve()
    return WasmFileHandler(filepath=str(wasm_path))


@pytest.fixture(name="qa_qir_bitcode")
def qa_qir_bitcode_fixture(test_circuit: Circuit, test_case_name: str) -> bytes:
    qir_bitcode = pytket_to_qir(test_circuit, name=f"qir for {test_case_name}")
    assert isinstance(qir_bitcode, bytes)
    return qir_bitcode


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


@pytest.fixture()
def test_circuit() -> Circuit:
    """A pytket circuit to use in the integration tests."""

    circuit = Circuit(3)
    circuit.H(0)
    for i, j in zip(circuit.qubits[:-1], circuit.qubits[1:]):
        circuit.CX(i, j)
    circuit.measure_all()
    return circuit


def _get_or_create_circuit(
    circuit: Circuit,
    project_name: str,
    circuit_name: str,
) -> CircuitRef:
    """Get or create a circuit with `circuit_name` in a project with
    `project_name`."""

    project_ref = qnx.projects.get_or_create(project_name)

    # Using `qnx.circuits.get_all()` since the names of compiled
    # circuits are the same as the original circuits with some suffix,
    # which makes `qnx.circuits.get(namelike)` to return multiple circuits
    circuits_df = qnx.circuits.get_all(project=project_ref).df()

    circuits_filtered: pd.DataFrame = []
    if len(circuits_df):
        circuits_filtered = circuits_df.loc[circuits_df["name"] == circuit_name]

    if len(circuits_filtered):
        circuit_ref = qnx.circuits.get(id=str(circuits_filtered.id.values[0]))
    else:
        circuit_ref = qnx.circuits.upload(
            circuit=circuit,
            name=circuit_name,
            description=f"description for {circuit_name}",
            project=project_ref,
        )

    return circuit_ref
