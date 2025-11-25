"""Enum for scope. Separate file to avoid circular imports."""

from enum import Enum


class ScopeFilterEnum(str, Enum):
    """ScopeFilterEnum model."""

    USER = "user"
    ORG_ADMIN = "org_admin"
    GLOBAL_ADMIN = "global_admin"
    HIGHEST = "highest"
