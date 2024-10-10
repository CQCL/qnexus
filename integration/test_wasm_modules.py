"""Test basic functionality relating to the wasm_modules module."""
from datetime import datetime

import pandas as pd
from pytket import Circuit
from pytket.wasm import WasmFileHandler

import qnexus as qnx
from qnexus.models.references import WasmModuleRef


def test_wasm_flow(
    _authenticated_nexus: None,
    qa_project_name: str,
) -> None:
    """Test the flow for executing a simple WASM circuit on H1-1LE."""

    my_proj = qnx.projects.get(name_like=qa_project_name)

    wfh = WasmFileHandler(filepath="../examples/data/add_one.wasm")
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

    circuit = Circuit(0, 2)
    circuit.add_wasm("add_one", wfh, [1], [1], [0, 1])
    qa_wasm_circuit_name_fixture = (
        f"qnexus_integration_test_wasm_circuit_{datetime.now()}"
    )

    wasm_circuit_ref = qnx.circuits.upload(
        name=qa_wasm_circuit_name_fixture,
        circuit=circuit,
    )

    execute_job_ref = qnx.start_execute_job(
        circuits=[wasm_circuit_ref],
        name=f"qnexus_integration_test_wasm_execute_job_{datetime.now()}",
        n_shots=[100],
        backend_config=qnx.QuantinuumConfig(
            device_name="H1-1LE",
        ),
        wasm_module=wasm_ref,
    )

    qnx.jobs.wait_for(execute_job_ref)

    assert qnx.jobs.status(execute_job_ref).status == qnx.jobs.StatusEnum.COMPLETED
