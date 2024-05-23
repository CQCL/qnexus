"""Pytest fixtures and settings used in the qnexus integration tests."""

from contextlib import contextmanager
from typing import Generator

import pytest
from constants import NEXUS_QA_USER_EMAIL, NEXUS_QA_USER_PASSWORD

import qnexus as qnx


@contextmanager
def make_authenticated_nexus(
    user_email: str = NEXUS_QA_USER_EMAIL,
    user_password: str = NEXUS_QA_USER_PASSWORD,
) -> Generator:
    """Authenticate the qnexus client."""
    try:
        qnx.auth._request_tokens(  # pylint: disable=protected-access
            user_email, user_password
        )
        yield
    finally:
        qnx.auth.logout()


@pytest.fixture(scope="session")
def _authenticated_nexus() -> Generator[None, None, None]:
    """Authenticated nexus instance fixture."""
    with make_authenticated_nexus():
        yield
