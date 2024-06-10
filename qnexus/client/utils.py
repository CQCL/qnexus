"""Utlity functions for the client."""
# pylint: disable=protected-access
import http
import json
from pathlib import Path
from typing import Any, Literal, Optional
from httpx import Response
from pydantic import BaseModel
import qnexus.exceptions as qnx_exc
from qnexus import consts



TokenTypes = Literal["access_token", "refresh_token"]


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


def remove_token(token_type: TokenTypes) -> None:
    """Delete a token file."""
    token_file_path = Path.home() / consts.TOKEN_FILE_PATH / token_type
    if token_file_path.exists():
        token_file_path.unlink()


class Token(BaseModel):
    """Stored token data."""

    delete_version_after: Optional[str]
    refresh_token: str


def read_token(token_type: TokenTypes) -> Token:
    """Read a token from a file."""
    token_file_path = Path.home() / consts.TOKEN_FILE_PATH
    with (token_file_path / token_type).open(encoding="UTF-8") as file:
        file_contents = file.read().strip()
        return Token(**json.loads(file_contents))


def write_token(token_type: TokenTypes, token: str) -> None:
    """Write a token to a file."""

    token_file_path = Path.home() / consts.TOKEN_FILE_PATH
    token_file_path.mkdir(parents=True, exist_ok=True)
    with (token_file_path / token_type).open(encoding="UTF-8", mode="w") as file:
        file.write(
            Token(refresh_token=token, delete_version_after=None).model_dump_json()
        )


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
