"""
capability_result.py

Resultado funcional de una capacidad de MAI.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from services.setup.task_result import TaskResult


class CapabilityStatus(str, Enum):

    AVAILABLE = "AVAILABLE"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass
class CapabilityResult:

    capability_id: str
    name: str
    status: CapabilityStatus
    message: str

    task_results: list[TaskResult] = field(
        default_factory=list
    )

    details: dict[str, Any] = field(
        default_factory=dict
    )

    repairable: bool = False
    repair_action: str | None = None

    @property
    def is_available(self) -> bool:

        return (
            self.status
            == CapabilityStatus.AVAILABLE
        )

    def as_dict(self) -> dict:

        return {
            "capability_id": self.capability_id,
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "repairable": self.repairable,
            "repair_action": self.repair_action,
            "details": self.details,
            "task_results": [
                result.as_dict()
                for result in self.task_results
            ],
        }
