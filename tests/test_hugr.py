"""Basic checks for HUGR functionality."""

from pathlib import Path

from hugr.package import Package

import qnexus as qnx


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

    encoded_package = qnx.hugr._encode_hugr(package)  # pylint: disable=protected-access
    decoded_package = qnx.hugr._decode_hugr(  # pylint: disable=protected-access
        encoded_package
    )
    assert encoded_package == qnx.hugr._encode_hugr(  # pylint: disable=protected-access
        decoded_package
    )
