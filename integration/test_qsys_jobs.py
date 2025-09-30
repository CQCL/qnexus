"""Tests related to running jobs against QSys devices."""

from typing import Any, Callable, ContextManager, cast

import pytest
from guppylang import guppy
from guppylang.std.builtins import result
from guppylang.std.quantum import cx, h, measure, qubit, x, z
from hugr.qsystem.result import QsysResult
from pytket.backends.backendinfo import BackendInfo
from quantinuum_schemas.models.backend_config import BasicEmulatorConfig

import qnexus as qnx
from qnexus.models.references import (
    ExecutionResultRef,
    HUGRRef,
    ProjectRef,
    ResultVersions,
)


def prepare_teleportation() -> Any:
    """Prepares the teleportation circuit."""

    @guppy
    def bell() -> tuple[qubit, qubit]:
        """Constructs a bell state."""
        q1, q2 = qubit(), qubit()
        h(q1)
        cx(q1, q2)
        return q1, q2

    @guppy
    def main() -> None:
        src = qubit()
        x(src)
        alice, bob = bell()

        cx(src, alice)
        h(src)
        if measure(alice):
            x(bob)
        if measure(src):
            z(bob)

        result("teleported", measure(bob))

    main.check()
    return main.compile()


@pytest.mark.skip(reason="Skipped while Selene is disabled for refactoring work.")
def test_guppy_execution(
    test_case_name: str,
    create_project: Callable[[str], ContextManager[ProjectRef]],
) -> None:
    """Test the execution of a guppy program
    on a next-generation QSys device."""

    with create_project(f"project for {test_case_name}") as project_ref:
        n_qubits = 3
        n_shots = 10

        hugr_ref = qnx.hugr.upload(
            hugr_package=prepare_teleportation(),
            name=f"hugr for {test_case_name}",
            project=project_ref,
        )

        job_ref = qnx.start_execute_job(
            programs=[hugr_ref],
            n_shots=[n_shots],
            backend_config=BasicEmulatorConfig(n_qubits=n_qubits),
            project=project_ref,
            name=f"basicemulator selene job for {test_case_name}",
        )

        qnx.jobs.wait_for(job_ref)

        results = qnx.jobs.results(job_ref)

        assert len(results) == 1
        result_ref = results[0]

        assert isinstance(result_ref, ExecutionResultRef)
        assert isinstance(result_ref.download_backend_info(), BackendInfo)
        assert isinstance(result_ref.get_input(), HUGRRef)

        assert result_ref.get_input().id == hugr_ref.id

        qsys_result = cast(QsysResult, result_ref.download_result())
        assert len(qsys_result.results) == n_shots
        assert qsys_result.results[0].entries[0][0] == "teleported"
        assert qsys_result.results[0].entries[0][1] == 1

        # check some QsysResults functionality
        assert len(qsys_result.collated_counts().items()) > 0

        # Assert we can get the same result for v4 results
        v4_qsys_result = cast(
            QsysResult, result_ref.download_result(version=ResultVersions.RAW)
        )
        assert len(v4_qsys_result.results) == n_shots
        assert v4_qsys_result.results[0].entries[0][0] == "USER:BOOL:teleported"
        assert v4_qsys_result.results[0].entries[0][1] == 1

        # This doesn't seem to work with v4 results, thinks everything is going to be a bit.
        # assert len(qsys_result.collated_counts().items()) > 0
