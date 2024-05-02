"""Client API for authentication in Nexus."""
import time
import webbrowser
from http import HTTPStatus

import httpx
from colorama import Fore

# from halo import Halo
from rich.console import Console
from rich.panel import Panel

import qnexus.exceptions as qnx_exc
from qnexus.client.utils import consolidate_error, write_token
from qnexus.config import Config

console = Console()
config = Config()


def login() -> None:
    """
    Log in to Quantinuum Nexus using the web browser.
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

    webbrowser.open(verification_uri_complete, new=2)

    token_request_body = {
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "device_code": device_code,
        "client_id": "scales",
    }

    print("🌐 Browser login initiated.")
    # spinner = Halo(
    #     text=f"Waiting for user to log in via browser...",
    #     spinner="simpleDotsScrolling",
    # )
    console.print(
        Panel(
            f"""
        Confirm that the browser shows the following code and click 'allow device':

                                     {user_code}
        """,
            width=90,
        )
    )

    print(
        "Browser didn't open automatically? Use this link: "
        f"{Fore.BLUE + verification_uri_complete}"
    )

    # spinner.start()

    polling_for_seconds = 0
    while polling_for_seconds < expires_in:
        time.sleep(poll_interval)
        polling_for_seconds += poll_interval
        resp = httpx.Client(base_url=f"{config.url}/auth").post(
            "/device/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=token_request_body,
        )
        if (
            resp.status_code == HTTPStatus.BAD_REQUEST
            and resp.json().get("error") == "AUTHORIZATION_PENDING"
        ):
            continue
        if resp.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            continue
        if resp.status_code == HTTPStatus.OK:
            resp_json = resp.json()
            write_token("refresh_token", resp_json["refresh_token"])
            write_token(
                "access_token",
                resp_json["access_token"],
            )
            # spinner.stop()
            print(
                f"✅ Successfully logged in as {resp_json['email']} using the browser."
            )
            return
        # Fail for all other statuses
        consolidate_error(res=resp, description="Browser Login")
        # spinner.stop()
        return
    # spinner.stop()
    raise qnx_exc.AuthenticationError("Browser login Failed, code has expired.")


def logout() -> None:
    """Clear tokens from file system"""
    write_token("refresh_token", "")
    write_token("access_token", "")
    print("Successfully logged out.")
