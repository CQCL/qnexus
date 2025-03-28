"""Tests related to running jobs against QSys devices."""
import os
from datetime import datetime
from typing import cast

import pytest
from guppylang import guppy
from guppylang.std.builtins import result
from guppylang.std.quantum import cx, h, measure, qubit, x, z
from pytket.backends.backendinfo import BackendInfo
from quantinuum_schemas.models.result import QSysResult

import qnexus as qnx

QSYS_QA_DEVICE_NAME = os.environ["NEXUS_QA_QSYS_DEVICE"]
N_SHOTS = 10


@pytest.mark.skip(
    "Skipping QSys tests until we have a consistent test device to target"
)
def prepare_teleportation():
    """Prepares the teleportation circuit."""

    @guppy
    def bell() -> tuple[qubit, qubit]:
        # pylint: disable=too-many-function-args
        """Constructs a bell state."""
        q1, q2 = qubit(), qubit()
        h(q1)
        cx(q1, q2)
        return q1, q2

    @guppy
    def main() -> None:
        # pylint: disable=too-many-function-args
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

    return main.compile()


def test_guppy_execution(
    _authenticated_nexus: None,
    qa_project_name: str,
) -> None:
    """Test the execution of a guppy program
    on a next-generation QSys device."""

    # Compile the guppy program
    compiled_module = prepare_teleportation()
    hugr_package = compiled_module.to_executable_package().package

    project_ref = qnx.projects.get_or_create(name=qa_project_name)

    hugr_ref = qnx.hugr.upload(
        hugr_package=hugr_package,
        name="QA testing teleportation program",
        project=project_ref,
    )

    job_ref = qnx.start_execute_job(
        circuits=[hugr_ref],
        n_shots=[N_SHOTS],
        backend_config=qnx.QuantinuumConfig(device_name=QSYS_QA_DEVICE_NAME),
        project=project_ref,
        name=f"QA Test QSys job from {datetime.now()}",
    )

    # QSYS QA device might not always be online, so we might expect failures for now
    qnx.jobs.wait_for(job_ref)

    results = qnx.jobs.results(job_ref)

    assert len(results) == 1
    result_ref = results[0]

    assert isinstance(result_ref.download_backend_info(), BackendInfo)
    assert isinstance(result_ref.get_input(), hugr_package)

    assert result_ref.get_input().id == hugr_ref.id

    qsys_result = cast(QSysResult, result_ref.download_result())
    assert len(qsys_result) == N_SHOTS
    assert qsys_result[0][0][0] == "teleported"
    assert qsys_result[0][0][1] == 0
