"""Test basic functionality relating to the wasm_modules module."""

from datetime import datetime
from pathlib import Path

import pandas as pd
from pytket.backends.status import StatusEnum
from pytket.circuit import Circuit
from pytket.wasm.wasm import WasmFileHandler

import qnexus as qnx
from qnexus.models.references import WasmModuleRef


def test_wasm_download(
    _authenticated_nexus: None,
    qa_project_name: str,
) -> None:
    """Test that valid WASM can be extracted from an uploaded WASM module."""

    my_proj = qnx.projects.get(name_like=qa_project_name)

    wasm_path = Path("examples/basics/data/add_one.wasm").resolve()
    wfh = WasmFileHandler(filepath=str(wasm_path))
    qa_wasm_module_name_fixture = f"qnexus_integration_test_wasm_{datetime.now()}"

    qnx.wasm_modules.upload(
        wasm_module_handler=wfh,
        name=qa_wasm_module_name_fixture,
        project=my_proj,
    )

    wasm_ref = qnx.wasm_modules.get(name_like=qa_wasm_module_name_fixture)
    assert isinstance(wasm_ref, WasmModuleRef)
    downloaded_wasm_module_handler = wasm_ref.download_wasm_contents()

    downloaded_wasm_module_handler.check()
    assert downloaded_wasm_module_handler.functions == wfh.functions


def test_wasm_flow(
    _authenticated_nexus: None,
    qa_project_name: str,
) -> None:
    """Test the flow for executing a simple WASM circuit on H1-1LE."""

    my_proj = qnx.projects.get(name_like=qa_project_name)

    wasm_path = Path("examples/basics/data/add_one.wasm").resolve()
    wfh = WasmFileHandler(filepath=str(wasm_path))
    qa_wasm_module_name_fixture = f"qnexus_integration_test_wasm_{datetime.now()}"

    qnx.wasm_modules.upload(
        wasm_module_handler=wfh,
        name=qa_wasm_module_name_fixture,
        project=my_proj,
    )

    my_wasm_db_matches = qnx.wasm_modules.get_all()
    assert isinstance(my_wasm_db_matches.summarize(), pd.DataFrame)
    assert isinstance(next(my_wasm_db_matches), WasmModuleRef)

    wasm_ref = qnx.wasm_modules.get(name_like=qa_wasm_module_name_fixture)
    assert isinstance(wasm_ref, WasmModuleRef)

    wasm_ref_2 = qnx.wasm_modules.get(id=wasm_ref.id)
    assert wasm_ref == wasm_ref_2

    circuit = Circuit(1)
    a = circuit.add_c_register("a", 8)
    circuit.add_wasm_to_reg("add_one", wfh, [a], [a])
    circuit.measure_all()
    qa_wasm_circuit_name_fixture = (
        f"qnexus_integration_test_wasm_circuit_{datetime.now()}"
    )

    wasm_circuit_ref = qnx.circuits.upload(
        name=qa_wasm_circuit_name_fixture,
        circuit=circuit,
        project=my_proj,
    )

    execute_job_ref = qnx.start_execute_job(
        circuits=[wasm_circuit_ref],
        name=f"qnexus_integration_test_wasm_execute_job_{datetime.now()}",
        n_shots=[100],
        backend_config=qnx.QuantinuumConfig(
            device_name="H1-Emulator",
        ),
        wasm_module=wasm_ref,
        project=my_proj,
    )

    qnx.jobs.wait_for(execute_job_ref)

    assert qnx.jobs.status(execute_job_ref).status == StatusEnum.COMPLETED
