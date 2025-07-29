"""Test basic functionality relating to the qir module."""

from collections import Counter
from datetime import datetime
from pathlib import Path

import pyqir
from hugr.qsystem.result import QsysResult
from pytket.backends.backendinfo import BackendInfo
from pytket.backends.backendresult import BackendResult
from pytket.circuit import Bit, Circuit
from pytket.qir import pytket_to_qir  # type: ignore[attr-defined]

import qnexus as qnx
from qnexus.models.annotations import PropertiesDict
from qnexus.models.references import QIRRef, QIRResult, ResultVersions


def test_qir_create_and_update(
    _authenticated_nexus: None,
    qa_project_name: str,
    circuit: Circuit,
) -> None:
    """Test that we can create a qir and add a property value."""

    my_proj = qnx.projects.get(name_like=qa_project_name)

    qir_name = f"QA_test_qir_{datetime.now()}"

    qir_bitcode = pytket_to_qir(circuit, name=qir_name)
    assert isinstance(qir_bitcode, bytes)
    my_new_qir = qnx.qir.upload(qir=qir_bitcode, name=qir_name, project=my_proj)

    assert isinstance(my_new_qir, QIRRef)

    test_property_name = "QA_test_prop"
    test_prop_value = "foo"

    updated_qir_ref = qnx.qir.update(
        ref=my_new_qir,
        properties=PropertiesDict({test_property_name: test_prop_value}),
    )

    assert updated_qir_ref.annotations.properties[test_property_name] == test_prop_value


def test_qir_download(
    _authenticated_nexus: None,
    qa_project_name: str,
    qa_qir_name: str,
) -> None:
    """Test that QIR bytes can be downloaded from an uploaded QIR module."""

    my_proj = qnx.projects.get(name_like=qa_project_name)
    my_qir_ref = qnx.qir.get(name_like=qa_qir_name, project=my_proj)

    qir_bytes = my_qir_ref.download_qir()
    assert isinstance(qir_bytes, bytes)


def test_qir_get_by_id(
    _authenticated_nexus: None,
    qa_project_name: str,
    qa_qir_name: str,
) -> None:
    """Test that we can get a QIRRef by its ID."""

    my_proj = qnx.projects.get(name_like=qa_project_name)
    my_qir_ref = qnx.qir.get(name_like=qa_qir_name, project=my_proj)

    qir_ref_by_id = qnx.qir.get(id=my_qir_ref.id)

    assert qir_ref_by_id == my_qir_ref


def test_qir_get_all(
    _authenticated_nexus: None,
    qa_project_name: str,
    qa_qir_name: str,
) -> None:
    """Test that we can get all qirRefs in a project."""

    my_proj = qnx.projects.get(name_like=qa_project_name)

    qirs = qnx.qir.get_all(project=my_proj)

    assert qirs.count() >= 1
    assert isinstance(qirs.list()[0], QIRRef)


def test_execution(
    _authenticated_nexus: None,
    qa_project_name: str,
    qa_qir_name: str,
) -> None:
    """Test the execution of a QIR program."""

    device_name = "H1-1SC"  # Syntax checker - no results

    project_ref = qnx.projects.get_or_create(name=qa_project_name)

    qir_program_ref = qnx.qir.get(name_like=qa_qir_name)

    job_ref = qnx.start_execute_job(
        programs=[qir_program_ref],
        n_shots=[10],
        backend_config=qnx.QuantinuumConfig(device_name=device_name),
        project=project_ref,
        name=f"QA Test QIR job from {datetime.now()}",
    )

    qnx.jobs.wait_for(job_ref)

    results = qnx.jobs.results(job_ref)

    assert len(results) == 1
    result_ref = results[0]

    assert isinstance(result_ref.download_backend_info(), BackendInfo)
    assert isinstance(result_ref.get_input(), QIRRef)

    assert result_ref.get_input().id == qir_program_ref.id

    qir_result = qnx.jobs.results(job_ref)[0].download_result()
    assert isinstance(qir_result, BackendResult)
    assert qir_result.get_counts() == Counter({(0, 0, 0): 10})
    assert qir_result.get_bitlist() == [Bit("c", 2), Bit("c", 1), Bit("c", 0)]


def test_execution_on_NG_devices(
    _authenticated_nexus: None,
    qa_project_name: str,
) -> None:
    """Test execution on NG devices, specifically to focus on getting the results"""
    project_ref = qnx.projects.get_or_create(name=qa_project_name)

    qir_ref = qnx.qir.upload(
        qir=make_qir_bitcode_from_file("RandomWalkPhaseEstimation.ll"),
        name="ng_qir_module_name",
        project=project_ref,
    )

    qir_program_ref = qnx.qir.get(id=qir_ref.id)

    job_ref = qnx.start_execute_job(
        programs=[qir_program_ref],
        n_shots=[10],
        backend_config=qnx.QuantinuumConfig(device_name="Helios-1E", max_cost=10),
        project=project_ref,
        name=f"QA Test QIR job from {datetime.now()}",
    )

    qnx.jobs.wait_for(job_ref)

    results = qnx.jobs.results(job_ref)[0].download_result()
    # Assert this is a QIR compliant result
    assert isinstance(results, QIRResult)
    assert results.results.startswith("HEADER\tschema_id\tlabeled")
    # Can't assert the value is the same, so just check the output is there
    assert "OUTPUT\tDOUBLE" in results.results

    v4_results = qnx.jobs.results(job_ref)[0].download_result(
        version=ResultVersions.RAW
    )
    # Assert this is in v4 format
    assert isinstance(v4_results, QsysResult)
    assert v4_results.results[0].entries[0][0] == "USER:FLOAT:d0"


def make_qir_bitcode_from_file(filename: str) -> bytes:
    with open(
        Path(__file__).parent.resolve() / "data" / filename,
        "r",
    ) as file:
        return pyqir.Module.from_ir(pyqir.Context(), file.read()).bitcode
