"""Test basic functionality relating to the circuit module."""

from datetime import datetime

import pandas as pd
import pytest
import qnexus as qnx
import qnexus.exceptions as qnx_exc
from pytket import Circuit
from qnexus.client.models.annotations import PropertiesDict
from qnexus.references import CircuitRef


def test_circuit_getonly(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get a specific unique CircuitRef,
    or get an appropriate exception."""

    my_circ = qnx.circuit.get_only(
        id="6d25444e-5901-4266-8e11-8d3b1a2765c8"
    )  # TODO use test id
    assert isinstance(my_circ, CircuitRef)

    assert isinstance(my_circ.download_circuit(), Circuit)

    with pytest.raises(qnx_exc.NoUniqueMatch):
        qnx.circuit.get_only()

    with pytest.raises(qnx_exc.ZeroMatches):
        qnx.circuit.get_only(name_like=f"{datetime.now()}_{datetime.now()}")


def test_circuit_get(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get an iterator over all circuits."""

    my_circ_db_matches = qnx.circuit.get()

    assert isinstance(my_circ_db_matches.count(), int)
    assert isinstance(my_circ_db_matches.summarize(), pd.DataFrame)

    assert isinstance(next(my_circ_db_matches), CircuitRef)


@pytest.mark.create
def test_circuit_create(
    _authenticated_nexus: None,
) -> None:
    """Test that we can create a circuit and add a property value."""

    my_proj = qnx.project.get_only(name_like="VanyaTest")  # TODO use test name

    circuit_name = f"QA_test_circuit_{datetime.now()}"

    my_circ = Circuit(2, 2).H(0).CX(0, 1).measure_all()

    my_new_circuit = qnx.circuit.upload(
        circuit=my_circ, name=circuit_name, project=my_proj
    )

    assert isinstance(my_new_circuit, CircuitRef)

    test_property_name = "QA_test_prop"  # TODO make sure this exists on the QA project
    test_prop_value = 10

    updated_circuit_ref = qnx.circuit.update(
        ref=my_new_circuit,
        properties=PropertiesDict({test_property_name: test_prop_value}),
    )

    assert (
        updated_circuit_ref.annotations.properties[test_property_name]
        == test_prop_value
    )
