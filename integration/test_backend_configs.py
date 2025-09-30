"""Tests that we can use all available backend configs."""

from typing import Callable, ContextManager

from pytket.backends.backendresult import BackendResult
from pytket.circuit import Circuit

import qnexus as qnx
from qnexus.models.job_status import JobStatusEnum
from qnexus.models.references import (
    CompilationResultRef,
    ExecutionResultRef,
    ProjectRef,
)

CONFIGS_REQUIRE_NO_MEASURE = [qnx.AerUnitaryConfig]
CONFIGS_NOT_TO_EXECUTE = [
    # We won't execute for these configs as they run on quantum hardware
    qnx.IBMQConfig
]


def test_basic_backend_config_usage(
    backend_config: qnx.BackendConfig,
    create_project: Callable[[str], ContextManager[ProjectRef]],
    test_case_name: str,
) -> None:
    """Test basic functionality of supported BackendConfigs."""

    with create_project(f"project for {test_case_name}") as project_ref:
        my_circ = Circuit(2, 2).H(0).CX(0, 1)

        if backend_config.__class__ not in CONFIGS_REQUIRE_NO_MEASURE:
            my_circ.measure_all()

        my_circ = qnx.circuits.upload(
            circuit=my_circ,
            name=f"circuit for {test_case_name}",
            description="This can be safely deleted.",
            project=project_ref,
        )

        compile_job_ref = qnx.start_compile_job(
            programs=[my_circ],
            name=f"compile job for {test_case_name}",
            optimisation_level=2,
            backend_config=backend_config,
            project=project_ref,
        )

        qnx.jobs.wait_for(compile_job_ref)

        # Check the backend config as stored in Nexus matches the one specified
        # QuantinuumConfig noisy_simulation flag getting reset in Nexus
        assert backend_config.model_dump(exclude={"noisy_simulation"}) == qnx.jobs.get(
            id=compile_job_ref.id
        ).backend_config.model_dump(exclude={"noisy_simulation"})

        execute_job_ref = qnx.start_execute_job(
            programs=[
                item.get_output()
                for item in qnx.jobs.results(compile_job_ref)
                if isinstance(item, CompilationResultRef)
            ],
            name=f"execute job for {test_case_name}",
            n_shots=[100],
            backend_config=backend_config,
            project=project_ref,
        )

        if backend_config.__class__ in CONFIGS_NOT_TO_EXECUTE:
            qnx.jobs.wait_for(execute_job_ref, wait_for_status=JobStatusEnum.SUBMITTED)
            qnx.jobs.cancel(execute_job_ref)
            qnx.jobs.wait_for(execute_job_ref, wait_for_status=JobStatusEnum.CANCELLED)
            return

        qnx.jobs.wait_for(execute_job_ref)

        execute_job_result_refs = qnx.jobs.results(execute_job_ref)

        for result_ref in execute_job_result_refs:
            assert isinstance(result_ref, ExecutionResultRef)
            assert isinstance(result_ref.download_result(), BackendResult)
