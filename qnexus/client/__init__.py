"""Client API for Nexus."""

import typing

import httpx

from qnexus.client.utils import read_token, write_token
from qnexus.config import CONFIG
from qnexus.exceptions import AuthenticationError


class AuthHandler(httpx.Auth):
    """Custom nexus auth handler"""

    cookies: httpx.Cookies

    def __init__(self) -> None:
        self.cookies = httpx.Cookies()
        self.reload_tokens()

        super().__init__()

    def reload_tokens(self) -> None:
        """Clear tokens and attempt to reload from the file system."""
        try:
            self.cookies.clear()
            token = read_token("refresh_token")
            self.cookies.set("myqos_oat", token, domain=CONFIG.domain)
            id_token = read_token("access_token")
            self.cookies.set("myqos_id", id_token, domain=CONFIG.domain)
        except FileNotFoundError:
            pass

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
                    self.cookies.set("myqos_oat", token, domain=CONFIG.domain)
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
                self.cookies.get("myqos_id", domain=CONFIG.domain) or "",
            )
            if request.headers.get("cookie"):
                request.headers.pop("cookie")
            self.cookies.set_cookie_header(request)
            yield request

    def build_refresh_request(self) -> httpx.Request:
        """Build the request for refreshing the id token."""
        self.cookies.delete("myqos_id")  # We need to delete any existing id token first
        return httpx.Request(
            method="POST",
            url=f"{CONFIG.url}/auth/tokens/refresh",
            cookies=self.cookies,
        )


_nexus_client: httpx.Client | None = None


def get_nexus_client(reload: bool = False) -> httpx.Client:
    """Getter function for the nexus client.
    Args:
        reload: If True, reconstruct the client (and auth tokens).
    Returns:
        httpx.Client: The nexus client.
    """
    global _nexus_client
    if _nexus_client is None or reload:
        _auth_handler = AuthHandler()
        _auth_handler.reload_tokens()

        _nexus_client = httpx.Client(
            base_url=CONFIG.url,
            auth=_auth_handler,
            timeout=None,
            verify=CONFIG.httpx_verify,
        )
    return _nexus_client
