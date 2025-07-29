"""Test basic functionality relating to the gpu_decoder_config."""

from datetime import datetime
from pathlib import Path

import pandas as pd

import qnexus as qnx
from qnexus.models.references import GpuDecoderConfigRef


def test_gpu_decoder_config_download(
    _authenticated_nexus: None,
    qa_project_name: str,
) -> None:
    """Test that valid GPU decoder config can be extracted from an uploaded GPU decoder config."""

    my_proj = qnx.projects.get(name_like=qa_project_name)

    gpu_decoder_config_path = Path(
        "examples/basics/data/gpu_decoder_config.yaml"
    ).resolve()
    with open(gpu_decoder_config_path) as fp:
        gpu_decoder_config = fp.read()

    qa_gpu_decoder_config_name_fixture = (
        f"qnexus_integration_test_gpu_decoder_config_{datetime.now()}"
    )

    qnx.gpu_decoder_configs.upload(
        gpu_decoder_config=gpu_decoder_config,
        name=qa_gpu_decoder_config_name_fixture,
        project=my_proj,
    )

    gpu_decoder_config_ref = qnx.gpu_decoder_configs.get(
        name_like=qa_gpu_decoder_config_name_fixture
    )
    assert isinstance(gpu_decoder_config_ref, GpuDecoderConfigRef)

    downloaded_gpu_decoder_config = (
        gpu_decoder_config_ref.download_gpu_decoder_config_contents()
    )

    assert downloaded_gpu_decoder_config == gpu_decoder_config


def test_gpu_decoder_config_flow(
    _authenticated_nexus: None,
    qa_project_name: str,
    qa_qir_name: str,
) -> None:
    """Test the flow for executing a simple GPU decoder config circuit on H1-1E."""

    device_name = "H1-1E"

    my_proj = qnx.projects.get(name_like=qa_project_name)

    gpu_decoder_config_path = Path(
        "examples/basics/data/gpu_decoder_config.yaml"
    ).resolve()
    with open(gpu_decoder_config_path) as fp:
        gpu_decoder_config = fp.read()

    qa_gpu_decoder_config_name_fixture = (
        f"qnexus_integration_test_gpu_decoder_config_{datetime.now()}"
    )

    qnx.gpu_decoder_configs.upload(
        gpu_decoder_config=gpu_decoder_config,
        name=qa_gpu_decoder_config_name_fixture,
        project=my_proj,
    )

    my_gpu_decoder_config_db_matches = qnx.gpu_decoder_configs.get_all()
    assert isinstance(my_gpu_decoder_config_db_matches.summarize(), pd.DataFrame)
    assert isinstance(next(my_gpu_decoder_config_db_matches), GpuDecoderConfigRef)

    gpu_decoder_config_ref = qnx.gpu_decoder_configs.get(
        name_like=qa_gpu_decoder_config_name_fixture
    )
    assert isinstance(gpu_decoder_config_ref, GpuDecoderConfigRef)

    gpu_decoder_config_ref_2 = qnx.gpu_decoder_configs.get(id=gpu_decoder_config_ref.id)
    assert gpu_decoder_config_ref == gpu_decoder_config_ref_2

    qir_program_ref = qnx.qir.get(name_like=qa_qir_name)

    job_ref = qnx.start_execute_job(
        programs=[qir_program_ref],
        n_shots=[10],
        backend_config=qnx.QuantinuumConfig(device_name=device_name),
        gpu_decoder_config=gpu_decoder_config_ref,
        project=my_proj,
        name=f"QA Test QIR GPU decoder config job from {datetime.now()}",
    )

    qnx.jobs.wait_for(job_ref)

    results = qnx.jobs.results(job_ref)

    assert len(results) == 1
