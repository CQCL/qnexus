"""Script to setup tokens in the testing environment."""

import qnexus as qnx
from qnexus.config import get_config

qnx.auth._request_tokens(  # pylint: disable=protected-access
    get_config().qa_user_email, get_config().qa_user_password
)
