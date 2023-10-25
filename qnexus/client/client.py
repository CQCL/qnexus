import httpx
from ..config import get_config

config = get_config()
nexus_client = httpx.Client(base_url=config.url)
