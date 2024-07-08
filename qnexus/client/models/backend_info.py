"""Serialization classes for pytket BackendInfo."""

# pylint: disable=too-many-branches, too-many-statements, too-many-locals, too-many-instance-attributes
# pylint: disable=import-outside-toplevel, no-name-in-module

from __future__ import annotations

from typing import Any, NewType, Optional, Union

from pydantic import BaseModel, Field
from pytket.architecture import Architecture, FullyConnected
from pytket.backends.backendinfo import BackendInfo
from pytket.circuit import OpType
from pytket.unit_id import Node, Qubit

Register = NewType("Register", tuple[str, tuple[int, ...]])


def register_from_pytket_node(node: Node | Qubit) -> Register:
    """Convert a pytket Node object to a nexus-dataclasses Register object."""
    args = node.to_list()
    return Register((args[0], tuple(args[1])))


def register_to_pytket_node(register: Register) -> Node:
    """Convert a pytket Node object from a nexus-dataclasses Register object."""

    return Node.from_list(list(register))


class StoredNode(BaseModel):
    """Node in a quantum device's connectivity graph, along with its error rates."""

    unitid: Register
    average_error: Optional[float] = None
    readout_error: Optional[float] = None
    gate_errors: dict[str, float]
    # Give default values for migration purpose
    zero_state_readout_error: Optional[float] = Field(default=None)
    one_state_readout_error: Optional[float] = Field(default=None)


class StoredEdge(BaseModel):
    """Edge in a quantum device's connectivity graph, along with its error rates."""

    unitid_from: Register
    unitid_to: Register
    average_error: Optional[float] = None
    gate_errors: dict[str, float]


class StoredDevice(BaseModel):
    """Nodes and edges that together make up a quantum device's connectivity graph.

    Based on pytket.architecture.Architecture."""

    nodes: list[StoredNode]
    edges: list[StoredEdge]

    n_nodes: Optional[int] = 0
    fully_connected: Optional[bool] = None


class StoredBackendInfo(BaseModel):
    """Equivalent of pytket's BackendInfo, but in a form that it can be converted to and from JSON
    for storage in the Nexus database."""

    name: str
    device_name: Optional[str] = None
    version: str
    device: StoredDevice
    gate_set: list[str]
    n_cl_reg: Optional[int] = None
    supports_fast_feedforward: bool
    supports_reset: bool
    supports_midcircuit_measurement: bool
    misc: dict[str, Any] = Field(default={})

    def to_pytket_backend_info(self) -> BackendInfo:
        """Reconstruct a pytket BackendInfo from the StoredBackendInfo instance."""

        stored_nodes = self.device.nodes
        stored_edges = self.device.edges
        architecture_edge_list = []

        # BackendInfo dictionary attributes are initialised as None,
        # Then dictionaries are built when they are to be populated.
        # This is to satisfy type-checking as well as BackendInfo expectations/tests.

        averaged_node_gate_errors = None
        averaged_readout_errors = None
        all_node_gate_errors = None
        all_readout_errors = None

        for stored_node in stored_nodes:
            # Create node from register
            new_pytket_node = register_to_pytket_node(stored_node.unitid)

            # Build average node gate errors
            if stored_node.average_error is not None:
                if averaged_node_gate_errors is None:
                    averaged_node_gate_errors = {}
                averaged_node_gate_errors[new_pytket_node] = stored_node.average_error
            # Build average readout errors
            if stored_node.readout_error is not None:
                if averaged_readout_errors is None:
                    averaged_readout_errors = {}
                averaged_readout_errors[new_pytket_node] = stored_node.readout_error

            if stored_node.gate_errors:
                node_gate_errors = {
                    getattr(OpType, optype_name): error
                    for optype_name, error in stored_node.gate_errors.items()
                }
                if all_node_gate_errors is None:
                    all_node_gate_errors = {}
                all_node_gate_errors[new_pytket_node] = node_gate_errors

            # Add stored_node readout errors to all_readout_errors
            stored_zero_state_readout_error = stored_node.zero_state_readout_error
            stored_one_state_readout_error = stored_node.one_state_readout_error
            if (
                stored_zero_state_readout_error is not None
                and stored_one_state_readout_error is not None
            ):
                if all_readout_errors is None:
                    all_readout_errors = {}
                readout_errors = [
                    [
                        1.0 - stored_zero_state_readout_error,
                        stored_zero_state_readout_error,
                    ],
                    [
                        stored_one_state_readout_error,
                        1.0 - stored_one_state_readout_error,
                    ],
                ]
                all_readout_errors[new_pytket_node] = readout_errors

        # Build all_edge_gate_errors and averaged_edge_gate_errors from stored_edges
        all_edge_gate_errors = None
        averaged_edge_gate_errors = None

        for stored_edge in stored_edges:
            node_from = register_to_pytket_node(stored_edge.unitid_from)
            node_to = register_to_pytket_node(stored_edge.unitid_to)

            new_edge_tuple = (node_from, node_to)
            architecture_edge_list.append(new_edge_tuple)

            if stored_edge.average_error is not None:
                if averaged_edge_gate_errors is None:
                    averaged_edge_gate_errors = {}
                averaged_edge_gate_errors[
                    (node_from, node_to)
                ] = stored_edge.average_error
            if stored_edge.gate_errors:
                edge_gate_errors = {
                    getattr(OpType, optype_name): error
                    for optype_name, error in stored_edge.gate_errors.items()
                }
                if all_edge_gate_errors is None:
                    all_edge_gate_errors = {}
                all_edge_gate_errors[(node_from, node_to)] = edge_gate_errors

        architecture: Union[Architecture, FullyConnected] = (
            FullyConnected(
                self.device.n_nodes
                if self.device.n_nodes is not None
                else len(self.device.nodes)
            )
            if self.device.fully_connected
            else Architecture(architecture_edge_list)
        )
        gate_set = {getattr(OpType, gate) for gate in self.gate_set}

        return BackendInfo(
            name=self.name,
            device_name=self.device_name,
            version=self.version,
            architecture=architecture,
            gate_set=gate_set,
            n_cl_reg=self.n_cl_reg,
            supports_fast_feedforward=self.supports_fast_feedforward,
            supports_reset=self.supports_reset,
            supports_midcircuit_measurement=self.supports_midcircuit_measurement,
            all_node_gate_errors=all_node_gate_errors,
            all_edge_gate_errors=all_edge_gate_errors,
            all_readout_errors=all_readout_errors,
            averaged_node_gate_errors=averaged_node_gate_errors,
            averaged_edge_gate_errors=averaged_edge_gate_errors,
            averaged_readout_errors=averaged_readout_errors,
            misc=self.misc,
        )
