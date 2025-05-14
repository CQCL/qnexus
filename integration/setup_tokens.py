"""Script to setup tokens in the testing environment."""

import qnexus as qnx
from qnexus.config import CONFIG

qnx.auth._request_tokens(CONFIG.qa_user_email, CONFIG.qa_user_password)
