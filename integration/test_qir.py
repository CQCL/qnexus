"""Test basic functionality relating to the qir module."""

from datetime import datetime

import pytest
from pytket.circuit import Circuit
from pytket.qir import pytket_to_qir  # type: ignore[attr-defined]
from pytket.backends.backendinfo import BackendInfo

import qnexus as qnx
from qnexus.models.annotations import PropertiesDict
from qnexus.models.references import QIRRef


@pytest.fixture(scope="session")
def circuit() -> Circuit:
    """A pytket circuit"""

    circuit = Circuit(3)
    circuit.H(0)
    for i, j in zip(circuit.qubits[:-1], circuit.qubits[1:]):
        circuit.CX(i, j)
    circuit.measure_all()
    return circuit


@pytest.fixture(scope="session")
def qir_name() -> str:
    """A name for uniquely identifying a QIR program owned by the Nexus QA user"""
    return f"qnexus_integration_test_qir_{datetime.now()}"


@pytest.fixture(scope="session")
def qir_program_ref(
    project: None, qa_project_name: str, circuit: Circuit, qir_name: str
) -> QIRRef:
    """An uploaded QIR program"""

    my_proj = qnx.projects.get(name_like=qa_project_name)
    qir_bitcode = pytket_to_qir(circuit, name=qir_name)
    assert isinstance(qir_bitcode, bytes)
    return qnx.qir.upload(qir=qir_bitcode, name=qir_name, project=my_proj)


def test_qir_create_and_update(
    project: None,
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
    qir_program_ref: QIRRef,
    qa_project_name: str,
    qir_name: str,
) -> None:
    """Test that valid QIR can be extracted from an uploaded QIR module."""

    my_proj = qnx.projects.get(name_like=qa_project_name)
    my_qir_ref = qnx.qir.get(name_like=qir_name, project=my_proj)

    qir_bytes = my_qir_ref.download_qir()
    assert isinstance(qir_bytes, bytes)


def test_qir_get_by_id(
    qir_program_ref: QIRRef,
    qa_project_name: str,
    qir_name: str,
) -> None:
    """Test that we can get a QIRRef by its ID."""

    my_proj = qnx.projects.get(name_like=qa_project_name)
    my_qir_ref = qnx.qir.get(name_like=qir_name, project=my_proj)

    qir_ref_by_id = qnx.qir.get(id=my_qir_ref.id)

    assert qir_ref_by_id == my_qir_ref


def test_qir_get_all(
    qir_program_ref: QIRRef,
    qa_project_name: str,
    qir_name: str,
) -> None:
    """Test that we can get all qirRefs in a project."""

    my_proj = qnx.projects.get(name_like=qa_project_name)

    qirs = qnx.qir.get_all(project=my_proj)

    assert qirs.count() >= 1
    assert isinstance(qirs.list()[0], QIRRef)


def test_execution(
    qir_program_ref: QIRRef,
    project: str,
    qir_name: str,
) -> None:
    """Test the execution of a QIR program."""

    device_name = "H1-1SC"  # Syntax checker - no results

    job_ref = qnx.start_execute_job(
        programs=[qir_program_ref],
        n_shots=[10],
        backend_config=qnx.QuantinuumConfig(device_name=device_name),
        name=f"QA Test QIR job from {datetime.now()}",
    )

    qnx.jobs.wait_for(job_ref)

    results = qnx.jobs.results(job_ref)

    assert len(results) == 1
    result_ref = results[0]

    assert isinstance(result_ref.download_backend_info(), BackendInfo)
    assert isinstance(result_ref.get_input(), QIRRef)

    assert result_ref.get_input().id == qir_program_ref.id

    # TODO
    # qir_result = cast(QsysResult, result_ref.download_result())
    # assert len(qir_result.results) == n_shots

    # # assert qir_result.results[0].entries[0][0] == "teleported"
    # # assert qir_result.results[0].entries[0][1] == 1

    # # # check some QsysResults functionality
    # # assert len(qir_result.collated_counts().items()) > 0
