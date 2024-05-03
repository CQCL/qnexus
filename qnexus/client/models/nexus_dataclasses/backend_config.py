"""Defines classes that pass information about the backend to be used for processing
a circuit, and any parameters needed to set up an instance of that backend.

These do not include any parameters that are used to pass access tokens or other credentials,
as our backend credential classes handle those.
"""
# pylint: disable=too-many-lines
import abc
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    PositiveInt,
    field_validator,
    model_validator,
)
from pydantic.fields import Field
from typing_extensions import Annotated

from qnexus.client.models.nexus_dataclasses.aer_noise import (
    AerNoiseModel,
    CrosstalkParams,
)


class ResultAvailability(Enum):
    """Describes if batches of results submitted to the backend
    become available for retrieval all at once or as a batch.
    """

    INDIVIDUAL = 1
    BATCH = 2


class BaseBackendConfig(BaseModel, abc.ABC):
    """Base class for all the backend configs."""

    model_config = ConfigDict(frozen=True)

    @staticmethod
    def description() -> str:
        """A sentence that describes the backend that this config represents."""
        raise NotImplementedError

    @staticmethod
    def fully_qualified_name() -> str:
        """The fully-qualified name for importing the backend that this config uses.

        This is another mypy type hint to make sure the method can be used anywhere
        that the base config is passed.

        Config classes must implement this method."""
        raise NotImplementedError

    @staticmethod
    def n_shots_required() -> bool:
        """A method indicating whether the backend needs n_shots to be passed for .process_circuit,
        which allows us to do better initial JSON validation.

        Config classes must implement this method."""
        raise NotImplementedError

    @staticmethod
    def qasm_header() -> str:
        """The header string to use when generating QASM for a particular backend.

        We have a default value on this parent class, so this only needs to be implemented
        for backend configs that use a different string to the default."""
        return "qelib1"

    def is_nexus_simulator(self) -> bool:
        """If True, this backend is for a simulator that will be run within Nexus.
        If False, this backend is for an external quantum system (either physical or simulated)
        that Nexus calls to run circuits on.

        Unlike most of the other methods, this is not a static method, because in some cases
        the instance parameters affect whether the backend will control a local simulator.

        Config classes must implement this method."""
        raise NotImplementedError

    @staticmethod
    def requires_credentials() -> bool:
        """If False, this backend requires no credentials to be used.
        If True this backend requires matching credentials to be set via the Nexus website
        before it can be used."""
        return False

    @staticmethod
    def result_availability() -> ResultAvailability:
        """How the results become available to the backend.

        Defaults to INDIVIDUAL.
        """
        return ResultAvailability.INDIVIDUAL


class AerConfig(BaseBackendConfig):
    """
    * Extension library for backend: pytket-qiskit.
    * Backend location: pytket.extensions.qiskit.backends.aer.AerBackend.
    """

    type: Literal["AerConfig"] = "AerConfig"
    noise_model: Optional[AerNoiseModel] = None
    simulation_method: str = "automatic"
    crosstalk_params: Optional[CrosstalkParams] = None
    n_qubits: PositiveInt = 40
    # Parameters below are kwargs used in AerBackend.process_circuits().
    seed: Optional[int] = None

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

    @staticmethod
    def description() -> str:
        return "Qiskit Aer QASM simulator."

    @staticmethod
    def fully_qualified_name() -> str:
        return "pytket.extensions.qiskit.backends.aer.AerBackend"

    @staticmethod
    def n_shots_required() -> bool:
        return True

    def is_nexus_simulator(self) -> bool:
        return True


class AerStateConfig(BaseBackendConfig):
    """
    * Extension library for backend: pytket-qiskit.
    * Backend location: pytket.extensions.qiskit.backends.aer.AerStateBackend.
    """

    type: Literal["AerStateConfig"] = "AerStateConfig"
    n_qubits: PositiveInt = 40

    @staticmethod
    def description() -> str:
        return "Qiskit Aer statevector simulator."

    @staticmethod
    def fully_qualified_name() -> str:
        return "pytket.extensions.qiskit.backends.aer.AerStateBackend"

    @staticmethod
    def n_shots_required() -> bool:
        return False

    def is_nexus_simulator(self) -> bool:
        return True


class AerUnitaryConfig(BaseBackendConfig):
    """
    * Extension library for backend: pytket-qiskit.
    * Backend location: pytket.extensions.qiskit.backends.aer.AerUnitaryBackend.
    """

    type: Literal["AerUnitaryConfig"] = "AerUnitaryConfig"
    n_qubits: PositiveInt = 40

    @staticmethod
    def description() -> str:
        return "Qiskit Aer unitary simulator."

    @staticmethod
    def fully_qualified_name() -> str:
        return "pytket.extensions.qiskit.backends.aer.AerUnitaryBackend"

    @staticmethod
    def n_shots_required() -> bool:
        return False

    def is_nexus_simulator(self) -> bool:
        return True


class BraketConfig(BaseBackendConfig):
    """
    * Extension library for backend: pytket-braket.
    * Backend location: pytket.extensions.braket.backends.braket.BraketBackend.

    The parameters other than "local" only apply if local=False.
    """

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

    @staticmethod
    def description() -> str:
        return "Runs circuits on quantum devices and simulators using Amazon's Braket service."

    @staticmethod
    def fully_qualified_name() -> str:
        return "pytket.extensions.braket.backends.braket.BraketBackend"

    @staticmethod
    def n_shots_required() -> bool:
        """This depends on the device asked for - if it has “Sample” as a supported result type,
        then it expects n_shots to be set, so will raise ValueError. But other cases do not need
        n_shots to be set."""
        return False

    def is_nexus_simulator(self) -> bool:
        """This is a local simulator if local == True; otherwise, we use remote devices."""
        return self.local

    @staticmethod
    def requires_credentials() -> bool:
        return True

    @staticmethod
    def provider_regions() -> Dict[str, str]:
        """Hard-coded regions for each braket provider.

        Physical quantum devices are only available in one AWS region each:
        https://docs.aws.amazon.com/braket/latest/developerguide/braket-regions.html

        Two quantum simulators are available in any region where Amazon Braket is available:
        https://docs.aws.amazon.com/braket/latest/developerguide/braket-devices.html
        and a third (TN1) is available in us-west-2 and us-east-1.

        The ARN for all the simulators does not need a region name.
        """
        return {
            "amazon": "",  # i.e. AWS quantum-simulators
            "d-wave": "us-west-2",
            "ionq": "us-east-1",
            "oqc": "eu-west-2",
            "rigetti": "us-west-1",
            "xanadu": "us-east-1",
        }


class QuantinuumCompilerOptions(BaseModel):
    """Class for Quantinuum Compiler Options.

    Intentionally allows extra unknown flags to be defined.
    """

    model_config = ConfigDict(extra="allow", frozen=True)

    @model_validator(mode="before")
    def check_field_values_are_supported_types(  # pylint: disable=no-self-argument,
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check that compiler option values are only of types that our protobuf class also
        supports. Currently, this is str, bool and int."""
        for key in values:
            assert isinstance(
                values[key], (str, int, bool)
            ), "Compiler options must be str, bool or int"
        return values


class QuantinuumConfig(BaseBackendConfig):
    """
    * Extension library for backend: pytket-quantinuum.
    * Backend location: pytket.extensions.quantinuum.backends.quantinuum.QuantinuumBackend.
    """

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
    postprocess: bool = False
    noisy_simulation: bool = True
    user_group: Optional[str] = None
    max_batch_cost: int = 2000
    compiler_options: Optional[QuantinuumCompilerOptions] = None
    no_opt: bool = False
    allow_2q_gate_rebase: bool = False
    leakage_detection: bool = False
    simplify_initial: bool = False

    @staticmethod
    def description() -> str:
        return "Runs circuits on Quantinuum's quantum devices and simulators."

    @staticmethod
    def fully_qualified_name() -> str:
        return "pytket.extensions.quantinuum.backends.quantinuum.QuantinuumBackend"

    @staticmethod
    def n_shots_required() -> bool:
        return True

    @staticmethod
    def qasm_header() -> str:
        """Quantinuum has its own QASM header."""
        return "hqslib1"

    def is_nexus_simulator(self) -> bool:
        """Will be treated as a Nexus simulator if the device_name is in the
        hardcoded known simulator names."""
        if self.device_name in self.known_nexus_simulators():
            return True
        return False

    @staticmethod
    def requires_credentials() -> bool:
        return True

    @staticmethod
    def known_device_names() -> List[str]:
        """Lists known device names for Quantinuum"""
        return [
            "H1-1",
            "H2-1",
            "H1-1E",
            "H2-1E",
            "H1-1LE",
            "H2-1LE",
            "H1-1SC",
            "H2-1SC",
        ]

    @staticmethod
    def known_nexus_simulators() -> List[str]:
        """Lists known nexus simulator names for Quantinuum"""
        return [
            "H1-1LE",
            "H2-1LE",
        ]


class IBMQConfig(BaseBackendConfig):
    """
    * Extension library for backend: pytket-qiskit.
    * Backend location: pytket.extensions.qiskit.backends.ibm.IBMQBackend.
    """

    type: Literal["IBMQConfig"] = "IBMQConfig"
    backend_name: str  # The quantum computer or simulator to run a circuit on.
    hub: str
    group: str
    project: str
    monitor: bool = False
    # Parameters below are kwargs used in IBMQBackend.process_circuits().
    postprocess: bool = False
    simplify_initial: bool = False

    @staticmethod
    def description() -> str:
        return "Runs circuits on IBM's quantum devices and simulators."

    @staticmethod
    def fully_qualified_name() -> str:
        return "pytket.extensions.qiskit.backends.ibm.IBMQBackend"

    @staticmethod
    def n_shots_required() -> bool:
        return True

    def is_nexus_simulator(self) -> bool:
        return False

    @staticmethod
    def requires_credentials() -> bool:
        return True

    @staticmethod
    def result_availability() -> ResultAvailability:
        return ResultAvailability.BATCH


class IBMQEmulatorConfig(BaseBackendConfig):
    """
    * Extension library for backend: pytket-qiskit.
    * Backend location: pytket.extensions.qiskit.backends.ibmq_emulator.IBMQEmulatorBackend.
    """

    type: Literal["IBMQEmulatorConfig"] = "IBMQEmulatorConfig"
    backend_name: str  # The quantum computer to emulate.
    hub: str
    group: str
    project: str
    # Parameters below are kwargs used in IBMQBackend.process_circuits().
    seed: Optional[int] = None
    postprocess: bool = False

    @staticmethod
    def description() -> str:
        return (
            "Runs circuits on the IBM-hosted simulator ibmq_qasm_simulator, using the noise model "
            "of a specific IBM quantum device."
        )

    @staticmethod
    def fully_qualified_name() -> str:
        return "pytket.extensions.qiskit.backends.ibmq_emulator.IBMQEmulatorBackend"

    @staticmethod
    def n_shots_required() -> bool:
        return True

    def is_nexus_simulator(self) -> bool:
        return False

    @staticmethod
    def requires_credentials() -> bool:
        return True


class ProjectQConfig(BaseBackendConfig):
    """
    * Extension library for backend: pytket-projectq.
    * Backend location: pytket.extensions.projectq.backends.projectq_backend.ProjectQBackend.
    """

    type: Literal["ProjectQConfig"] = "ProjectQConfig"

    @staticmethod
    def description() -> str:
        return "ProjectQ statevector simulator."

    @staticmethod
    def fully_qualified_name() -> str:
        return "pytket.extensions.projectq.backends.projectq_backend.ProjectQBackend"

    @staticmethod
    def n_shots_required() -> bool:
        """If there are no OpType.Measure gates and n_shots is set, we can use it;
        otherwise look for the state. n_shots is definitely optional for the ProjectQBackend.
        """
        return False

    def is_nexus_simulator(self) -> bool:
        return True


class QulacsConfig(BaseBackendConfig):
    """
    * Extension library for backend: pytket-qulacs.
    * Backend location: pytket.extensions.qulacs.backends.qulacs_backend.QulacsBackend.
    """

    type: Literal["QulacsConfig"] = "QulacsConfig"
    result_type: str = "state_vector"
    # Parameters below are kwargs used in AerBackend.process_circuits().
    seed: Optional[int] = None

    @staticmethod
    def description() -> str:
        return "Qulacs simulator."

    @staticmethod
    def fully_qualified_name() -> str:
        return "pytket.extensions.qulacs.backends.qulacs_backend.QulacsBackend"

    @staticmethod
    def n_shots_required() -> bool:
        """If n_shots isn't supplied, we will just get the calculated state."""
        return False

    def is_nexus_simulator(self) -> bool:
        return True


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
