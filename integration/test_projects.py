


import qnexus as qnx

from qnexus.references import ProjectRef




def test_project_getonly(
    authenticated_nexus: None,
) -> None:
    """ """

    my_proj = qnx.project.get_only(name="VanyaTest")


    assert isinstance(my_proj, ProjectRef)
