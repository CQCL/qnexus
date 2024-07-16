"""Test basic functionality relating to the credential module."""

import qnexus as qnx
from qnexus.client.models import Credential, CredentialIssuer


def test_credential_get(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get a list of credentials."""
    creds = qnx.credential.get_all()
    assert isinstance(creds, list)
    for cred in creds:
        assert isinstance(cred, Credential)
        assert isinstance(cred.backend_issuer, CredentialIssuer)