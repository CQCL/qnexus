"""Test basic functionality relating to the hugr module."""

from datetime import datetime
from pathlib import Path

from hugr.package import Package

import qnexus as qnx
from qnexus.models.annotations import PropertiesDict
from qnexus.models.references import HUGRRef


def test_hugr_create_and_update(
    _authenticated_nexus: None,
    qa_project_name: str,
) -> None:
    """Test that we can create a hugr and add a property value."""

    my_proj = qnx.projects.get(name_like=qa_project_name)

    hugr_name = f"QA_test_hugr_{datetime.now()}"

    hugr_path = Path("integration/data/hugr_example.json").resolve()
    hugr_package = Package.from_json(hugr_path.read_text(encoding="utf-8"))

    my_new_hugr = qnx.hugr.upload(
        hugr_package=hugr_package, name=hugr_name, project=my_proj
    )

    assert isinstance(my_new_hugr, HUGRRef)

    test_property_name = "QA_test_prop"
    test_prop_value = "foo"

    updated_hugr_ref = qnx.hugr.update(
        ref=my_new_hugr,
        properties=PropertiesDict({test_property_name: test_prop_value}),
    )

    assert (
        updated_hugr_ref.annotations.properties[test_property_name] == test_prop_value
    )


def test_hugr_download(
    _authenticated_nexus: None,
    qa_project_name: str,
    qa_hugr_name: str,
) -> None:
    """Test that valid HUGR can be extracted from an uploaded HUGR module."""

    my_proj = qnx.projects.get(name_like=qa_project_name)
    my_hugr_ref = qnx.hugr.get(name_like=qa_hugr_name, project=my_proj)

    hugr_package = my_hugr_ref.download_hugr()
    assert isinstance(hugr_package, Package)


def test_hugr_get_by_id(
    _authenticated_nexus: None,
    qa_project_name: str,
    qa_hugr_name: str,
) -> None:
    """Test that we can get a HUGRRef by its ID."""
    my_proj = qnx.projects.get(name_like=qa_project_name)
    my_hugr_ref = qnx.hugr.get(name_like=qa_hugr_name, project=my_proj)

    hugr_ref_by_id = qnx.hugr.get(id=my_hugr_ref.id)

    assert hugr_ref_by_id == my_hugr_ref


def test_hugr_get_all(
    _authenticated_nexus: None,
    qa_project_name: str,
) -> None:
    """Test that we can get all HUGRRefs in a project."""
    my_proj = qnx.projects.get(name_like=qa_project_name)

    hugrs = qnx.hugr.get_all(project=my_proj)

    assert hugrs.count() >= 1
    assert isinstance(hugrs.list()[0], HUGRRef)
