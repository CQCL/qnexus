"""Utlity functions for the client."""

import http
import os
from pathlib import Path
from typing import Any, Literal

from httpx import Response

import qnexus.exceptions as qnx_exc
from qnexus import consts

_in_memory_refresh_token: str | None = None
_in_memory_access_token: str | None = None


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


def write_token(
    token_type: Literal["access_token", "refresh_token"], token: str
) -> None:
    """Write a token to a file."""
    if consts.STORE_TOKENS:
        _write_token_file(token_type, token)
    match token_type:
        case "access_token":
            _in_memory_access_token = token
        case "refresh_token":
            _in_memory_refresh_token = token


def read_token(token_type: Literal["access_token", "refresh_token"]) -> str:
    """Read a token from a file."""
    if consts.STORE_TOKENS:
        return _read_token_file(token_type)
    match token_type:
        case "access_token":
            if _in_memory_access_token:
                return _in_memory_access_token
        case "refresh_token":
            if _in_memory_refresh_token:
                return _in_memory_refresh_token
    raise FileNotFoundError


def remove_token(token_type: Literal["access_token", "refresh_token"]) -> None:
    """Delete a token file."""
    token_file_path = Path.home() / consts.TOKEN_FILE_PATH / token_type
    if token_file_path.exists():
        token_file_path.unlink()


def _read_token_file(token_type: Literal["access_token", "refresh_token"]) -> str:
    """Read a token from a file."""

    token_file_path = Path.home() / consts.TOKEN_FILE_PATH
    with (token_file_path / token_type).open(encoding="UTF-8") as file:
        return file.read().strip()


def _write_token_file(
    token_type: Literal["access_token", "refresh_token"], token: str
) -> None:
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
