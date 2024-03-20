import typing

import httpx

from ..config import get_config
from ..exceptions import NotAuthenticatedException
from .utils import read_token, write_token

config = get_config()


class AuthHandler(httpx.Auth):
    """Custom nexus auth handler"""
    cookies: httpx.Cookies

    def __init__(self) -> None:
        self.cookies = httpx.Cookies()
        try:
            refresh_token = read_token("refresh_token")
            self.cookies.set("myqos_oat", refresh_token, domain=config.domain)
        except FileNotFoundError:
            pass  # Okay to ignore this as the user may log in later

        super().__init__()


    def auth_flow(
        self, request: httpx.Request
    ) -> typing.Generator[httpx.Request, httpx.Response, None]:
        self.cookies.set_cookie_header(request)
        response = yield request
        if response.status_code == 401:
            if self.cookies.get("myqos_oat") is None:
                try:
                    refresh_token = read_token("refresh_token")
                    self.cookies.set(
                        "myqos_oat", refresh_token, domain=config.domain
                    )
                except FileNotFoundError:
                    raise NotAuthenticatedException(
                        "Not authenticated. Please run `qnx login` in your terminal."
                    )

            auth_response = yield self.build_refresh_request()
            if auth_response.status_code == 401:
                raise NotAuthenticatedException(
                    "Not authenticated. Please run `qnx login` in your terminal."
                )

            auth_response.raise_for_status()
            self.cookies.extract_cookies(auth_response)

            write_token(
                "access_token",
                self.cookies.get("myqos_id", domain=config.domain) or "",
            )
            request.headers.pop("cookie")
            self.cookies.set_cookie_header(request)
            yield request

    def build_refresh_request(self) -> httpx.Request:
        self.cookies.delete("myqos_id")  # We need to delete the existing token first
        return httpx.Request(
            method="POST",
            url=f"{config.url}/auth/tokens/refresh",
            cookies=self.cookies,
        )


config = get_config()
nexus_client = httpx.Client(
    base_url=config.url,
    auth=AuthHandler(),
    timeout=None,
)
