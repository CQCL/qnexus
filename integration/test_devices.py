"""Test basic functionality relating to the device module."""

from pytket.backends.backendinfo import BackendInfo

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
        assert device.backend_info_dict is not None  # pylint: disable=protected-access
        assert isinstance(device.backend_info, BackendInfo)


def test_supports_shots(
    _authenticated_nexus: None,
) -> None:
    """Test whether a BackendConfig supports shots."""
    backend_config = qnx.QuantinuumConfig(device_name="H1-1LE")

    supports_shots = qnx.devices.supports_shots(backend_config)

    assert isinstance(supports_shots, bool)
    assert supports_shots is True


def test_supports_counts(
    _authenticated_nexus: None,
) -> None:
    """Test whether a BackendConfig supports counts."""
    backend_config = qnx.QuantinuumConfig(device_name="H1-1LE")

    supports_counts = qnx.devices.supports_counts(backend_config)

    assert isinstance(supports_counts, bool)
    assert supports_counts is True


def test_supports_state(
    _authenticated_nexus: None,
) -> None:
    """Test whether a BackendConfig supports state."""
    backend_config = qnx.QuantinuumConfig(device_name="H1-1LE")

    supports_state = qnx.devices.supports_state(backend_config)

    assert isinstance(supports_state, bool)
    assert supports_state is False


def test_supports_unitary(
    _authenticated_nexus: None,
) -> None:
    """Test whether a BackendConfig supports unitary."""
    backend_config = qnx.QuantinuumConfig(device_name="H1-1LE")

    supports_unitary = qnx.devices.supports_unitary(backend_config)

    assert isinstance(supports_unitary, bool)
    assert supports_unitary is False


def test_supports_density_matrix(
    _authenticated_nexus: None,
) -> None:
    """Test whether a BackendConfig supports density matrix."""
    backend_config = qnx.QuantinuumConfig(device_name="H1-1LE")

    supports_density_matrix = qnx.devices.supports_density_matrix(backend_config)

    assert isinstance(supports_density_matrix, bool)
    assert supports_density_matrix is False


def test_supports_expectation(
    _authenticated_nexus: None,
) -> None:
    """Test whether a BackendConfig supports expectation."""
    backend_config = qnx.QuantinuumConfig(device_name="H1-1LE")

    supports_expectation = qnx.devices.supports_expectation(backend_config)

    assert isinstance(supports_expectation, bool)
    assert supports_expectation is False


def test_expectation_allows_nonhermitian(
    _authenticated_nexus: None,
) -> None:
    """Test whether a BackendConfig supports expectation_allows_nonhermitian."""
    backend_config = qnx.QuantinuumConfig(device_name="H1-1LE")

    expectation_allows_nonhermitian = qnx.devices.expectation_allows_nonhermitian(
        backend_config
    )

    assert isinstance(expectation_allows_nonhermitian, bool)
    assert expectation_allows_nonhermitian is False


def test_supports_contextual_optimisation(
    _authenticated_nexus: None,
) -> None:
    """Test whether a BackendConfig supports contextual optimisation."""
    backend_config = qnx.QuantinuumConfig(device_name="H1-1LE")

    supports_contextual_optimisation = qnx.devices.supports_contextual_optimisation(
        backend_config
    )

    assert isinstance(supports_contextual_optimisation, bool)
    assert supports_contextual_optimisation is True
