"""Validation classes for Aer noise models."""
from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, List, Literal, Optional, Tuple, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

import qnexus.exceptions as qnx_exc
from qnexus.models.backend_info import Register
from qnexus.models.backend_info import register_from_pytket_node as reg_from_qb
from qnexus.models.backend_info import register_to_pytket_node as reg_to_qb

if TYPE_CHECKING:
    from pytket.extensions.qiskit.backends.crosstalk_model import (
        CrosstalkParams as PytketCrosstalkParams,
    )
    from qiskit.circuit import QuantumCircuit  # type: ignore
    from qiskit_aer.noise.noise_model import NoiseModel  # type: ignore


class QiskitBasicInstruction(BaseModel):
    """Validation model for qiskit instructions without params."""

    name: Literal["id", "x", "y", "z", "reset"]
    qubits: List[int]


class QiskitPauliInstruction(BaseModel):
    """Validation model for qiskit pauli string instructions."""

    name: Literal["pauli"] = "pauli"
    params: List[str]
    qubits: List[int]


class QiskitKrausInstruction(BaseModel):
    """Validation model for qiskit kraus operator instructions."""

    name: Literal["kraus"] = "kraus"
    # List of matrices of complex numbers
    params: List[List[List[List[float]]]]
    qubits: List[int]


QiskitInstruction = Annotated[
    Union[
        QiskitBasicInstruction,
        QiskitPauliInstruction,
        QiskitKrausInstruction,
    ],
    Field(discriminator="name"),
]


class AerQuantumError(BaseModel):
    """Validation model for qiskit-aer's QuantumError class."""

    type: Literal["qerror"] = "qerror"
    id: str = Field(default_factory=lambda: uuid4().hex)
    operations: Optional[List[str]] = Field(default_factory=list)
    instructions: List[List[QiskitInstruction]]
    probabilities: List[float] = Field(min_length=1)
    gate_qubits: List[List[int]]

    @field_validator("id")
    def validate_id(cls, value: Any) -> str:  # pylint: disable=no-self-argument
        """Ensure id is a v4 UUID in hex format."""
        return UUID(value, version=4).hex

    # pylint: disable=too-many-locals
    def noise_ops(self) -> List[Tuple["QuantumCircuit", float]]:
        """Return a list of qiskit Circuit and probability tuples for use in QuantumError."""
        # pylint: disable=import-outside-toplevel
        try:
            # fmt: off
            from qiskit.circuit import QuantumCircuit
            from qiskit.circuit.library import IGate  # type: ignore
            from qiskit.circuit.library import Reset  # type: ignore
            from qiskit.circuit.library import PauliGate, XGate, YGate, ZGate
            from qiskit.quantum_info.operators import Kraus  # type: ignore

            # fmt: on
        except ImportError as err:
            raise qnx_exc.OptionalDependencyError(
                "qiskit-aer is not installed. "
                "Please install qiskit-aer before calling noise_ops "
                "'pip install 'qiskit-aer''"
            ) from err

        noise_ops = []
        for instruction, probability in zip(self.instructions, self.probabilities):
            max_qubits = max(max(op.qubits) for op in instruction) + 1
            circuit = QuantumCircuit(max_qubits)
            for operation in instruction:
                if isinstance(operation, QiskitBasicInstruction):
                    if operation.name == "id":
                        circuit.append(IGate(), qargs=operation.qubits)
                    if operation.name == "x":
                        circuit.append(XGate(), qargs=operation.qubits)
                    if operation.name == "y":
                        circuit.append(YGate(), qargs=operation.qubits)
                    if operation.name == "z":
                        circuit.append(ZGate(), qargs=operation.qubits)
                    if operation.name == "reset":
                        circuit.append(Reset(), qargs=operation.qubits)
                if isinstance(operation, QiskitPauliInstruction):
                    circuit.append(
                        PauliGate(
                            label=operation.params[0],
                        ),
                        qargs=operation.qubits,
                    )
                if isinstance(operation, QiskitKrausInstruction):
                    data = [
                        [
                            [complex(array[0], array[1]) for array in matrix]
                            for matrix in param
                        ]
                        for param in operation.params
                    ]

                    circuit.append(
                        Kraus(data=data).to_instruction(), qargs=operation.qubits
                    )

            noise_ops.append((circuit, probability))

        return noise_ops


class AerReadoutError(BaseModel):
    """Validation model for qiskit-aer's ReadoutError class."""

    type: Literal["roerror"] = "roerror"
    operations: Optional[List[str]] = Field(default_factory=lambda: ["measure"])
    probabilities: List[List[float]] = Field(min_length=1)
    gate_qubits: List[List[int]]


Error = Annotated[Union[AerQuantumError, AerReadoutError], Field(discriminator="type")]


class AerNoiseModel(BaseModel):
    """Validation model for qiskit-aer's NoiseModel class."""

    errors: List[Error]

    def to_native(self) -> NoiseModel:
        """Convert to a qiskit native NoiseModel."""
        # pylint: disable=import-outside-toplevel
        try:
            from qiskit_aer.noise.noise_model import (
                NoiseModel,
                QuantumError,
                ReadoutError,
            )
        except ImportError as err:
            raise ImportError(
                "qiskit-aer is not installed. "
                "Please install qiskit-aer before calling `to_native` "
                "'pip install 'qiskit-aer''"
            ) from err

        noise_model = NoiseModel()
        for error in self.errors:
            if isinstance(error, AerQuantumError):
                for applied_qubits in error.gate_qubits:
                    qerror = QuantumError(noise_ops=error.noise_ops())
                    # pylint: disable=protected-access
                    # We can't set the id on a QuantumError usually.
                    qerror._id = error.id
                    # pylint: disable=protected-access
                    # The QuantumError constructor re-scales probabilities
                    # which we want to avoid for serialization.
                    qerror._probs = error.probabilities
                    noise_model.add_quantum_error(
                        error=qerror,
                        instructions=error.operations,
                        qubits=applied_qubits,
                    )
            if isinstance(error, AerReadoutError):
                for applied_qubits in error.gate_qubits:
                    noise_model.add_readout_error(
                        error=ReadoutError(probabilities=error.probabilities),
                        qubits=applied_qubits,
                    )

        return noise_model


class CrosstalkParams(BaseModel):
    """
    Based on pytket-qiskit's CrosstalkParams model.
    Stores various parameters for modelling crosstalk noise.
    """

    zz_crosstalks: dict[Tuple[Register, Register], float]
    single_q_phase_errors: dict[Register, float]
    two_q_induced_phase_errors: dict[Tuple[Register, Register], Tuple[Register, float]]
    non_markovian_noise: list[Tuple[Register, float, float]]
    virtual_z: bool
    N: float
    gate_times: dict[Tuple[str, Tuple[Register, ...]], float]
    phase_damping_error: dict[Register, float]
    amplitude_damping_error: dict[Register, float]

    @classmethod
    def from_pytket_crosstalk_params(
        cls,
        crosstalk_params: PytketCrosstalkParams,
    ) -> "CrosstalkParams":
        """Construct a CrosstalkParams from a pytket CrosstalkParams."""
        return CrosstalkParams(
            zz_crosstalks={
                (
                    reg_from_qb(qbs[0]),
                    reg_from_qb(qbs[1]),
                ): error
                for qbs, error in crosstalk_params.zz_crosstalks.items()
            },
            single_q_phase_errors={
                reg_from_qb(qb): error
                for qb, error in crosstalk_params.single_q_phase_errors.items()
            },
            two_q_induced_phase_errors={
                (reg_from_qb(qbs[0]), reg_from_qb(qbs[1])): (
                    reg_from_qb(qb_plus_phase[0]),
                    qb_plus_phase[1],
                )
                for qbs, qb_plus_phase in crosstalk_params.two_q_induced_phase_errors.items()
            },
            non_markovian_noise=[
                (
                    reg_from_qb(noise_entry[0]),
                    noise_entry[1],
                    noise_entry[2],
                )
                for noise_entry in crosstalk_params.non_markovian_noise
            ],
            virtual_z=crosstalk_params.virtual_z,
            N=crosstalk_params.N,
            gate_times={
                (
                    gate[0].name,
                    tuple((reg_from_qb(qb) for qb in gate[1])),
                ): time_info
                for gate, time_info in crosstalk_params.gate_times.items()
            },
            phase_damping_error={
                reg_from_qb(qb): error
                for qb, error in crosstalk_params.phase_damping_error.items()
            },
            amplitude_damping_error={
                reg_from_qb(qb): error
                for qb, error in crosstalk_params.amplitude_damping_error.items()
            },
        )

    def to_pytket_crosstalk_params(self) -> PytketCrosstalkParams:
        """Construct a pytket CrosstalkParams from a CrosstalkParams."""
        try:
            # pylint: disable=import-outside-toplevel
            from pytket.circuit import OpType
            from pytket.extensions.qiskit.backends.crosstalk_model import (
                CrosstalkParams as PytketCrosstalkParams,
            )
        except ImportError as err:
            raise qnx_exc.OptionalDependencyError from err
        return PytketCrosstalkParams(
            zz_crosstalks={
                (reg_to_qb(regs[0]), reg_to_qb(regs[1])): error
                for regs, error in self.zz_crosstalks.items()
            },
            single_q_phase_errors={
                reg_to_qb(reg): error
                for reg, error in self.single_q_phase_errors.items()
            },
            two_q_induced_phase_errors={
                (reg_to_qb(regs[0]), reg_to_qb(regs[1])): (
                    reg_to_qb(qb_plus_phase[0]),
                    qb_plus_phase[1],
                )
                for regs, qb_plus_phase in self.two_q_induced_phase_errors.items()
            },
            non_markovian_noise=[
                (reg_to_qb(noise_entry[0]), noise_entry[1], noise_entry[2])
                for noise_entry in self.non_markovian_noise
            ],
            virtual_z=self.virtual_z,
            N=self.N,
            gate_times={
                (
                    OpType.from_name(gate[0]),
                    tuple((reg_to_qb(r) for r in gate[1])),
                ): time_info
                for gate, time_info in self.gate_times.items()
            },
            phase_damping_error={
                reg_to_qb(reg): error for reg, error in self.phase_damping_error.items()
            },
            amplitude_damping_error={
                reg_to_qb(reg): error
                for reg, error in self.amplitude_damping_error.items()
            },
        )
