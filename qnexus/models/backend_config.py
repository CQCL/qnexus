"""Defines classes that pass information about the backend to be used for processing
a circuit, and any parameters needed to set up an instance of that backend.

These do not include any parameters that are used to pass access tokens or other credentials,
as our backend credential classes handle those.
"""
# pylint: disable=too-many-lines
import abc
from typing import Any, Dict, Literal, Optional, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    PositiveInt,
    field_validator,
    model_validator,
)
from pydantic.fields import Field
from typing_extensions import Annotated

from qnexus.models.aer_noise import AerNoiseModel, CrosstalkParams
from qnexus.models.h_series_noise import UserErrorParams


class BaseBackendConfig(BaseModel, abc.ABC):
    """Base class for all the backend configs."""

    model_config = ConfigDict(frozen=True)


class AerConfig(BaseBackendConfig):
    """Qiskit Aer QASM simulator."""

    type: Literal["AerConfig"] = "AerConfig"
    noise_model: Optional[AerNoiseModel] = None
    simulation_method: str = "automatic"
    crosstalk_params: Optional[CrosstalkParams] = None
    n_qubits: PositiveInt = 40

    @field_validator("noise_model", mode="before")
    @classmethod
    def validate_noise_model(
        cls,
        value: Any,
    ) -> Optional[AerNoiseModel]:
        """Validate that we can use this"""
        if value is not None:
            if isinstance(value, AerNoiseModel):
                return value
            if hasattr(value, "to_dict"):
                # Should cover the case of an Aer NoiseModel being passed directly.
                # Needs to be passed serializable=True to prevent numpy
                # arrays being included in the dictionary.
                return AerNoiseModel(**value.to_dict(serializable=True))
            if isinstance(value, dict):
                return AerNoiseModel(**value)
            raise ValueError(
                "must be an AerNoiseModel, a qiskit-aer NoiseModel or conform to the spec."
            )
        return None


class AerStateConfig(BaseBackendConfig):
    """Qiskit Aer statevector simulator."""

    type: Literal["AerStateConfig"] = "AerStateConfig"
    n_qubits: PositiveInt = 40


class AerUnitaryConfig(BaseBackendConfig):
    """Qiskit Aer unitary simulator."""

    type: Literal["AerUnitaryConfig"] = "AerUnitaryConfig"
    n_qubits: PositiveInt = 40


class BraketConfig(BaseBackendConfig):
    """Runs circuits on quantum devices and simulators using Amazon's Braket service."""

    type: Literal["BraketConfig"] = "BraketConfig"
    local: bool
    local_device: str = "default"
    device_type: Optional[str] = None
    provider: Optional[str] = None
    device: Optional[
        str
    ] = None  # The quantum computer or simulator to run a circuit on.
    s3_bucket: Optional[str] = None
    s3_folder: Optional[str] = None
    # Parameters below are kwargs used in BraketBackend.process_circuits().
    simplify_initial: bool = False

    @model_validator(mode="before")
    def check_local_remote_parameters_are_consistent(  # pylint: disable=no-self-argument,
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that the parameters for BraketConfig are consistent for either a local device,
        or a remote device."""
        if values.get("local"):
            # For a local config, we care about local_device only. This has a default value,
            # so we don't need to validate it, but we should give a ValidationError if any of
            # the other items are set.
            if any(
                (
                    values.get(remote_field) is not None
                    for remote_field in (
                        "device_type",
                        "provider",
                        "device",
                        "s3_bucket",
                        "s3_folder",
                    )
                )
            ):
                raise ValueError(
                    "BraketConfig with local=True must only have local and local_device set"
                )
        else:
            # We can ignore local_device, because it has a default value in BraketBackend,
            # but all of the other parameters must be set.
            if any(
                (
                    values.get(remote_field) is None
                    for remote_field in (
                        "device_type",
                        "provider",
                        "device",
                        "s3_bucket",
                        "s3_folder",
                    )
                )
            ):
                raise ValueError(
                    "BraketConfig with local=False must have device_type, provider, device, "
                    "s3_bucket and s3_folder set"
                )
        return values


class QuantinuumCompilerOptions(BaseModel):
    """Class for Quantinuum Compiler Options.

    Intentionally allows extra unknown flags to be defined.
    """

    model_config = ConfigDict(extra="allow", frozen=True)

    @model_validator(mode="before")
    def check_field_values_are_supported_types(  # pylint: disable=no-self-argument,
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check that compiler option values are supported types."""
        for key in values:
            assert isinstance(
                values[key], (str, int, bool)
            ), "Compiler options must be str, bool or int"
        return values


class QuantinuumConfig(BaseBackendConfig):
    """Runs circuits on Quantinuum's quantum devices and simulators."""

    type: Literal["QuantinuumConfig"] = "QuantinuumConfig"
    device_name: str  # The quantum computer or simulator to run a circuit on.
    simulator: str = (
        "state-vector"  # If device_name is a simulator, the type of simulator to use.
    )
    machine_debug: bool = False
    attempt_batching: bool = False
    # Parameters below are passed into QuantinuumBackend.compilation_config in their own class.
    allow_implicit_swaps: bool = True
    target_2qb_gate: Optional[str] = None
    # Parameters below are kwargs used in QuantinuumBackend.process_circuits().
    noisy_simulation: bool = True
    user_group: Optional[str] = None
    compiler_options: Optional[QuantinuumCompilerOptions] = None
    no_opt: bool = True
    allow_2q_gate_rebase: bool = False
    leakage_detection: bool = False
    simplify_initial: bool = False
    error_params: Optional[UserErrorParams] = None


class IBMQConfig(BaseBackendConfig):
    """Runs circuits on IBM's quantum devices and simulators."""

    type: Literal["IBMQConfig"] = "IBMQConfig"
    backend_name: str  # The quantum computer or simulator to run a circuit on.
    hub: str
    group: str
    project: str
    monitor: bool = False
    # Parameters below are kwargs used in IBMQBackend.process_circuits().
    simplify_initial: bool = False


class IBMQEmulatorConfig(BaseBackendConfig):
    """
    Runs circuits on the IBM-hosted simulator ibmq_qasm_simulator, using the noise model "
    of a specific IBM quantum device.
    """

    type: Literal["IBMQEmulatorConfig"] = "IBMQEmulatorConfig"
    backend_name: str  # The quantum computer to emulate.
    hub: str
    group: str
    project: str


class ProjectQConfig(BaseBackendConfig):
    """ProjectQ statevector simulator."""

    type: Literal["ProjectQConfig"] = "ProjectQConfig"


class QulacsConfig(BaseBackendConfig):
    """ "Qulacs simulator."""

    type: Literal["QulacsConfig"] = "QulacsConfig"
    result_type: str = "state_vector"


BackendConfig = Annotated[
    Union[
        AerConfig,
        AerStateConfig,
        AerUnitaryConfig,
        BraketConfig,
        QuantinuumConfig,
        IBMQConfig,
        IBMQEmulatorConfig,
        ProjectQConfig,
        QulacsConfig,
    ],
    Field(discriminator="type"),
]

config_name_to_class: Dict[str, BackendConfig] = {
    config_type.__name__: config_type  # type: ignore
    for config_type in BaseBackendConfig.__subclasses__()
}
