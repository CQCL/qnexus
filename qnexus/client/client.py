import os

import httpx

from ..config import get_config
from ..exceptions import NotAuthenticatedException
from .utils import read_token_file, write_token_file

config = get_config()


def refresh_cookies(cookies: httpx.Cookies) -> None:
    """Mutate cookie object with fresh access token and save updated cookies to disk."""
    refresh_response = httpx.Client(base_url=f"{config.url}/auth").post(
        "/tokens/refresh",
        cookies=cookies,
    )
    cookies.extract_cookies(response=refresh_response)
    write_token_file(
        "access_token",
        cookies.get("myqos_id", domain="nexus.quantinuum.com") or "",
    )


class AuthHandler(httpx.Auth):
    """Custom nexus auth handler"""

    requires_response_body = True

    def auth_flow(self, request):
        try:
            if access_token := read_token_file("access_token"):
                httpx.Cookies({"myqos_id": access_token}).set_cookie_header(request)
                response: httpx.Response = yield request
                if response.status_code != 401:
                    return response

            refresh_token = read_token_file("refresh_token")
            cookies = httpx.Cookies({"myqos_oat": refresh_token})
            refresh_cookies(cookies)
            cookies.set_cookie_header(request)
            response: httpx.Response = yield request
            if response.status_code == 401:
                raise NotAuthenticatedException(
                    "Not authenticated. Please run `qnx login` in your terminal."
                )

            return response
        except (FileNotFoundError, NotAuthenticatedException):
            raise SystemExit(
                "Not authenticated. Please run `qnx login` in your terminal to log in."
            )


config = get_config()
nexus_client = httpx.Client(
    base_url=config.url,
    auth=AuthHandler(),
)
