"""Basic checks for HUGR functionality."""

from datetime import datetime
from pathlib import Path
import uuid

from hugr.package import Package
import pytest

import qnexus as qnx
from qnexus.exceptions import IncompatibleResultVersion
from qnexus.models.annotations import Annotations
from qnexus.models.references import ExecutionResultRef, ProjectRef, ResultVersions


def test_hugr_encode_decode() -> None:
    """
    Given a known-good binary-encoded HUGR in a file, test that it can be loaded
    into a hugr.package.Package instance, then serialised and deserialised with
    fidelity.

    We expect this test to continue passing when client.hugr.ENVELOPE_CONFIG is
    changed.
    """
    with open(Path(__file__).parent.resolve() / "data" / "hugr.dat", "rb") as fp:
        data = fp.read()
        package = Package.from_bytes(data)

    encoded_package = qnx.hugr._encode_hugr(package)
    decoded_package = qnx.hugr._decode_hugr(encoded_package)
    assert encoded_package == qnx.hugr._encode_hugr(decoded_package)


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
