from .client import nexus_client
from colorama import Fore
from ..config import get_config


def status():
    """Get QNexus health"""
    config = get_config()
    res = nexus_client.get("/health").json()
    if res["status"] == "ok":
        return Fore.GREEN + f"✅  {config.url} is up and reachable"
    return Fore.RED + "🛑 Offline"
