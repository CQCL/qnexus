"""Language options for remote job submission."""

from enum import Enum


class Language(str, Enum):
    """Enumeration for the possible submission languages for remote submissions."""

    AUTO = "AUTO"
    QASM = "OPENQASM 2.0"
    QIR = "QIR 1.0"
