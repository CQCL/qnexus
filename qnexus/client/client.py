import httpx
from ..config import get_config
from ..consts import ACCESS_TOKEN_FILE_PATH, REFRESH_TOKEN_FILE_PATH
from ..errors import NotAuthenticatedException
import os
from pathlib import Path

config = get_config()


def read_token_file(path: str) -> str:
    """Read a token from a file."""
    full_path = f"{Path.home()}/{path}"
    if os.path.isfile(full_path):
        with open(full_path, encoding="UTF-8") as file:
            return file.read().strip()
    return ""


def write_token_file(path: str, token: str) -> None:
    """Write a token to a file."""
    full_path = f"{Path.home()}/{path}"
    with open(full_path, encoding="UTF-8", mode="w") as file:
        file.write(token)
    return None


def refresh_cookies(cookies: httpx.Cookies) -> None:
    """Mutate cookie object with fresh access token and save updated cookies to disk."""
    refresh_response = httpx.Client(base_url=f"{config.url}/auth").post(
        "/tokens/refresh",
        cookies=cookies,
    )
    cookies.extract_cookies(response=refresh_response)
    write_token_file(
        ACCESS_TOKEN_FILE_PATH,
        cookies.get("myqos_id", domain="nexus.quantinuum.com") or "",
    )


class AuthHandler(httpx.Auth):
    """Custom nexus auth handler"""

    requires_response_body = True

    def auth_flow(self, request):
        access_token = read_token_file(ACCESS_TOKEN_FILE_PATH)
        refresh_token = read_token_file(REFRESH_TOKEN_FILE_PATH)
        if access_token:
            httpx.Cookies({"myqos_id": access_token}).set_cookie_header(request)
            response: httpx.Response = yield request
            if response.status_code != 401:
                return response

        cookies = httpx.Cookies({"myqos_oat": refresh_token})
        refresh_cookies(cookies)
        cookies.set_cookie_header(request)
        response: httpx.Response = yield request
        return response


config = get_config()
nexus_client = httpx.Client(
    base_url=config.url,
    auth=AuthHandler(),
)
