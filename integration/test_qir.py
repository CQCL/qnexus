"""Test basic functionality relating to the qir module."""

from collections import Counter
from datetime import datetime

from pytket.backends.backendinfo import BackendInfo
from pytket.backends.backendresult import BackendResult
from pytket.circuit import Bit, Circuit
from pytket.qir import pytket_to_qir  # type: ignore[attr-defined]

import qnexus as qnx
from qnexus.models.annotations import PropertiesDict
from qnexus.models.references import QIRRef


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
