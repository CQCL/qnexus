"""Test basic functionality relating to the auth module."""

from io import StringIO
from typing import Any

import pytest
from httpx import ConnectError

import qnexus as qnx
from qnexus.client import get_nexus_client
from qnexus.client.auth import login_no_interaction
from qnexus.client.utils import read_token
from qnexus.config import CONFIG
from qnexus.exceptions import AuthenticationError


def test_credential_login_full_flow(
    monkeypatch: Any,
) -> None:
    """Test that we can delete access tokens, login using credentials and
    delete tokens once again."""
    username = CONFIG.qa_user_email
    pwd = CONFIG.qa_user_password

    qnx.logout()
    with pytest.raises(FileNotFoundError):
        read_token(token_type="access_token")
        read_token(token_type="refresh_token")

    with pytest.raises(AuthenticationError):
        qnx.users.get_self()

    # fake user input from stdin
    monkeypatch.setattr("sys.stdin", StringIO(username + "\n"))
    monkeypatch.setattr("getpass.getpass", lambda prompt: pwd)

    qnx.login_with_credentials()

    assert read_token(token_type="access_token") != ""
    assert read_token(token_type="refresh_token") != ""

    qnx.users.get_self()

    qnx.logout()
    with pytest.raises(FileNotFoundError):
        read_token(token_type="access_token")
        read_token(token_type="refresh_token")

    with pytest.raises(AuthenticationError):
        qnx.users.get_self()

    # Login again to make sure credentials are in the system for the other tests
    # fake user input from stdin
    monkeypatch.setattr("sys.stdin", StringIO(username + "\n"))
    monkeypatch.setattr("getpass.getpass", lambda prompt: pwd)
    qnx.login_with_credentials()


@pytest.mark.skip(reason="Not implemented")
def test_device_code_flow_login_full_flow() -> None:
    """Test the flow for logging in with the browser."""


def test_domain_switch() -> None:
    """Set that we can reset the domain, login and not
    for tokens/URL to be dynamically loaded."""

    username = CONFIG.qa_user_email
    pwd = CONFIG.qa_user_password

    login_no_interaction(username, pwd)

    qnx.users.get_self()

    original_domain = CONFIG.domain

    # fake domain will reset the client value
    qnx.logout()
    fake_domain = "fake_nexus.com"
    CONFIG.domain = fake_domain
    assert fake_domain in str(get_nexus_client(reload=True).base_url)

    with pytest.raises(ConnectError):
        qnx.users.get_self()

    # setting it again will update the client without any restart required
    CONFIG.domain = original_domain
    login_no_interaction(username, pwd)
    assert original_domain in str(get_nexus_client().base_url)

    qnx.users.get_self()
