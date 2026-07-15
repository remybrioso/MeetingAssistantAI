"""
health_result.py

Resultado individual de una comprobación de salud.
"""

from dataclasses import dataclass
from enum import Enum


class HealthStatus(str, Enum):

    OK = "OK"
    WARNING = "WARNING"
    FAILED = "FAILED"


@dataclass
class HealthResult:

    name: str
    status: HealthStatus
    message: str
    details: str | None = None

    @property
    def is_ok(self) -> bool:
        return self.status == HealthStatus.OK

    def as_dict(self) -> dict:

        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
        }
