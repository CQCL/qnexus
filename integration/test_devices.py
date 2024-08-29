"""Test basic functionality relating to the device module."""

import qnexus as qnx
from qnexus.models import Device
from qnexus.models.references import DataframableList


def test_device_get_all(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get a list of devices."""
    devices = qnx.devices.get_all()
    assert isinstance(devices, DataframableList)

    for device in devices:
        assert isinstance(device, Device)


def test_supports_shots(
    _authenticated_nexus: None,
) -> None:
    """Test whether a BackendConfig supports shots."""
    backend_config = qnx.QuantinuumConfig(device_name="H1-1LE")

    supports_shots = qnx.devices.supports_shots(backend_config)

    assert isinstance(supports_shots, bool)


def test_supports_counts(
    _authenticated_nexus: None,
) -> None:
    """Test whether a BackendConfig supports counts."""
    backend_config = qnx.QuantinuumConfig(device_name="H1-1LE")

    supports_counts = qnx.devices.supports_counts(backend_config)

    assert isinstance(supports_counts, bool)


def test_supports_state(
    _authenticated_nexus: None,
) -> None:
    """Test whether a BackendConfig supports state."""
    backend_config = qnx.QuantinuumConfig(device_name="H1-1LE")

    supports_state = qnx.devices.supports_state(backend_config)

    assert isinstance(supports_state, bool)


def test_supports_unitary(
    _authenticated_nexus: None,
) -> None:
    """Test whether a BackendConfig supports unitary."""
    backend_config = qnx.QuantinuumConfig(device_name="H1-1LE")

    supports_unitary = qnx.devices.supports_unitary(backend_config)

    assert isinstance(supports_unitary, bool)


def test_supports_density_matrix(
    _authenticated_nexus: None,
) -> None:
    """Test whether a BackendConfig supports density matrix."""
    backend_config = qnx.QuantinuumConfig(device_name="H1-1LE")

    supports_density_matrix = qnx.devices.supports_density_matrix(backend_config)

    assert isinstance(supports_density_matrix, bool)


def test_supports_expectation(
    _authenticated_nexus: None,
) -> None:
    """Test whether a BackendConfig supports expectation."""
    backend_config = qnx.QuantinuumConfig(device_name="H1-1LE")

    supports_expectation = qnx.devices.supports_expectation(backend_config)

    assert isinstance(supports_expectation, bool)


def test_expectation_allows_nonhermitian(
    _authenticated_nexus: None,
) -> None:
    """Test whether a BackendConfig supports expectation_allows_nonhermitian."""
    backend_config = qnx.QuantinuumConfig(device_name="H1-1LE")

    expectation_allows_nonhermitian = qnx.devices.expectation_allows_nonhermitian(
        backend_config
    )

    assert isinstance(expectation_allows_nonhermitian, bool)


def test_supports_contextual_optimisation(
    _authenticated_nexus: None,
) -> None:
    """Test whether a BackendConfig supports contextual optimisation."""
    backend_config = qnx.QuantinuumConfig(device_name="H1-1LE")

    supports_contextual_optimisation = qnx.devices.supports_contextual_optimisation(
        backend_config
    )

    assert isinstance(supports_contextual_optimisation, bool)
