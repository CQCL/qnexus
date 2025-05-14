"""Test basic functionality relating to the job module."""

from collections import Counter
from datetime import datetime
from time import sleep

import pandas as pd
import pytest
from pytket.backends.backendinfo import BackendInfo
from pytket.backends.backendresult import BackendResult
from pytket.circuit import Circuit
from quantinuum_schemas.models.backend_config import BaseBackendConfig
from quantinuum_schemas.models.hypertket_config import HyperTketConfig

import qnexus as qnx
import qnexus.exceptions as qnx_exc
from qnexus.models.references import (
    CircuitRef,
    CompilationPassRef,
    CompilationResultRef,
    CompileJobRef,
    ExecuteJobRef,
    JobRef,
)


def test_job_get_all(
    _authenticated_nexus: None,
    qa_project_name: str,
) -> None:
    """Test that we can get an iterator over all jobs."""

    project_ref = qnx.projects.get(name_like=qa_project_name)

    my_job_db_matches = qnx.jobs.get_all(project=project_ref)

    assert isinstance(my_job_db_matches.count(), int)
    assert isinstance(my_job_db_matches.summarize(), pd.DataFrame)

    for job_ref in my_job_db_matches.list():
        assert isinstance(job_ref, JobRef)
        assert job_ref.backend_config is not None
        assert isinstance(job_ref.backend_config, BaseBackendConfig)


def test_job_get_by_id(
    _authenticated_nexus: None,
    qa_compile_job_name: str,
    qa_execute_job_name: str,
) -> None:
    """Test that we can get JobRefs by id."""

    my_compile_job = qnx.jobs.get(name_like=qa_compile_job_name)
    assert isinstance(my_compile_job, CompileJobRef)
    assert isinstance(my_compile_job.backend_config, BaseBackendConfig)

    my_compile_job_2 = qnx.jobs.get(id=my_compile_job.id)
    assert my_compile_job == my_compile_job_2

    my_execute_job = qnx.jobs.get(name_like=qa_execute_job_name)
    assert isinstance(my_execute_job, ExecuteJobRef)
    assert isinstance(my_execute_job.backend_config, BaseBackendConfig)

    my_execute_job_2 = qnx.jobs.get(id=my_execute_job.id)
    assert my_execute_job == my_execute_job_2


def test_compile_job_get(
    _authenticated_nexus: None,
    qa_compile_job_name: str,
) -> None:
    """Test that we can get a specific unique CompileJobRef,
    or get an appropriate exception."""

    my_job = qnx.jobs.get(name_like=qa_compile_job_name)
    assert isinstance(my_job, CompileJobRef)

    with pytest.raises(qnx_exc.NoUniqueMatch):
        qnx.jobs.get()

    with pytest.raises(qnx_exc.ZeroMatches):
        qnx.jobs.get(name_like=f"{datetime.now()}_{datetime.now()}")


def test_execute_job_get(
    _authenticated_nexus: None,
    qa_execute_job_name: str,
) -> None:
    """Test that we can get a specific unique ExecuteJobRef,
    or get an appropriate exception."""

    my_job = qnx.jobs.get(name_like=qa_execute_job_name)
    assert isinstance(my_job, ExecuteJobRef)

    with pytest.raises(qnx_exc.NoUniqueMatch):
        qnx.jobs.get()

    with pytest.raises(qnx_exc.ZeroMatches):
        qnx.jobs.get(name_like=f"{datetime.now()}_{datetime.now()}")


def test_submit_compile(
    _authenticated_nexus_circuit_ref: CircuitRef,
    qa_project_name: str,
) -> None:
    """Test that we can run a compile job in Nexus, wait for the job to complete and
    obtain the results from the compilation."""

    my_proj = qnx.projects.get(name_like=qa_project_name)

    config = qnx.AerConfig()

    compile_job_ref = qnx.start_compile_job(
        circuits=[_authenticated_nexus_circuit_ref],
        name=f"qnexus_integration_test_compile_job_{datetime.now()}",
        project=my_proj,
        backend_config=config,
        skip_intermediate_circuits=False,
    )

    assert isinstance(compile_job_ref, CompileJobRef)

    qnx.jobs.wait_for(compile_job_ref)

    compile_results = qnx.jobs.results(compile_job_ref)

    assert len(compile_results) == 1
    assert isinstance(compile_results[0], CompilationResultRef)

    assert isinstance(compile_results[0].get_input(), CircuitRef)
    assert isinstance(compile_results[0].get_output(), CircuitRef)

    first_pass_data = compile_results[0].get_passes()[0]

    assert isinstance(first_pass_data, CompilationPassRef)
    assert isinstance(first_pass_data.get_input(), CircuitRef)
    assert isinstance(first_pass_data.get_output(), CircuitRef)
    assert isinstance(first_pass_data.pass_name, str)

    cj_ref = qnx.jobs.get(id=compile_job_ref.id)
    assert cj_ref.backend_config == config


def test_compile(
    _authenticated_nexus_circuit_ref: CircuitRef,
    qa_project_name: str,
) -> None:
    """Test that we can run the utility compile function and get compiled circuits."""

    my_proj = qnx.projects.get(name_like=qa_project_name)

    compiled_circuits = qnx.compile(
        circuits=[_authenticated_nexus_circuit_ref],
        name=f"qnexus_integration_test_compile_job_{datetime.now()}",
        project=my_proj,
        backend_config=qnx.AerConfig(),
    )

    assert len(compiled_circuits) == 1
    assert isinstance(compiled_circuits[0], CircuitRef)


def test_get_results_for_incomplete_compile(
    _authenticated_nexus_circuit_ref: CircuitRef,
    qa_project_name: str,
) -> None:
    """Test that we can run a compile job in Nexus, and fetch complete results for
    an otherwise errored/incomplete job."""

    my_proj = qnx.projects.get(name_like=qa_project_name)

    compile_job_ref = qnx.start_compile_job(
        circuits=[_authenticated_nexus_circuit_ref],
        name=f"qnexus_integration_test_compile_job_{datetime.now()}",
        project=my_proj,
        backend_config=qnx.AerConfig(),
    )
    # Unsure how to guarantee that the job will be incomplete
    # This check may fail if the compilation completes quickly
    compile_results = qnx.jobs.results(compile_job_ref, allow_incomplete=True)
    assert len(compile_results) == 0


def test_compile_hypertket(
    _authenticated_nexus_circuit_ref: CircuitRef,
    qa_project_name: str,
) -> None:
    """Test that we can run compile circuits for hypertket."""

    my_proj = qnx.projects.get(name_like=qa_project_name)

    compiled_circuits = qnx.compile(
        circuits=[_authenticated_nexus_circuit_ref],
        name=f"qnexus_integration_test_compile_job_{datetime.now()}",
        project=my_proj,
        backend_config=qnx.QuantinuumConfig(device_name="H1-1LE"),
        hypertket_config=HyperTketConfig(),
    )

    assert len(compiled_circuits) == 1
    assert isinstance(compiled_circuits[0], CircuitRef)


def test_submit_execute(
    _authenticated_nexus: None,
    qa_project_name: str,
    qa_circuit_name: str,
) -> None:
    """Test that we can run an execute job in Nexus, wait for the job to complete and
    obtain the results from the execution."""

    config = qnx.AerConfig()

    my_proj = qnx.projects.get(name_like=qa_project_name)
    my_circ = qnx.circuits.get(name_like=qa_circuit_name, project=my_proj)

    execute_job_ref = qnx.start_execute_job(
        circuits=[my_circ],
        name=f"qnexus_integration_test_execute_job_{datetime.now()}",
        project=my_proj,
        backend_config=config,
        n_shots=[10],
    )

    assert isinstance(execute_job_ref, ExecuteJobRef)

    qnx.jobs.wait_for(execute_job_ref)

    execute_results = qnx.jobs.results(execute_job_ref)

    assert len(execute_results) == 1

    assert isinstance(execute_results[0].get_input(), CircuitRef)

    assert isinstance(execute_results[0].download_result(), BackendResult)

    assert isinstance(execute_results[0].download_backend_info(), BackendInfo)

    pj_ref = qnx.jobs.get(id=execute_job_ref.id)
    assert pj_ref.backend_config == config


def test_execute(
    _authenticated_nexus: None,
    qa_project_name: str,
    qa_circuit_name: str,
) -> None:
    """Test that we can run the utility execute function and get the results of the execution."""

    my_proj = qnx.projects.get(name_like=qa_project_name)
    my_circ = qnx.circuits.get(name_like=qa_circuit_name, project=my_proj)

    backend_results = qnx.execute(
        circuits=[my_circ],
        name=f"qnexus_integration_test_execute_job_{datetime.now()}",
        project=my_proj,
        backend_config=qnx.AerConfig(),
        n_shots=[10],
    )

    assert len(backend_results) == 1
    assert isinstance(backend_results[0], BackendResult)
    assert isinstance(backend_results[0].get_counts(), Counter)


def test_get_results_for_incomplete_execute(
    _authenticated_nexus: None,
    qa_project_name: str,
    qa_circuit_name: str,
) -> None:
    """Test that we can run an execute job in Nexus, and fetch complete results for
    an otherwise errored/incomplete job."""

    my_proj = qnx.projects.get(name_like=qa_project_name)
    my_circ = qnx.circuits.get(name_like=qa_circuit_name, project=my_proj)

    my_q_systems_circuit = qnx.circuits.upload(
        circuit=Circuit(2, 2).ZZPhase(0.5, 0, 1).measure_all(),
        name="qa_q_systems_circuit",
        project=my_proj,
    )

    execute_job_ref = qnx.start_execute_job(
        circuits=[my_circ, my_q_systems_circuit],
        name=f"qnexus_integration_test_execute_job_{datetime.now()}",
        project=my_proj,
        backend_config=qnx.QuantinuumConfig(device_name="H1-1LE"),
        n_shots=[10, 10],
    )

    assert isinstance(execute_job_ref, ExecuteJobRef)

    with pytest.raises(qnx_exc.JobError):
        qnx.jobs.wait_for(execute_job_ref)

    incomplete_results = qnx.jobs.results(execute_job_ref, allow_incomplete=True)

    # wait for the ZZPhase circuit execution to complete
    for _ in range(10):
        incomplete_results = qnx.jobs.results(execute_job_ref, allow_incomplete=True)
        if len(incomplete_results) > 0:
            break
        sleep(10)

    # we expect the CX circuit to fail on H1-1LE, but the ZZPhase circuit should succeed
    assert len(incomplete_results) == 1

    assert isinstance(incomplete_results[0].get_input(), CircuitRef)
    assert isinstance(incomplete_results[0].download_result(), BackendResult)
    assert isinstance(incomplete_results[0].download_backend_info(), BackendInfo)


def test_wait_for_raises_on_job_error(
    _authenticated_nexus: None,
    qa_project_name: str,
    qa_circuit_name: str,
) -> None:
    """Test that if a job errors, the wait_for function raises an Exception."""

    my_proj = qnx.projects.get(name_like=qa_project_name)

    # Circuit not compiled for H1-1LE, so we expect it to error when executed
    my_circ = qnx.circuits.get(name_like=qa_circuit_name, project=my_proj)

    failing_job_ref = qnx.start_execute_job(
        circuits=[my_circ],
        name=f"qnexus_integration_test_failing_job_{datetime.now()}",
        project=my_proj,
        n_shots=[10],
        backend_config=qnx.QuantinuumConfig(device_name="H1-1LE"),
    )

    with pytest.raises(qnx_exc.ResourceFetchFailed):
        qnx.jobs.results(failing_job_ref)

    with pytest.raises(qnx_exc.JobError):
        qnx.jobs.wait_for(failing_job_ref)


def test_results_not_available_error(
    _authenticated_nexus: None,
    qa_project_name: str,
    qa_circuit_name: str,
) -> None:
    """Test that we can't get the results of a job until it is complete."""

    my_proj = qnx.projects.get(name_like=qa_project_name)
    my_circ = qnx.circuits.get(name_like=qa_circuit_name, project=my_proj)
    execute_job_ref = qnx.start_execute_job(
        circuits=[my_circ],
        name=f"qnexus_integration_test_waiting_job_{datetime.now()}",
        project=my_proj,
        backend_config=qnx.AerConfig(),
        n_shots=[10],
    )

    with pytest.raises(qnx_exc.ResourceFetchFailed):
        qnx.jobs.results(execute_job_ref)

    qnx.jobs.wait_for(execute_job_ref)

    execute_results = qnx.jobs.results(execute_job_ref)

    assert len(execute_results) == 1

    assert isinstance(execute_results[0].get_input(), CircuitRef)

    assert isinstance(execute_results[0].download_result(), BackendResult)

    assert isinstance(execute_results[0].download_backend_info(), BackendInfo)


def test_submit_under_user_group(
    _authenticated_nexus_circuit_ref: CircuitRef,
    qa_project_name: str,
    qa_circuit_name: str,
) -> None:
    """Test that a user can submit jobs under a user_group that
    they belong to.

    Requires that the test user is a member of a group called:
    'QA_IntegrationTestGroup',
    and not a member of a group called:
    'made_up_group'.
    """

    fake_group = "made_up_group"

    my_proj = qnx.projects.get(name_like=qa_project_name)

    with pytest.raises(qnx_exc.ResourceCreateFailed) as exc:
        qnx.start_compile_job(
            circuits=[_authenticated_nexus_circuit_ref],
            name=f"qnexus_integration_test_compile_job_{datetime.now()}",
            project=my_proj,
            backend_config=qnx.AerConfig(),
            user_group=fake_group,
        )
        assert exc.value.message == f"Not a member of any group with name: {fake_group}"

    qnx.start_compile_job(
        circuits=[_authenticated_nexus_circuit_ref],
        name=f"qnexus_integration_test_compile_job_{datetime.now()}",
        project=my_proj,
        backend_config=qnx.AerConfig(),
        user_group="QA_IntegrationTestGroup",
    )

    my_circ = qnx.circuits.get(name_like=qa_circuit_name, project=my_proj)

    with pytest.raises(qnx_exc.ResourceCreateFailed):
        qnx.start_execute_job(
            circuits=[my_circ],
            name=f"qnexus_integration_test_execute_job_{datetime.now()}",
            project=my_proj,
            backend_config=qnx.AerConfig(),
            n_shots=[10],
            user_group="made_up_group",
        )
        assert exc.value.message == f"Not a member of any group with name: {fake_group}"

    qnx.start_execute_job(
        circuits=[my_circ],
        name=f"qnexus_integration_test_execute_job_{datetime.now()}",
        project=my_proj,
        backend_config=qnx.AerConfig(),
        n_shots=[10],
        user_group="QA_IntegrationTestGroup",
    )
