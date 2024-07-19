"""Utilities for qnexus-filesystem interactions."""

import json
from pathlib import Path

from qnexus.models.references import Ref, deserialize_nexus_ref


def save(ref: Ref, path: Path, mkdir: bool = False) -> None:
    """Save a Nexus Ref to a file."""
    if mkdir:
        path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(ref.model_dump_json())


def load(path: Path) -> Ref:
    """Load a Nexus Ref from a file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return deserialize_nexus_ref(data)
