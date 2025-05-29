"""Test basic functionality relating to the device module."""

import pytest
from pytket.backends.backendinfo import BackendInfo
from quantinuum_schemas.models.backend_config import BackendConfig
from quantinuum_schemas.models.backend_info import StoredBackendInfo

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
        assert isinstance(device.stored_backend_info, StoredBackendInfo)
        assert isinstance(device.backend_info, BackendInfo)


def test_supports_shots(
    _authenticated_nexus: None,
    backend_config: BackendConfig,
) -> None:
    """Test whether a BackendConfig supports shots."""

    supports_shots = qnx.devices.supports_shots(backend_config)
    assert isinstance(supports_shots, bool)


def test_supports_counts(
    _authenticated_nexus: None,
    backend_config: BackendConfig,
) -> None:
    """Test whether a BackendConfig supports counts."""

    supports_counts = qnx.devices.supports_counts(backend_config)
    assert isinstance(supports_counts, bool)


def test_supports_state(
    _authenticated_nexus: None,
    backend_config: BackendConfig,
) -> None:
    """Test whether a BackendConfig supports state."""

    supports_state = qnx.devices.supports_state(backend_config)
    assert isinstance(supports_state, bool)


def test_supports_unitary(
    _authenticated_nexus: None,
    backend_config: BackendConfig,
) -> None:
    """Test whether a BackendConfig supports unitary."""

    supports_unitary = qnx.devices.supports_unitary(backend_config)
    assert isinstance(supports_unitary, bool)


def test_supports_density_matrix(
    _authenticated_nexus: None,
    backend_config: BackendConfig,
) -> None:
    """Test whether a BackendConfig supports density matrix."""

    supports_density_matrix = qnx.devices.supports_density_matrix(backend_config)
    assert isinstance(supports_density_matrix, bool)


def test_supports_expectation(
    _authenticated_nexus: None,
    backend_config: BackendConfig,
) -> None:
    """Test whether a BackendConfig supports expectation."""

    supports_expectation = qnx.devices.supports_expectation(backend_config)
    assert isinstance(supports_expectation, bool)


def test_expectation_allows_nonhermitian(
    _authenticated_nexus: None,
    backend_config: BackendConfig,
) -> None:
    """Test whether a BackendConfig supports expectation_allows_nonhermitian."""

    expectation_allows_nonhermitian = qnx.devices.expectation_allows_nonhermitian(
        backend_config
    )
    assert isinstance(expectation_allows_nonhermitian, bool)


def test_supports_contextual_optimisation(
    _authenticated_nexus: None,
    backend_config: BackendConfig,
) -> None:
    """Test whether a BackendConfig supports contextual optimisation."""
    supports_contextual_optimisation = qnx.devices.supports_contextual_optimisation(
        backend_config
    )
    assert isinstance(supports_contextual_optimisation, bool)


def test_quantinuum_device_status(
    _authenticated_nexus: None,
) -> None:
    """Check that we can get the status of a hardware-hosted
    Quantinuum device."""

    unsupported_config = qnx.AerConfig()
    with pytest.raises(AssertionError):
        qnx.devices.status(unsupported_config)  # type: ignore

    backend_config = qnx.QuantinuumConfig(device_name="H1-1")

    machine_status = qnx.devices.status(backend_config)

    assert isinstance(machine_status, qnx.devices.DeviceStateEnum)
