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
                if response.status_code != 401:
                    return
                
            print(f"older access {read_token_file('access_token')}")

            self.refresh_cookies()
            refreshed_access_token = read_token_file('access_token')
            print(request.headers)
            httpx.Cookies({"myqos_id": refreshed_access_token}).set_cookie_header(request)
            print(request.headers)
            response: httpx.Response = yield request
            if response.status_code == 401:
                raise NotAuthenticatedException(
                    "Not authenticated. Please run `qnx login` in your terminal."
                )
            return
        
        except (FileNotFoundError, NotAuthenticatedException, httpx.HTTPStatusError):
            raise SystemExit(
                "Not authenticated. Please run `qnx login` in your terminal to log in."
            )
        
    def refresh_cookies(self) -> None:
        """Mutate cookie object with fresh access token and save updated cookies to disk."""
        cookies = httpx.Cookies({"myqos_oat": read_token_file("refresh_token")})

        refresh_response = httpx.Client(base_url=f"{config.url}/auth").post(
            "/tokens/refresh",
            cookies=cookies,
        )
        refresh_response.raise_for_status()
        cookies.extract_cookies(response=refresh_response)
        write_token_file(
            "access_token",
            cookies.get("myqos_id", domain="nexus.quantinuum.com") or "",
        )


config = get_config()
nexus_client = httpx.Client(
    base_url=config.url,
    auth=AuthHandler(),
)
