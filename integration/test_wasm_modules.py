"""Test basic functionality relating to the wasm_modules module."""
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest
from pytket.backends.backendinfo import BackendInfo
from pytket.backends.backendresult import BackendResult
from pytket.wasm import WasmFileHandler
from pytket.wasm.wasm import WasmModuleHandler

import qnexus as qnx
import qnexus.exceptions as qnx_exc
from qnexus.models.hypertket_config import HyperTketConfig
from qnexus.models.references import (
    CircuitRef,
    CompilationPassRef,
    CompilationResultRef,
    CompileJobRef,
    ExecuteJobRef,
    JobRef,
    WasmModuleRef,
)


def test_wasm_flow(
    _authenticated_nexus: None,
    qa_project_name: str,
    qa_wasm_module_name_fixture: str,
) -> None:
    """Test."""

    my_proj = qnx.projects.get(name_like=qa_project_name)

    wasm_path = Path().cwd() / "extras" / "rus.wasm"
    wfh = WasmFileHandler(str(wasm_path))

    qnx.wasm_modules.upload(
        wasm_module_handler=wfh,
        name=qa_wasm_module_name_fixture,
        project=my_proj,
    )

    my_wasm_db_matches = qnx.wasm_modules.get_all()
    assert isinstance(my_wasm_db_matches.summarize(), pd.DataFrame)
    assert isinstance(next(my_wasm_db_matches), WasmModuleRef)

    my_wasm = qnx.wasm_modules.get(name_like=qa_wasm_module_name_fixture)
    assert isinstance(my_wasm, WasmModuleRef)
