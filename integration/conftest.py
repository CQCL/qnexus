"""Pytest fixtures and settings used in the qnexus integration tests."""

from contextlib import contextmanager
from typing import Generator
import pytest

from integration.constants import (
    NEXUS_USER_EMAIL,
    NEXUS_USER_PASSWORD,
    NEXUS_INTEGRATION_TEST,
)
import qnexus as qnx
from qnexus.consts import STORE_TOKENS


@contextmanager
def make_authenticated_nexus(
    user_email: str = NEXUS_USER_EMAIL,
    user_password: str = NEXUS_USER_PASSWORD,
) -> Generator:
    """Authenticate the qnexus client.
    """
    STORE_TOKENS = False
    try:
        qnx.auth._request_tokens(user_email, user_password)  # pylint: disable=protected-access
        yield
    finally:
        qnx.auth.logout()



@pytest.fixture()
def authenticated_nexus() -> Generator[None, None, None]:
    """Authenticated nexus instance fixture."""
    with make_authenticated_nexus():
        yield