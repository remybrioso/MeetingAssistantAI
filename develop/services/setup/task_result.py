"""
task_result.py

Resultado de una tarea ejecutada por
el MAI Setup & Recovery Engine.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskStatus(str, Enum):

    SUCCESS = "SUCCESS"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"


@dataclass
class TaskResult:

    task_id: str
    name: str
    status: TaskStatus
    message: str

    details: dict[str, Any] = field(
        default_factory=dict
    )

    error: str | None = None
    restart_required: bool = False
    verification_required: bool = False

    @property
    def is_successful(self) -> bool:

        return self.status in {
            TaskStatus.SUCCESS,
            TaskStatus.SKIPPED,
        }

    def as_dict(self) -> dict:

        return {
            "task_id": self.task_id,
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "error": self.error,
            "restart_required": self.restart_required,
            "verification_required": (
                self.verification_required
            ),
        }