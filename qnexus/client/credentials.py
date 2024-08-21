"""Client API for credentials in Nexus."""

from qnexus.client import get_nexus_client
from qnexus.models import Credential, CredentialIssuer
from qnexus.models.filters import CredentialsFilter
from qnexus.models.references import DataframableList


class Params(CredentialsFilter):
    """Params for filtering credentials."""


def get_all(
    issuer: CredentialIssuer | str | None = None,
) -> DataframableList[Credential]:
    """Get saved credentials."""

    params = Params(
        issuer=issuer,
    ).model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)

    res = get_nexus_client().get(
        "/api/v5/credentials",
        params=params,
    )

    return DataframableList([Credential(**cred) for cred in res.json()])
