"""Automatic recovery action domain model."""

from dataclasses import dataclass
from enum import Enum


class AutomaticActionType(str, Enum):
    """Execution behavior exposed by an automatic recovery action."""

    ONE_CLICK = "one_click"
    CONFIRMATION_REQUIRED = "confirmation_required"
    BACKGROUND = "background"


@dataclass(frozen=True, slots=True)
class AutomaticAction:
    """Metadata describing an automatic recovery action.

    The model contains no execution logic. Execution belongs to a future
    automatic recovery service and registry.
    """

    action_id: str
    label: str
    description: str
    action_type: AutomaticActionType = AutomaticActionType.CONFIRMATION_REQUIRED
    requires_elevation: bool = False
    destructive: bool = False

    def __post_init__(self) -> None:
        if not self.action_id.strip():
            raise ValueError("AutomaticAction.action_id cannot be empty.")
        if not self.label.strip():
            raise ValueError("AutomaticAction.label cannot be empty.")
        if not self.description.strip():
            raise ValueError("AutomaticAction.description cannot be empty.")
        if self.destructive and self.action_type is AutomaticActionType.BACKGROUND:
            raise ValueError(
                "Destructive actions cannot execute as background actions."
            )
