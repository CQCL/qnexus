"""Script to setup tokens in the testing environment."""

from constants import NEXUS_QA_USER_EMAIL, NEXUS_QA_USER_PASSWORD

import qnexus as qnx

qnx.auth._request_tokens(  # pylint: disable=protected-access
    NEXUS_QA_USER_EMAIL, NEXUS_QA_USER_PASSWORD
)
