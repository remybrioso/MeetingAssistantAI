"""Severity levels for recovery experiences."""

from enum import Enum


class Severity(str, Enum):
    """Represents how strongly an issue affects MAI operation."""

    INFO = "info"
    RECOMMENDED = "recommended"
    WARNING = "warning"
    CRITICAL = "critical"
