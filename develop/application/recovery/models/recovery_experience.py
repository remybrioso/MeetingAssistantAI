"""Aggregate root for a user-facing recovery experience."""

from dataclasses import dataclass
from datetime import timedelta

from .automatic_action import AutomaticAction
from .difficulty import Difficulty
from .help_link import HelpLink
from .recovery_step import RecoveryStep
from .severity import Severity


@dataclass(frozen=True, slots=True)
class RecoveryExperience:
    """Complete user-facing description of how MAI handles an issue.

    This immutable aggregate contains presentation-ready domain data but
    has no dependency on UI frameworks, files, JSON, services, or logging.
    """

    recovery_id: str
    title: str
    summary: str
    explanation: str
    impact: str
    severity: Severity
    difficulty: Difficulty
    estimated_time: timedelta | None
    can_continue: bool
    steps: tuple[RecoveryStep, ...] = ()
    automatic_actions: tuple[AutomaticAction, ...] = ()
    help_links: tuple[HelpLink, ...] = ()
    icon_resource: str | None = None

    def __post_init__(self) -> None:
        required = {
            "recovery_id": self.recovery_id,
            "title": self.title,
            "summary": self.summary,
            "explanation": self.explanation,
            "impact": self.impact,
        }
        for field_name, value in required.items():
            if not value.strip():
                raise ValueError(
                    f"RecoveryExperience.{field_name} cannot be empty."
                )

        if self.estimated_time is not None and self.estimated_time.total_seconds() < 0:
            raise ValueError(
                "RecoveryExperience.estimated_time cannot be negative."
            )

        orders = [step.order for step in self.steps]
        if len(orders) != len(set(orders)):
            raise ValueError("RecoveryExperience step orders must be unique.")

        if orders and orders != sorted(orders):
            raise ValueError(
                "RecoveryExperience steps must be ordered by step.order."
            )

        action_ids = [action.action_id for action in self.automatic_actions]
        if len(action_ids) != len(set(action_ids)):
            raise ValueError(
                "RecoveryExperience automatic action IDs must be unique."
            )
