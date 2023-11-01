from typing import Any, Dict, Literal
import time
from typing import Callable
from pathlib import Path
from httpx import Response
import http
import os

from ..consts import TOKEN_FILE_PATH

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


def read_token_file(token_type: Literal["access_token", "refresh_token"]) -> str:
    """Read a token from a file."""

    token_file_path = Path.home() / TOKEN_FILE_PATH
    with (token_file_path / token_type).open(encoding="UTF-8") as file:
        return file.read().strip()


def write_token_file(token_type: Literal["access_token", "refresh_token"], token: str) -> None:
    """Write a token to a file."""

    token_file_path = Path.home() / TOKEN_FILE_PATH
    token_file_path.mkdir(parents=True, exist_ok=True)
    with (token_file_path / token_type).open(encoding="UTF-8", mode="w") as file:
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
