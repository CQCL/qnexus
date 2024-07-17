"""Test filesystem operations with Nexus Refs."""

from datetime import datetime
from pathlib import Path
import shutil
from typing import cast

import qnexus as qnx
from qnexus.references import BaseRef, JobRef
from qnexus.filesystem import save, load


def test_save_load(  # pylint: disable=too-many-locals
    _authenticated_nexus: None,
    qa_project_name: str,
    qa_circuit_name: str,
    qa_team_name: str,
    qa_compile_job_name: str,
    qa_execute_job_name: str,
) -> None:
    """Test Ref serialization and deserialization roundtrip,
    and check that all Ref types are covered."""

    user_ref = qnx.users.get_self()
    project_ref = qnx.projects.get(name_like=qa_project_name)
    team_ref = qnx.teams.get(name=qa_team_name)
    circuit_ref = qnx.circuits.get(name_like=qa_circuit_name)
    execute_job_ref = cast(
        qnx.jobs.ExecuteJobRef, qnx.jobs.get(name_like=qa_execute_job_name)
    )
    compile_job_ref = cast(
        qnx.jobs.CompileJobRef, qnx.jobs.get(name_like=qa_compile_job_name)
    )
    execute_result_ref = qnx.jobs.results(execute_job_ref)[0]
    compile_result_ref = qnx.jobs.results(compile_job_ref)[0]
    # Cast and copy to avoid adding cached data to the ref which will
    # affect the equality assertion below
    compilation_pass_ref = cast(
        qnx.jobs.CompilationResultRef, compile_result_ref.model_copy()
    ).get_passes()[0]

    test_refs = [
        user_ref,
        project_ref,
        team_ref,
        circuit_ref,
        execute_job_ref,
        compile_job_ref,
        execute_result_ref,
        compile_result_ref,
        compilation_pass_ref,
    ]
    test_ref_types = set(type(test_ref) for test_ref in test_refs)
    all_refs = set(BaseRef.__subclasses__())
    # remove JobRef as its only used as a base class
    all_refs.remove(JobRef)  # type: ignore
    assert test_ref_types == all_refs

    test_ref_path = Path().cwd() / f"refs_test_{datetime.now()}"

    save(ref=project_ref, path=test_ref_path / "project", mkdir=True)
    save(ref=team_ref, path=test_ref_path / "team", mkdir=True)
    save(ref=circuit_ref, path=test_ref_path / "circuit", mkdir=True)
    save(ref=execute_job_ref, path=test_ref_path / "execute", mkdir=True)
    save(ref=compile_job_ref, path=test_ref_path / "compile", mkdir=True)
    save(ref=execute_result_ref, path=test_ref_path / "execute_result", mkdir=True)
    save(ref=compile_result_ref, path=test_ref_path / "compile_result", mkdir=True)
    save(ref=compilation_pass_ref, path=test_ref_path / "compilation_pass", mkdir=True)
    save(ref=user_ref, path=test_ref_path / "user", mkdir=True)

    project_ref_2 = load(path=test_ref_path / "project")
    team_ref_2 = load(path=test_ref_path / "team")
    circuit_ref_2 = load(path=test_ref_path / "circuit")
    execute_job_ref_2 = load(path=test_ref_path / "execute")
    compile_job_ref_2 = load(path=test_ref_path / "compile")
    execute_result_ref_2 = load(path=test_ref_path / "execute_result")
    compile_result_ref_2 = load(path=test_ref_path / "compile_result")
    compilation_pass_ref_2 = load(path=test_ref_path / "compilation_pass")
    user_ref_2 = load(path=test_ref_path / "user")

    assert project_ref == project_ref_2
    assert team_ref == team_ref_2
    assert circuit_ref == circuit_ref_2
    assert execute_job_ref == execute_job_ref_2
    assert compile_job_ref == compile_job_ref_2
    assert execute_result_ref == execute_result_ref_2
    assert compile_result_ref == compile_result_ref_2
    assert compilation_pass_ref == compilation_pass_ref_2
    assert user_ref == user_ref_2

    # Clean up the saved ref files
    shutil.rmtree(test_ref_path)