"""Recovery step domain model."""

from dataclasses import dataclass
from enum import Enum


class RecoveryStepType(str, Enum):
    """Supported presentation types for a recovery step."""

    INSTRUCTION = "instruction"
    VALIDATION = "validation"
    INFORMATION = "information"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class RecoveryStep:
    """One ordered instruction or validation in a recovery experience.

    Attributes:
        order: One-based display order.
        title: Short user-facing heading.
        description: Clear instruction or explanation.
        step_type: Semantic purpose of the step.
        optional: Whether the user may skip the step.
        image_resource: Optional resource identifier for an illustration.
    """

    order: int
    title: str
    description: str
    step_type: RecoveryStepType = RecoveryStepType.INSTRUCTION
    optional: bool = False
    image_resource: str | None = None

    def __post_init__(self) -> None:
        if self.order < 1:
            raise ValueError("RecoveryStep.order must be greater than zero.")
        if not self.title.strip():
            raise ValueError("RecoveryStep.title cannot be empty.")
        if not self.description.strip():
            raise ValueError("RecoveryStep.description cannot be empty.")
