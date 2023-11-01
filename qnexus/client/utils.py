from typing import Any, Dict
import time
from typing import Callable
from pathlib import Path
from httpx import Response
import http
import os


def normalize_included(included: list[Any]) -> Dict[str, Dict[str, Any]]:
    """Convert a JSON API included array into a mapped dict of the form:
    {
        "user": {
            [user_id]: User
        },
        "project": {
            [project_id]: Project
        }
    }
    """
    included_map = {}
    for item in included:
        included_map.setdefault(item["type"], {item["id"]: {}})
        included_map[item["type"]][item["id"]] = item
    return included_map


def read_token_file(path: str) -> str:
    """Read a token from a file."""
    full_path = f"{Path.home()}/{path}"
    if os.path.isfile(full_path):
        with open(full_path, encoding="UTF-8") as file:
            return file.read().strip()
    return ""


def write_token_file(path: str, token: str) -> None:
    """Write a token to a file."""
    full_path = f"{Path.home()}/{path}"
    with open(full_path, encoding="UTF-8", mode="w") as file:
        file.write(token)
    return None


def consolidate_error(res: Response, description: str) -> None:
    """Consolidate as much error-checking of response"""
    # check if token has expired or is generally unauthorized
    resp_json = res.json()
    if res.status_code == http.HTTPStatus.UNAUTHORIZED:
        raise Exception(
            (
                f"Authorization failure attempting: {description}."
                f"\n\nServer Response: {resp_json}"
            )
        )
    if res.status_code != http.HTTPStatus.OK:
        raise Exception(
            f"HTTP error attempting: {description}.\n\nServer Response: {resp_json}"
        )
