import os
import typing

import httpx

from ..config import get_config
from ..exceptions import NotAuthenticatedException
from .utils import read_token_file, write_token_file

config = get_config()


class AuthHandler(httpx.Auth):
    """Custom nexus auth handler"""

    requires_response_body = True

    def auth_flow(self, request) -> typing.Generator[httpx.Request, httpx.Response, None]:
        try:
            if access_token := read_token_file("access_token"):
                httpx.Cookies({"myqos_id": access_token}).set_cookie_header(request)
                response: httpx.Response = yield request
                if response.status_code == 401:
                    refresh_response = yield self.refresh_cookies()
                    refresh_response.raise_for_status()
                    refreshed_cookies = httpx.Cookies()
                    refreshed_cookies.extract_cookies(response=refresh_response)
                    write_token_file(
                        "access_token",
                        refreshed_cookies.get("myqos_id", domain="nexus.quantinuum.com") or "",
                    )
                    request.headers.pop("cookie")
                    refreshed_cookies.set_cookie_header(request)
                    response: httpx.Response = yield request
                    if response.status_code == 401:
                        raise NotAuthenticatedException
        
        except (FileNotFoundError, NotAuthenticatedException, httpx.HTTPStatusError):
            raise SystemExit(
                "Not authenticated. Please run `qnx login` in your terminal to log in."
            )
        
    def refresh_cookies(self) -> httpx.Request:
        """Mutate cookie object with fresh access token and save updated cookies to disk."""
        return httpx.Request(
            method="POST",
            url=f"{config.url}/auth/tokens/refresh",
            cookies=httpx.Cookies({"myqos_oat": read_token_file("refresh_token")}),
        )


config = get_config()
nexus_client = httpx.Client(
    base_url=config.url,
    auth=AuthHandler(),
)
