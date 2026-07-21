"""Difficulty levels for user-guided recovery."""

from enum import Enum


class Difficulty(str, Enum):
    """Represents the expected complexity of a recovery procedure."""

    AUTOMATIC = "automatic"
    EASY = "easy"
    MODERATE = "moderate"
    ADVANCED = "advanced"
