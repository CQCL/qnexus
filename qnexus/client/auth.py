import httpx
from ..config import get_config
from ..consts import ACCESS_TOKEN_FILE_PATH, REFRESH_TOKEN_FILE_PATH
from .utils import write_token_file, consolidate_error
import webbrowser
from http import HTTPStatus
import time
from rich.console import Console
from rich.style import Style
from rich.panel import Panel
from rich.text import Text

console = Console()

config = get_config()


def browser_login() -> None:
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

    #  print(
    #                 "Browser login initiated and will involve the following steps:\n"
    #                 f"1. Visit this URL in a browser (using any device): {verification_uri_complete}\n"
    #                 f"2. Confirm that the browser shows the following code: {user_code}\n"
    #                 "3. Click 'Allow' and log in (with third-party such as Microsoft if required).\n"
    #                 "4. Wait for this program to confirm successful login.\n"
    #             )

    console.print("\n")
    console.print(
        Panel(
            f"""
Confirm that the browser shows the following code:
{Text(user_code, style=Style(bold=True, color="cyan"))}
            """,
            width=100,
            style=Style(color="white", bold=True),
        ),
        justify="center",
    )
    console.print("\n")
    console.print(
        f"Browser didn't open automatically? Click this link: {verification_uri_complete}"
    )
    polling_for_seconds = 0
    with console.status(
        "[bold cyan]Waiting for user to confirm code via web browser...",
        spinner_style="cyan",
    ) as status:
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
                write_token_file(REFRESH_TOKEN_FILE_PATH, resp_json["refresh_token"])
                write_token_file(
                    ACCESS_TOKEN_FILE_PATH,
                    resp_json["access_token"],
                )
                print(
                    f"Successfully logged in as {resp_json['email']} using the browser."
                )
                return
            # Fail for all other statuses
            consolidate_error(res=resp, description="Browser Login")
            return
    raise Exception("Browser Login Failed, code has expired.")


def logout() -> None:
    """Clear tokens from file system"""
    write_token_file(REFRESH_TOKEN_FILE_PATH, "")
    write_token_file(ACCESS_TOKEN_FILE_PATH, "")
    print("Successfully logged out.")
