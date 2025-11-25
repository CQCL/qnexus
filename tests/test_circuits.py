"""Checks for circuit functionality."""

import uuid
from datetime import datetime
from unittest import mock

import pytest

from qnexus.context import using_scope
from qnexus.models.annotations import Annotations
from qnexus.models.references import CircuitRef, ProjectRef
from qnexus.models.scope import ScopeFilterEnum


@pytest.mark.parametrize(
    "chosen_scope,expected_scope",
    [
        (
            None,
            ScopeFilterEnum.USER,
        ),
        (
            ScopeFilterEnum.USER,
            ScopeFilterEnum.USER,
        ),
        (
            ScopeFilterEnum.HIGHEST,
            ScopeFilterEnum.HIGHEST,
        ),
    ],
)
@mock.patch("qnexus.client.circuits._fetch_circuit")
def test_uses_scope_when_downloading_circuit(
    fetch_circuit: mock.MagicMock,
    chosen_scope: ScopeFilterEnum,
    expected_scope: ScopeFilterEnum,
) -> None:
    """Given an circuit ref, it will hit the Nexus API with the appropriate
    scope when .download_circuit() is called."""

    circuit_ref = CircuitRef(
        id=uuid.uuid4(),
        annotations=Annotations(),
        project=ProjectRef(
            id=uuid.uuid4(), annotations=Annotations(), contents_modified=datetime.now()
        ),
    )
    if chosen_scope:
        with using_scope(chosen_scope):
            circuit_ref.download_circuit()
    else:
        circuit_ref.download_circuit()

    fetch_circuit.assert_called_once_with(circuit_ref, scope=expected_scope)
