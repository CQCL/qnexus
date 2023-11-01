from .client import nexus_client
from colorama import Fore
from ..config import get_config
from rich.console import Console

console = Console()
# from rich


def status():
    """Get QNexus health"""

    with console.status("[bold green]", speed=2.5) as status:
        config = get_config()
        res = nexus_client.get("/health").json()
        user = nexus_client.get("/api/v6/user/me").json()
    if res["status"] == "ok":
        return f"""
            Signed in as {user["display_name"]} ({user["user_name"]})
            Current Project: {config.project_name}
        """
    return Fore.RED + "🛑 Offline"
