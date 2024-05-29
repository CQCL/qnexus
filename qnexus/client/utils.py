"""Utlity functions for the client."""
# pylint: disable=protected-access
import http
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from httpx import Response

from qnexus import consts
from qnexus.client.models.utils import assert_never
import qnexus.exceptions as qnx_exc

TokenTypes = Literal["access_token", "refresh_token"]


@dataclass
class MemoryTokenStore:
    """Simple store for in-memory token storage."""

    in_memory_refresh_token: str | None = None
    in_memory_access_token: str | None = None

    def remove_token(self, token_type: TokenTypes):
        "Remove an in-memory token"
        match token_type:
            case "access_token":
                self.in_memory_access_token = None
            case "refresh_token":
                self.in_memory_refresh_token = None
            case _:
                assert_never(token_type)


_memory_token_store = MemoryTokenStore()


def normalize_included(included: list[Any]) -> dict[str, dict[str, Any]]:
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
    included_map: dict[str, dict[str, Any]] = {}
    for item in included:
        included_map.setdefault(item["type"], {item["id"]: {}})
        included_map[item["type"]][item["id"]] = item
    return included_map


def write_token(token_type: TokenTypes, token: str) -> None:
    """Write a token to a file."""
    if consts.STORE_TOKENS:
        _write_token_file(token_type, token)
    match token_type:
        case "access_token":
            _memory_token_store.in_memory_access_token = token
        case "refresh_token":
            _memory_token_store.in_memory_refresh_token = token


def read_token(token_type: TokenTypes) -> str:
    """Read a token from a file."""
    print(consts.STORE_TOKENS)
    if consts.STORE_TOKENS:
        return _read_token_file(token_type)
    match token_type:
        case "access_token":
            if _memory_token_store.in_memory_access_token:
                return _memory_token_store.in_memory_access_token
        case "refresh_token":
            if _memory_token_store.in_memory_refresh_token:
                return _memory_token_store.in_memory_refresh_token
    raise FileNotFoundError


def remove_token(token_type: TokenTypes) -> None:
    """Delete a token file."""
    _memory_token_store.remove_token(token_type)
    token_file_path = Path.home() / consts.TOKEN_FILE_PATH / token_type
    if token_file_path.exists():
        token_file_path.unlink()


def _read_token_file(token_type: TokenTypes) -> str:
    """Read a token from a file."""

    token_file_path = Path.home() / consts.TOKEN_FILE_PATH
    with (token_file_path / token_type).open(encoding="UTF-8") as file:
        return file.read().strip()


def _write_token_file(token_type: TokenTypes, token: str) -> None:
    """Write a token to a file."""

    token_file_path = Path.home() / consts.TOKEN_FILE_PATH
    token_file_path.mkdir(parents=True, exist_ok=True)
    with (token_file_path / token_type).open(encoding="UTF-8", mode="w") as file:
        file.write(token)


def consolidate_error(res: Response, description: str) -> None:
    """Consolidate as much error-checking of response"""
    # check if token has expired or is generally unauthorized
    resp_json = res.json()
    if res.status_code == http.HTTPStatus.UNAUTHORIZED:
        raise qnx_exc.AuthenticationError(
            (
                f"Authorization failure attempting: {description}."
                f"\n\nServer Response: {resp_json}"
            )
        )
    if res.status_code != http.HTTPStatus.OK:
        raise qnx_exc.AuthenticationError(
            f"HTTP error attempting: {description}.\n\nServer Response: {resp_json}"
        )


def handle_fetch_errors(res: Response) -> None:
    """Handle errors related to a fetch request."""

    if res.status_code == 404:
        raise qnx_exc.ZeroMatches()

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(
            message=res.json(), status_code=res.status_code
        )
