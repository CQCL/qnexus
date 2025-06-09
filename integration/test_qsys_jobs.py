"""Tests related to running jobs against QSys devices."""

from datetime import datetime
from typing import Any, cast

from guppylang import guppy  # type: ignore
from guppylang.std.builtins import result
from guppylang.std.quantum import cx, h, measure, qubit, x, z
from hugr.qsystem.result import QsysResult
from pytket.backends.backendinfo import BackendInfo
from quantinuum_schemas.models.backend_config import SeleneQuestConfig

import qnexus as qnx
from qnexus.models.references import HUGRRef


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

        result("teleported", measure(bob))  # type: ignore

    return main.compile()  # type: ignore


def test_guppy_execution(
    _authenticated_nexus: None,
    qa_project_name: str,
) -> None:
    """Test the execution of a guppy program
    on a next-generation QSys device."""

    n_qubits = 3
    n_shots = 10

    project_ref = qnx.projects.get_or_create(name=qa_project_name)

    hugr_ref = qnx.hugr.upload(
        hugr_package=prepare_teleportation(),
        name="QA testing teleportation program",
        project=project_ref,
    )

    job_ref = qnx.start_execute_job(
        programs=[hugr_ref],
        n_shots=[n_shots],
        backend_config=SeleneQuestConfig(n_qubits=n_qubits),
        project=project_ref,
        name=f"QA Test QSys job from {datetime.now()}",
    )

    qnx.jobs.wait_for(job_ref)

    results = qnx.jobs.results(job_ref)

    assert len(results) == 1
    result_ref = results[0]

    assert isinstance(result_ref.download_backend_info(), BackendInfo)
    assert isinstance(result_ref.get_input(), HUGRRef)

    assert result_ref.get_input().id == hugr_ref.id

    qsys_result = cast(QsysResult, result_ref.download_result())
    assert len(qsys_result.results) == n_shots
    assert qsys_result.results[0].entries[0][0] == "teleported"
    assert qsys_result.results[0].entries[0][1] == 1

    # check some QsysResults functionality
    assert len(qsys_result.collated_counts().items()) > 0
