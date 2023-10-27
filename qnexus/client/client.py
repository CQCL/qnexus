import httpx
from ..config import get_config


config = get_config()


class AuthHandler(httpx.Auth):
    """Custom nexus auth handler"""

    requires_response_body = True

    def __init__(self, refresh_token):
        self.access_token: str = ""
        self.refresh_token: str = refresh_token

    def auth_flow(self, request):
        response = yield request
        if response.status_code == 401:
            # If the server issues a 401 response attempt a refresh,\
            cookies = httpx.Cookies({"myqos_oat": self.refresh_token})
            refresh_response = httpx.Client(base_url=f"{config.url}/auth").post(
                "/tokens/refresh",
                cookies=cookies,
            )
            if refresh_response.status_code == 401:
                print("Your session has expired.")

            cookies.extract_cookies(response=refresh_response)
            self.access_token = cookies["myqos_id"]
            request.headers["Cookie"] = f"myqos_id={cookies['myqos_id']}"
            yield request


config = get_config()
nexus_client = httpx.Client(
    base_url=config.url,
    auth=AuthHandler(
        refresh_token="sfv0iycvv7n6zAzZsDYF-MX7dPeIgUr5W0wWxwkKuyQm81eSpGnPt48p0FL8V3njdBKjAupH394mmvV1U1JaXg"
    ),
)
