"""Basic checks for HUGR functionality."""

import uuid
from datetime import datetime

import pytest

from qnexus.exceptions import IncompatibleResultVersion
from qnexus.models.annotations import Annotations
from qnexus.models.references import ExecutionResultRef, ProjectRef, ResultVersions


def test_raises_when_trying_to_get_raw_results_from_pytket_result() -> None:
    """Given an ExecutionResultRef to a pytket result, it will raise an error
    if the user tries to get anything other than the default results."""

    ref = ExecutionResultRef(
        id=uuid.uuid4(),
        annotations=Annotations(),
        project=ProjectRef(
            id=uuid.uuid4(), annotations=Annotations(), contents_modified=datetime.now()
        ),
    )

    with pytest.raises(IncompatibleResultVersion):
        ref.download_result(version=ResultVersions.RAW)
