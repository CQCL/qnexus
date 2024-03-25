from .client import nexus_client


def status():
    """Get summary of current environment."""
    user = nexus_client.get("/api/v6/user/me")
    display_name = user.json()["display_name"]
    user_name = user.json()["user_name"]
    print(f"Signed in as {display_name} ({user_name})")
