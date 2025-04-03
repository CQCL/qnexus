"""Test that we can set properties on a project, and use them when creating/filtering resources."""

from datetime import datetime
from typing import OrderedDict

from pytket.circuit import Circuit

import qnexus as qnx
from qnexus.models.annotations import PropertiesDict


def test_property_creation_and_filtering(
    _authenticated_nexus: None,
) -> None:
    """Test that we can create resources with property values
    and filter resources by their property values."""

    project_name = f"QA_test_project_properties_{datetime.now()}"

    my_new_project = qnx.projects.create(name=project_name)

    test_property_name_1 = "QA_test_prop_1"
    test_property_name_2 = "QA_test_prop_2"
    test_property_name_3 = "QA_test_prop_3"
    test_property_name_4 = "QA_test_prop_4"

    qnx.projects.add_property(
        name=test_property_name_1,
        property_type="bool",
        project=my_new_project,
        description="A test property for my QA test project",
    )

    qnx.projects.add_property(
        name=test_property_name_2,
        property_type="string",
        project=my_new_project,
        description="Another test property for my QA test project",
    )

    qnx.projects.add_property(
        name=test_property_name_3,
        property_type="int",
        project=my_new_project,
        description="Another test property for my QA test project",
    )

    qnx.projects.add_property(
        name=test_property_name_4,
        property_type="float",
        project=my_new_project,
        description="Another test property for my QA test project",
    )

    test_props = qnx.projects.get_properties(my_new_project)

    assert len(test_props) == 4

    circuit_name = f"QA_test_circuit_with_props_{datetime.now()}"

    my_circ = Circuit(2, 2).H(0).CX(0, 1).measure_all()

    qnx.circuits.upload(
        circuit=my_circ,
        name=circuit_name,
        project=my_new_project,
        properties=OrderedDict(
            {
                test_property_name_1: True,
                test_property_name_2: "test_string",
                test_property_name_3: 42,
                test_property_name_4: 3.15,
            }
        ),
    )

    qnx.circuits.upload(
        circuit=my_circ,
        name=circuit_name,
        project=my_new_project,
        properties=OrderedDict(
            {
                test_property_name_1: False,
            }
        ),
    )

    my_circuit_refs = qnx.circuits.get_all(
        project=my_new_project,
        properties=PropertiesDict(
            {
                test_property_name_1: True,
                test_property_name_2: "test_string",
                test_property_name_3: 42,
                test_property_name_4: 3.15,
            }
        ),
    )

    assert my_circuit_refs.count() == 1
    my_circuit_ref = my_circuit_refs.list()[0]

    assert my_circuit_ref.annotations.properties[test_property_name_1] is True
    assert my_circuit_ref.annotations.properties[test_property_name_2] == "test_string"

    qnx.projects.update(my_new_project, archive=True)
    qnx.projects.delete(my_new_project)
