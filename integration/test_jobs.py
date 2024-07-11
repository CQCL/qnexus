"""Test basic functionality relating to the job module."""

from datetime import datetime

import pandas as pd
import pytest
from pytket.backends.backendinfo import BackendInfo
from pytket.backends.backendresult import BackendResult

import qnexus as qnx
import qnexus.exceptions as qnx_exc
from qnexus.references import (CircuitRef, CompilationPassRef,
                               CompilationResultRef, CompileJobRef,
                               ExecuteJobRef, JobRef)


def test_job_get(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get an iterator over all jobs."""

    my_job_db_matches = qnx.job.get()

    assert isinstance(my_job_db_matches.count(), int)
    assert isinstance(my_job_db_matches.summarize(), pd.DataFrame)

    assert isinstance(next(my_job_db_matches), JobRef)


def test_compile_job_getonly(
    _authenticated_nexus: None,
    qa_compile_job_name: str,
) -> None:
    """Test that we can get a specific unique CompileJobRef,
    or get an appropriate exception."""

    my_job = qnx.job.get_only(name_like=qa_compile_job_name)
    assert isinstance(my_job, CompileJobRef)

    with pytest.raises(qnx_exc.NoUniqueMatch):
        qnx.job.get_only()

    with pytest.raises(qnx_exc.ZeroMatches):
        qnx.job.get_only(name_like=f"{datetime.now()}_{datetime.now()}")


def test_execute_job_getonly(
    _authenticated_nexus: None,
    qa_execute_job_name: str,
) -> None:
    """Test that we can get a specific unique ExecuteJobRef,
    or get an appropriate exception."""

    my_job = qnx.job.get_only(name_like=qa_execute_job_name)
    assert isinstance(my_job, ExecuteJobRef)

    with pytest.raises(qnx_exc.NoUniqueMatch):
        qnx.job.get_only()

    with pytest.raises(qnx_exc.ZeroMatches):
        qnx.job.get_only(name_like=f"{datetime.now()}_{datetime.now()}")


def test_compile(
    _authenticated_nexus_circuit_ref: CircuitRef,
    qa_project_name: str,
) -> None:
    """Test that we can run a compile job in Nexus, wait for the job to complete and
    obtain the results from the compilation."""

    my_proj = qnx.project.get_only(name_like=qa_project_name)

    compile_job_ref = qnx.compile(
        circuits=[_authenticated_nexus_circuit_ref],
        name=f"qnexus_integration_test_compile_job_{datetime.now()}",
        project=my_proj,
        backend_config=qnx.AerConfig(),
    )

    assert isinstance(compile_job_ref, CompileJobRef)

    qnx.job.wait_for(compile_job_ref)

    compile_results = qnx.job.results(compile_job_ref)

    assert len(compile_results) == 1
    assert isinstance(compile_results[0], CompilationResultRef)

    assert isinstance(compile_results[0].get_input(), CircuitRef)
    assert isinstance(compile_results[0].get_output(), CircuitRef)

    first_pass_data = compile_results[0].get_passes()[0]

    assert isinstance(first_pass_data, CompilationPassRef)
    assert isinstance(first_pass_data.get_input(), CircuitRef)
    assert isinstance(first_pass_data.get_output(), CircuitRef)
    assert isinstance(first_pass_data.pass_name, str)


def test_execute(
    _authenticated_nexus: None,
    qa_project_name: str,
    qa_circuit_name: str,
) -> None:
    """Test that we can run an execute job in Nexus, wait for the job to complete and
    obtain the results from the execution."""

    my_proj = qnx.project.get_only(name_like=qa_project_name)
    my_circ = qnx.circuit.get_only(name_like=qa_circuit_name, project=my_proj)

    execute_job_ref = qnx.execute(
        circuits=[my_circ],
        name=f"qnexus_integration_test_execute_job_{datetime.now()}",
        project=my_proj,
        backend_config=qnx.AerConfig(),
        n_shots=[10],
    )

    assert isinstance(execute_job_ref, ExecuteJobRef)

    qnx.job.wait_for(execute_job_ref)

    execute_results = qnx.job.results(execute_job_ref)

    assert len(execute_results) == 1

    assert isinstance(execute_results[0].get_input(), CircuitRef)

    assert isinstance(execute_results[0].download_result(), BackendResult)

    assert isinstance(execute_results[0].download_backend_info(), BackendInfo)


def test_wait_for_raises_on_job_error(
    _authenticated_nexus: None,
    qa_project_name: str,
    qa_circuit_name: str,
) -> None:
    """Test that if a job errors, the wait_for function raises an Exception."""

    my_proj = qnx.project.get_only(name_like=qa_project_name)

    # Circuit not compiled for H1-1LE, so we expect it to error when executed
    my_circ = qnx.circuit.get_only(name_like=qa_circuit_name, project=my_proj)

    failing_job_ref = qnx.execute(
        circuits=[my_circ],
        name=f"qnexus_integration_test_failing_job_{datetime.now()}",
        project=my_proj,
        n_shots=[10],
        backend_config=qnx.QuantinuumConfig(device_name="H1-1LE"),
    )

    with pytest.raises(qnx_exc.ResourceFetchFailed):
        qnx.job.results(failing_job_ref)

    with pytest.raises(qnx_exc.JobError):
        qnx.job.wait_for(failing_job_ref)


def test_results_not_available_error(
    _authenticated_nexus: None,
    qa_project_name: str,
    qa_circuit_name: str,
) -> None:
    """Test that we can't get the results of a job until it is complete."""

    my_proj = qnx.project.get_only(name_like=qa_project_name)
    my_circ = qnx.circuit.get_only(name_like=qa_circuit_name, project=my_proj)
    execute_job_ref = qnx.execute(
        circuits=[my_circ],
        name=f"qnexus_integration_test_waiting_job_{datetime.now()}",
        project=my_proj,
        backend_config=qnx.AerConfig(),
        n_shots=[10],
    )

    with pytest.raises(qnx_exc.ResourceFetchFailed):
        qnx.job.results(execute_job_ref)

    qnx.job.wait_for(execute_job_ref)

    execute_results = qnx.job.results(execute_job_ref)

    assert len(execute_results) == 1

    assert isinstance(execute_results[0].get_input(), CircuitRef)

    assert isinstance(execute_results[0].download_result(), BackendResult)

    assert isinstance(execute_results[0].download_backend_info(), BackendInfo)
