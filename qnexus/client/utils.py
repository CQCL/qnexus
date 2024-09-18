"""Utlity functions for the client."""
# pylint: disable=protected-access
import http
import json
import os
from pathlib import Path
from typing import Any, Literal

from httpx import Response
from pydantic import BaseModel

import qnexus.exceptions as qnx_exc
from qnexus.config import get_config

TokenTypes = Literal["access_token", "refresh_token"]

token_file_from_type = {
    "access_token": "id.json",
    "refresh_token": "token.json",
}


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
    # Don't try to delete refresh token in Jupyterhub
    if is_jupyterhub_environment() and token_type == "refresh_token":
        return
    token_file_path = (
        Path.home() / get_config().token_path / token_file_from_type[token_type]
    )
    if token_file_path.exists():
        token_file_path.unlink()


class RefreshTokenData(BaseModel):
    """Stored refresh token data."""

    delete_version_after: str | None
    refresh_token: str


class RefreshToken(BaseModel):
    """Model for token storage file."""

    data: RefreshTokenData


class AccessTokenData(BaseModel):
    """Stored access token data."""

    access_token: str


class AccessToken(BaseModel):
    """Model for access token storage."""

    data: AccessTokenData


def read_token(token_type: TokenTypes) -> str:
    """Read a token from a file."""
    token_file_path = Path.home() / get_config().token_path
    with (token_file_path / token_file_from_type[token_type]).open(
        encoding="UTF-8"
    ) as file:
        file_contents = file.read().strip()
        if token_type == "access_token":
            return AccessToken(**json.loads(file_contents)).data.access_token
        return RefreshToken(**json.loads(file_contents)).data.refresh_token


def write_token(token_type: TokenTypes, token: str) -> None:
    """Write a token to a file."""

    # don't allow writing of refresh token in Jupyterhub
    if is_jupyterhub_environment() and token_type == "refresh_token":
        return

    token_file_path = Path.home() / get_config().token_path
    token_file_path.mkdir(parents=True, exist_ok=True)
    with (token_file_path / token_file_from_type[token_type]).open(
        encoding="UTF-8", mode="w"
    ) as file:
        if token_type == "access_token":
            file.write(
                AccessToken(data=AccessTokenData(access_token=token)).model_dump_json()
            )
            return
        file.write(
            RefreshToken(
                data=RefreshTokenData(refresh_token=token, delete_version_after=None)
            ).model_dump_json()
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
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)


def is_jupyterhub_environment() -> bool:
    """Check if the module is running in the Nexus JupyterHub."""
    if os.environ.get("JUPYTERHUB_USER"):
        return True
    return False
