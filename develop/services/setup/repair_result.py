"""
repair_result.py

Resultado de una ejecución de reparación solicitada
desde el Setup Wizard de Meeting Assistant AI.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RepairExecutionStatus(str, Enum):

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    UNSUPPORTED = "UNSUPPORTED"
    USER_ACTION_REQUIRED = "USER_ACTION_REQUIRED"


@dataclass(frozen=True)
class RepairExecutionResult:

    action: str
    status: RepairExecutionStatus
    message: str
    details: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def succeeded(self) -> bool:
        return (
            self.status
            == RepairExecutionStatus.SUCCESS
        )

    @property
    def failed(self) -> bool:
        return (
            self.status
            == RepairExecutionStatus.FAILED
        )

    @property
    def unsupported(self) -> bool:
        return (
            self.status
            == RepairExecutionStatus.UNSUPPORTED
        )

    @property
    def user_action_required(self) -> bool:
        return (
            self.status
            == RepairExecutionStatus.USER_ACTION_REQUIRED
        )
