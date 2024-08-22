"""Test basic functionality relating to the auth module."""
from io import StringIO
from typing import Any

import pytest

import qnexus as qnx
from qnexus.client.utils import read_token
from qnexus.config import get_config


def test_credential_login_full_flow(
    monkeypatch: Any,
) -> None:
    """Test that we can delete access tokens, login using credentials and
    delete tokens once again."""
    username = get_config().qa_user_email
    pwd = get_config().qa_user_password

    qnx.auth.logout()
    with pytest.raises(FileNotFoundError):
        read_token(token_type="access_token")
        read_token(token_type="refresh_token")

    # fake user input from stdin
    monkeypatch.setattr("sys.stdin", StringIO(username + "\n"))
    monkeypatch.setattr("getpass.getpass", lambda prompt: pwd)

    qnx.auth.login_with_credentials()

    assert read_token(token_type="access_token") != ""
    assert read_token(token_type="refresh_token") != ""

    qnx.auth.logout()
    with pytest.raises(FileNotFoundError):
        read_token(token_type="access_token")
        read_token(token_type="refresh_token")


@pytest.mark.skip(reason="Not implemented")
def test_device_code_flow_login_full_flow() -> None:
    """Test the flow for logging in with the browser."""
