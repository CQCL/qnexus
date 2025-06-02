"""Tests that we can use all available backend configs."""

from datetime import datetime

from pytket.backends.backendresult import BackendResult
from pytket.backends.status import StatusEnum
from pytket.circuit import Circuit

import qnexus as qnx

CONFIGS_REQUIRE_NO_MEASURE = [qnx.AerUnitaryConfig]
CONFIGS_NOT_TO_EXECUTE = [
    # We won't execute for these configs as they run on quantum hardware
    qnx.IBMQConfig
]


def test_basic_backend_config_usage(
    _authenticated_nexus: None,
    backend_config: qnx.BackendConfig,
    qa_project_name: str,
) -> None:
    """Test basic functionality of supported BackendConfigs."""

    project_ref = qnx.projects.get(name_like=qa_project_name)

    my_circ = Circuit(2, 2).H(0).CX(0, 1)

    if backend_config.__class__ not in CONFIGS_REQUIRE_NO_MEASURE:
        my_circ.measure_all()

    my_circ = qnx.circuits.upload(
        circuit=my_circ,
        name=f"QA BackendConfig circuit {backend_config.__class__.__name__}_{datetime.now()}",
        description=f"This can be safely deleted. Test Run: {datetime.now()}",
        project=project_ref,
    )

    compile_job_ref = qnx.start_compile_job(
        programs=[my_circ],
        name=f"QA BackendConfig compile job {backend_config.__class__.__name__}_{datetime.now()}",
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
        programs=[item.get_output() for item in qnx.jobs.results(compile_job_ref)],
        name=f"Execute {backend_config.__class__.__name__}_{datetime.now()}",
        n_shots=[100],
        backend_config=backend_config,
        project=project_ref,
    )

    if backend_config.__class__ in CONFIGS_NOT_TO_EXECUTE:
        qnx.jobs.wait_for(execute_job_ref, wait_for_status=StatusEnum.QUEUED)
        qnx.jobs.cancel(execute_job_ref)
        qnx.jobs.wait_for(execute_job_ref, wait_for_status=StatusEnum.CANCELLED)
        return

    qnx.jobs.wait_for(execute_job_ref)

    execute_job_result_refs = qnx.jobs.results(execute_job_ref)

    for result_ref in execute_job_result_refs:
        assert isinstance(result_ref.download_result(), BackendResult)
