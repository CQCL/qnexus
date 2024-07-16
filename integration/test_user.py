"""Test basic functionality relating to the user module."""

import qnexus as qnx
from qnexus.references import UserRef


def test_user_getonly(_authenticated_nexus: None) -> None:
    """Test that we can get a specific unique UserRef."""

    my_user = qnx.user.get_self()
    assert isinstance(my_user, UserRef)

    my_user_again = qnx.user._fetch(  # pylint: disable=protected-access
        user_id=my_user.id
    )
    assert isinstance(my_user_again, UserRef)
