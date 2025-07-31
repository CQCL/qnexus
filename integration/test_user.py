"""Test basic functionality relating to the user module."""

from typing import Callable

import qnexus as qnx
from qnexus.models.references import Ref, UserRef


def test_user_get(authenticated_nexus: None) -> None:
    """Test that we can get a specific unique UserRef."""

    my_user = qnx.users.get_self()
    assert isinstance(my_user, UserRef)

    my_user_again = qnx.users._fetch_by_id(user_id=my_user.id)
    assert isinstance(my_user_again, UserRef)
    assert my_user == my_user_again


def test_user_ref_serialisation(
    authenticated_nexus: None,
    test_ref_serialisation: Callable[[str, Ref], None],
) -> None:
    """Test the serialisation round trip of a UserRef."""

    my_user = qnx.users.get_self()

    test_ref_serialisation("user", my_user)
