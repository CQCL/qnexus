"""Test basic functionality relating to the qir module."""

from datetime import datetime

import pytest
from pytket.circuit import Circuit
from pytket.qir import pytket_to_qir  # type: ignore[attr-defined]

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
def uploaded_qir(
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

    qir_name = f"QA_test_hugr_{datetime.now()}"

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
    uploaded_qir: None,
    qa_project_name: str,
    qir_name: str,
) -> None:
    """Test that valid QIR can be extracted from an uploaded QIR module."""

    my_proj = qnx.projects.get(name_like=qa_project_name)
    my_qir_ref = qnx.qir.get(name_like=qir_name, project=my_proj)

    qir_bytes = my_qir_ref.download_qir()
    assert isinstance(qir_bytes, bytes)


def test_qir_get_by_id(
    uploaded_qir: None,
    qa_project_name: str,
    qir_name: str,
) -> None:
    """Test that we can get a QIRRef by its ID."""

    my_proj = qnx.projects.get(name_like=qa_project_name)
    my_qir_ref = qnx.qir.get(name_like=qir_name, project=my_proj)

    qir_ref_by_id = qnx.qir.get(id=my_qir_ref.id)

    assert qir_ref_by_id == my_qir_ref


def test_qir_get_all(
    uploaded_qir: None,
    qa_project_name: str,
    qir_name: str,
) -> None:
    """Test that we can get all qirRefs in a project."""

    my_proj = qnx.projects.get(name_like=qa_project_name)

    qirs = qnx.qir.get_all(project=my_proj)

    assert qirs.count() >= 1
    assert isinstance(qirs.list()[0], QIRRef)
