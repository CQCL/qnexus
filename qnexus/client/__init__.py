"""Client API for Nexus."""
import typing

import httpx

from qnexus.client.utils import read_token, write_token
from qnexus.config import get_config
from qnexus.exceptions import AuthenticationError

config = get_config()


class AuthHandler(httpx.Auth):
    """Custom nexus auth handler"""

    cookies: httpx.Cookies

    def __init__(self) -> None:
        self.cookies = httpx.Cookies()
        try:
            token = read_token(
                "refresh_token",
            )
            self.cookies.set("myqos_oat", token, domain=config.domain)
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
                    token = read_token(
                        "refresh_token",
                    )
                    self.cookies.set("myqos_oat", token, domain=config.domain)
                except FileNotFoundError as exc:
                    raise AuthenticationError(
                        "Not authenticated. Please run `qnx login` in your terminal."
                    ) from exc

            auth_response = yield self.build_refresh_request()
            if auth_response.status_code == 401:
                raise AuthenticationError(
                    "Not authenticated. Please run `qnx login` in your terminal."
                )

            auth_response.raise_for_status()
            self.cookies.extract_cookies(auth_response)

            write_token(
                "access_token",
                self.cookies.get("myqos_id", domain=config.domain) or "",
            )
            if request.headers.get("cookie"):
                request.headers.pop("cookie")
            self.cookies.set_cookie_header(request)
            yield request

    def build_refresh_request(self) -> httpx.Request:
        """Build the request for refreshing the id token."""
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


def reload_client() -> None:
    """Reload the nexus client with new tokens."""
    global nexus_client  # pylint: disable=global-statement
    global config  # pylint: disable=global-statement
    config = get_config()
    nexus_client = httpx.Client(
        base_url=config.url,
        auth=AuthHandler(),
        timeout=None,
    )
