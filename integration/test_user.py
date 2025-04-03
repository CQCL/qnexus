"""Test basic functionality relating to the user module."""

import qnexus as qnx
from qnexus.models.references import UserRef


def test_user_get(_authenticated_nexus: None) -> None:
    """Test that we can get a specific unique UserRef."""

    my_user = qnx.users.get_self()
    assert isinstance(my_user, UserRef)

    my_user_again = qnx.users._fetch_by_id(user_id=my_user.id)
    assert isinstance(my_user_again, UserRef)
    assert my_user == my_user_again
