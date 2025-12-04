from pathlib import Path
from typing import Generator
from pact import Pact

import pytest


@pytest.fixture
def pact() -> Generator[Pact, None, None]:
    pact = Pact("QNexus", "Stipe").with_specification("V3")
    yield pact
    pact.write_file(Path(__file__).parent.parent / "pacts")
