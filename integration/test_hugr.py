"""Test basic functionality relating to the hugr module."""

from typing import Callable, ContextManager

import pytest
from hugr.package import Package

import qnexus as qnx
import qnexus.exceptions as qnx_exc
from qnexus.models.annotations import PropertiesDict
from qnexus.models.references import HUGRRef, ProjectRef, Ref


def test_hugr_create_and_update(
    test_case_name: str,
    qa_hugr_package: Package,
    create_property_in_project: Callable[..., ContextManager[ProjectRef]],
) -> None:
    """Test that we can create a hugr and add a property value."""
    project_name = f"project for {test_case_name}"
    property_name = f"property for {test_case_name}"

    with create_property_in_project(
        project_name=project_name,
        property_name=property_name,
        property_type="string",
        required=False,
    ) as my_proj:
        hugr_name = f"hugr for {test_case_name}"
        my_new_hugr = qnx.hugr.upload(
            hugr_package=qa_hugr_package, name=hugr_name, project=my_proj
        )

        assert isinstance(my_new_hugr, HUGRRef)

        test_prop_value = "foo"
        updated_hugr_ref = qnx.hugr.update(
            ref=my_new_hugr,
            properties=PropertiesDict({property_name: test_prop_value}),
        )

        assert updated_hugr_ref.annotations.properties[property_name] == test_prop_value


def test_hugr_download(
    test_case_name: str,
    qa_hugr_package: Package,
    create_hugr_in_project: Callable[[str, str, Package], ContextManager[HUGRRef]],
) -> None:
    """Test that valid HUGR can be extracted from an uploaded HUGR module."""
    project_name = f"project for {test_case_name}"
    hugr_name = f"hugr for {test_case_name}"

    with create_hugr_in_project(
        project_name,
        hugr_name,
        qa_hugr_package,
    ) as hugr_ref:
        with pytest.raises(qnx_exc.ResourceFetchFailed):
            # Temporarily disabled due to missing functionality in hugr
            downloaded_hugr_package = hugr_ref.download_hugr()
            assert isinstance(downloaded_hugr_package, Package)
            assert qa_hugr_package == downloaded_hugr_package
        downloaded_hugr_bytes = hugr_ref.download_hugr_bytes()
        assert isinstance(downloaded_hugr_bytes, bytes)
        assert qa_hugr_package.to_bytes() == downloaded_hugr_bytes


def test_hugr_get_by_id(
    test_case_name: str,
    qa_hugr_package: Package,
    create_hugr_in_project: Callable[[str, str, Package], ContextManager[HUGRRef]],
    test_ref_serialisation: Callable[[str, Ref], None],
) -> None:
    """Test that we can get a HUGRRef by its ID and the HUGRRef
    serialisation round trip."""
    project_name = f"project for {test_case_name}"
    hugr_name = f"hugr for {test_case_name}"

    with create_hugr_in_project(
        project_name,
        hugr_name,
        qa_hugr_package,
    ):
        my_proj = qnx.projects.get(name_like=project_name)
        my_hugr_ref = qnx.hugr.get(name_like=hugr_name, project=my_proj)

        hugr_ref_by_id = qnx.hugr.get(id=my_hugr_ref.id)

        assert hugr_ref_by_id == my_hugr_ref

        test_ref_serialisation("hugr", hugr_ref_by_id)


def test_hugr_get_all(
    test_case_name: str,
    qa_hugr_package: Package,
    create_hugr_in_project: Callable[[str, str, Package], ContextManager[HUGRRef]],
) -> None:
    """Test that we can get all HUGRRefs in a project."""
    project_name = f"project for {test_case_name}"
    hugr_name = f"hugr for {test_case_name}"

    with create_hugr_in_project(
        project_name,
        hugr_name,
        qa_hugr_package,
    ):
        my_proj = qnx.projects.get(name_like=project_name)

        hugrs = qnx.hugr.get_all(project=my_proj)

        assert hugrs.count() >= 1
        assert isinstance(hugrs.list()[0], HUGRRef)
