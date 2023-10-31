import httpx
from colorama import Fore
from ..config import get_config

config = get_config()


def browser_login() -> None:
    """
    Log in to Quantinuum Nexus.
    ...
    """

    res = httpx.Client(base_url=f"{config.url}/auth").post(
        "/device/device_authorization",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"client_id": "scales", "scope": "myqos"},
    )

    user_code = res.json()["user_code"]
    device_code = res.json()["device_code"]
    verification_uri_complete = res.json()["verification_uri_complete"]
    expires_in = res.json()["expires_in"]
    poll_interval = res.json()["interval"]

    print(
        "Browser login initiated and will involve the following steps:\n"
        f"1. Visit this URL in a browser (using any device): {verification_uri_complete}\n"
        f"2. Confirm that the browser shows the following code: {user_code}\n"
        "3. Click 'Allow' and log in (with third-party such as Microsoft if required).\n"
        "4. Wait for this program to confirm successful login.\n"
    )
    return None
