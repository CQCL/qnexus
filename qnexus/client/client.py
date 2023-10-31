import httpx
from ..config import get_config
from ..consts import CREDS_FILE_PATH
from typing import Dict, Any
import os
from urllib.request import Request

config = get_config()


def read_config_file(path: str) -> Dict[str, Any]:
    """Read a config of key value pairs as a dict"""
    env_vars = {}
    homedir = os.path.expanduser("~")
    with open(f"{homedir}/{path}", encoding="UTF-8") as myfile:
        for line in myfile:
            name, var = line.partition("=")[::2]
            env_vars[name.strip()] = var.strip()
    return env_vars


def write_config_file(path: str, obj: Dict[str, Any]) -> None:
    """Replace content in a config with key value pairs."""
    homedir = os.path.expanduser("~")
    f = open(f"{homedir}/{path}", encoding="UTF-8", mode="w")
    for key, val in obj.items():
        f.write(f"{key}={val}")
        f.write("\n")
    return None


def refresh_cookies(cookies: httpx.Cookies) -> None:
    """Mutate cookie object with fresh access token and save updated cookies to disk."""
    refresh_response = httpx.Client(base_url=f"{config.url}/auth").post(
        "/tokens/refresh",
        cookies=cookies,
    )
    cookies.extract_cookies(response=refresh_response)
    write_config_file(
        CREDS_FILE_PATH,
        {
            "myqos_id": cookies.get("myqos_id", domain="nexus.quantinuum.com") or "",
            "myqos_oat": cookies.get("myqos_oat") or "",
        },
    )


class AuthHandler(httpx.Auth):
    """Custom nexus auth handler"""

    requires_response_body = True

    def auth_flow(self, request):
        creds = read_config_file(CREDS_FILE_PATH)
        access_token = creds.get("myqos_id")
        refresh_token = creds.get("myqos_oat")
        if access_token:
            httpx.Cookies({"myqos_id": creds.get("myqos_id")}).set_cookie_header(
                request
            )
            response: httpx.Response = yield request
            if response.status_code != 401:
                return response
        if refresh_token:
            cookies = httpx.Cookies({"myqos_oat": creds.get("myqos_oat")})
            refresh_cookies(cookies)
            cookies.set_cookie_header(request)
            response: httpx.Response = yield request
            if response.status_code != 401:
                return response
        raise Exception("Unauthenticated")


config = get_config()
nexus_client = httpx.Client(
    base_url=config.url,
    auth=AuthHandler(),
)
