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
        user = nexus_client.get("/api/v6/user/me")
        if user.status_code == 401:
            return "Not authorized"
        res = nexus_client.get("/health").json()

    if res["status"] == "ok":
        return f"""
            Signed in as {user.json()["display_name"]} ({user.json()["user_name"]})
            Current Project: {config.project_name}
        """
    return Fore.RED + "🛑 Offline"
