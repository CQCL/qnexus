"""Additional tests for references."""

from typing import get_args

from qnexus.models.references import BaseRef, Ref


def test_base_ref() -> None:
    """Test that all subclasses of BaseRef are the same
    as the generic Ref Union type."""

    all_base_refs = set(BaseRef.__subclasses__())

    all_refs = set(get_args(Ref.__args__[0]))  # type: ignore

    assert all_base_refs == all_refs
