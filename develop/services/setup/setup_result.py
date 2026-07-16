"""
setup_result.py

Resultado completo de una ejecución
del Setup & Recovery Engine.
"""

from dataclasses import dataclass, field
from datetime import datetime

from services.setup.task_result import (
    TaskResult,
    TaskStatus,
)


@dataclass
class SetupResult:

    started_at: datetime
    completed_at: datetime
    task_results: list[TaskResult] = field(
        default_factory=list
    )

    @property
    def successful(self) -> bool:

        return all(
            result.status != TaskStatus.FAILED
            for result in self.task_results
        )

    @property
    def failed_tasks(self) -> list[TaskResult]:

        return [
            result
            for result in self.task_results
            if result.status == TaskStatus.FAILED
        ]

    @property
    def restart_required(self) -> bool:

        return any(
            result.restart_required
            for result in self.task_results
        )

    def as_dict(self) -> dict:

        return {
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "successful": self.successful,
            "restart_required": self.restart_required,
            "task_results": [
                result.as_dict()
                for result in self.task_results
            ],
        }