"""
setup_wizard_result.py

Resultado global del asistente de configuración
de Meeting Assistant AI.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from services.setup.capabilities.capability_result import (
    CapabilityResult,
    CapabilityStatus,
)


class SetupWizardStatus(str, Enum):

    READY = "READY"
    ATTENTION = "ATTENTION"
    BLOCKED = "BLOCKED"


@dataclass
class SetupWizardResult:

    status: SetupWizardStatus
    message: str

    started_at: datetime
    completed_at: datetime

    capability_results: list[
        CapabilityResult
    ] = field(default_factory=list)

    details: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def can_continue(self) -> bool:

        return self.status in {
            SetupWizardStatus.READY,
            SetupWizardStatus.ATTENTION,
        }

    @property
    def is_ready(self) -> bool:

        return (
            self.status
            == SetupWizardStatus.READY
        )

    @property
    def has_attention_items(self) -> bool:

        return (
            self.status
            == SetupWizardStatus.ATTENTION
        )

    @property
    def is_blocked(self) -> bool:

        return (
            self.status
            == SetupWizardStatus.BLOCKED
        )

    def get_capability(
        self,
        capability_id: str,
    ) -> CapabilityResult | None:

        for result in self.capability_results:

            if (
                result.capability_id
                == capability_id
            ):
                return result

        return None

    def get_unavailable(self) -> list[
        CapabilityResult
    ]:

        return [
            result
            for result in self.capability_results
            if (
                result.status
                == CapabilityStatus.UNAVAILABLE
            )
        ]

    def get_degraded(self) -> list[
        CapabilityResult
    ]:

        return [
            result
            for result in self.capability_results
            if (
                result.status
                == CapabilityStatus.DEGRADED
            )
        ]

    def get_repairable(self) -> list[
        CapabilityResult
    ]:

        return [
            result
            for result in self.capability_results
            if result.repairable
        ]

    def as_dict(self) -> dict:

        return {
            "status": self.status.value,
            "message": self.message,
            "can_continue": self.can_continue,
            "started_at": (
                self.started_at.isoformat()
            ),
            "completed_at": (
                self.completed_at.isoformat()
            ),
            "details": self.details,
            "capabilities": [
                result.as_dict()
                for result
                in self.capability_results
            ],
        }