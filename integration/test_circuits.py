"""Test basic functionality relating to the circuit module."""

from datetime import datetime

import pandas as pd
import pytest
from pytket.circuit import Circuit

import qnexus as qnx
import qnexus.exceptions as qnx_exc
from qnexus.models.annotations import PropertiesDict
from qnexus.models.references import CircuitRef


def test_circuit_get(
    _authenticated_nexus: None,
    qa_circuit_name: str,
) -> None:
    """Test that we can get a specific unique CircuitRef
    by name or id, or get an appropriate exception."""

    my_circ = qnx.circuits.get(name_like=qa_circuit_name)
    assert isinstance(my_circ, CircuitRef)

    assert isinstance(my_circ.download_circuit(), Circuit)

    my_circ_2 = qnx.circuits.get(id=my_circ.id)
    # For some reason direct equality check fails
    assert my_circ.id == my_circ_2.id
    assert my_circ.annotations == my_circ_2.annotations
    assert my_circ.project == my_circ_2.project

    with pytest.raises(qnx_exc.NoUniqueMatch):
        qnx.circuits.get()

    with pytest.raises(qnx_exc.ZeroMatches):
        qnx.circuits.get(name_like=f"{datetime.now()}_{datetime.now()}")


def test_circuit_get_all(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get an iterator over all circuits."""

    my_circ_db_matches = qnx.circuits.get_all()

    assert isinstance(my_circ_db_matches.count(), int)
    assert isinstance(my_circ_db_matches.summarize(), pd.DataFrame)

    assert isinstance(next(my_circ_db_matches), CircuitRef)


def test_circuit_create(
    _authenticated_nexus: None,
    qa_project_name: str,
) -> None:
    """Test that we can create a circuit and add a property value."""

    my_proj = qnx.projects.get(name_like=qa_project_name)

    circuit_name = f"QA_test_circuit_{datetime.now()}"

    my_circ = Circuit(2, 2).H(0).CX(0, 1).measure_all()

    my_new_circuit = qnx.circuits.upload(
        circuit=my_circ, name=circuit_name, project=my_proj
    )

    assert isinstance(my_new_circuit, CircuitRef)

    test_property_name = "QA_test_prop"
    test_prop_value = "foo"

    updated_circuit_ref = qnx.circuits.update(
        ref=my_new_circuit,
        properties=PropertiesDict({test_property_name: test_prop_value}),
    )

    assert (
        updated_circuit_ref.annotations.properties[test_property_name]
        == test_prop_value
    )


def test_circuit_get_cost(
    _authenticated_nexus: None,
    qa_project_name: str,
) -> None:
    """Test that we can get the cost to run a CircuitRef,
    on a particular Quantinuum Systems device."""

    my_proj = qnx.projects.get(name_like=qa_project_name)

    my_q_systems_circuit = qnx.circuits.upload(
        circuit=Circuit(2, 2).ZZPhase(0.5, 0, 1).measure_all(),
        name="qa_q_systems_circuit",
        project=my_proj,
    )

    cost = qnx.circuits.cost(
        circuit_ref=my_q_systems_circuit,
        n_shots=10,
        backend_config=qnx.QuantinuumConfig(device_name="H1-1E"),
        syntax_checker="H1-1SC",
    )

    assert isinstance(cost, float)
    assert cost > 0.0
