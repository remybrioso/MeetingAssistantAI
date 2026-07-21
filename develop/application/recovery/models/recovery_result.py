"""Result returned after a recovery operation or user decision."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Mapping


class RecoveryResultStatus(str, Enum):
    """Outcome of a recovery attempt."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class RecoveryResult:
    """Immutable outcome produced by recovery orchestration.

    Details are intended for structured diagnostics and must not contain
    secrets or raw exception objects.
    """

    recovery_id: str
    status: RecoveryResultStatus
    message: str = ""
    action_id: str | None = None
    details: Mapping[str, str] = field(default_factory=dict)
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if not self.recovery_id.strip():
            raise ValueError("RecoveryResult.recovery_id cannot be empty.")
        if self.occurred_at.tzinfo is None:
            raise ValueError("RecoveryResult.occurred_at must be timezone-aware.")

        sanitized = {
            str(key): str(value)
            for key, value in self.details.items()
        }
        object.__setattr__(
            self,
            "details",
            MappingProxyType(sanitized),
        )
