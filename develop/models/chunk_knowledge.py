"""
chunk_knowledge.py

Representación intermedia del conocimiento extraído de un
TranscriptChunk.
"""

from dataclasses import dataclass, field
from numbers import Real
from typing import TypeVar

from models.meeting_report import (
    ActionItem,
    Decision,
    MeetingRisk,
    MeetingTopic,
    Participant,
    PendingItem,
)

ItemType = TypeVar("ItemType")


@dataclass
class ChunkKnowledge:
    chunk_index: int
    start: float
    end: float

    key_points: list[str] = field(default_factory=list)
    topics: list[MeetingTopic] = field(default_factory=list)
    decisions: list[Decision] = field(default_factory=list)
    action_items: list[ActionItem] = field(default_factory=list)
    risks: list[MeetingRisk] = field(default_factory=list)
    pending_items: list[PendingItem] = field(default_factory=list)
    participants: list[Participant] = field(default_factory=list)
    conclusions: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate_source_metadata()

        self.key_points = self._normalize_text_collection(
            self.key_points,
            "key_points",
        )
        self.conclusions = self._normalize_text_collection(
            self.conclusions,
            "conclusions",
        )

        self.topics = self._validate_domain_collection(
            self.topics,
            MeetingTopic,
            "topics",
        )
        self.decisions = self._validate_domain_collection(
            self.decisions,
            Decision,
            "decisions",
        )
        self.action_items = self._validate_domain_collection(
            self.action_items,
            ActionItem,
            "action_items",
        )
        self.risks = self._validate_domain_collection(
            self.risks,
            MeetingRisk,
            "risks",
        )
        self.pending_items = self._validate_domain_collection(
            self.pending_items,
            PendingItem,
            "pending_items",
        )
        self.participants = self._validate_domain_collection(
            self.participants,
            Participant,
            "participants",
        )

        self._validate_evidence_ranges()

    @property
    def has_content(self) -> bool:
        return any(
            (
                self.key_points,
                self.topics,
                self.decisions,
                self.action_items,
                self.risks,
                self.pending_items,
                self.participants,
                self.conclusions,
            )
        )

    def as_dict(self) -> dict:
        return {
            "chunk_index": self.chunk_index,
            "start": self.start,
            "end": self.end,
            "key_points": list(self.key_points),
            "topics": [item.as_dict() for item in self.topics],
            "decisions": [item.as_dict() for item in self.decisions],
            "action_items": [item.as_dict() for item in self.action_items],
            "risks": [item.as_dict() for item in self.risks],
            "pending_items": [
                item.as_dict()
                for item in self.pending_items
            ],
            "participants": [
                item.as_dict()
                for item in self.participants
            ],
            "conclusions": list(self.conclusions),
        }

    def _validate_source_metadata(self) -> None:
        if (
            not isinstance(self.chunk_index, int)
            or isinstance(self.chunk_index, bool)
        ):
            raise TypeError(
                "ChunkKnowledge chunk_index debe ser entero."
            )

        if self.chunk_index < 0:
            raise ValueError(
                "ChunkKnowledge chunk_index no puede ser negativo."
            )

        self.start = self._normalize_timestamp(
            self.start,
            "start",
        )
        self.end = self._normalize_timestamp(
            self.end,
            "end",
        )

        if self.end < self.start:
            raise ValueError(
                "ChunkKnowledge end no puede ser menor que start."
            )

    @staticmethod
    def _normalize_timestamp(
        value,
        field_name: str,
    ) -> float:
        if (
            not isinstance(value, Real)
            or isinstance(value, bool)
        ):
            raise TypeError(
                f"ChunkKnowledge {field_name} debe ser numérico."
            )

        value = float(value)

        if value < 0:
            raise ValueError(
                f"ChunkKnowledge {field_name} no puede ser negativo."
            )

        return value

    @staticmethod
    def _normalize_text_collection(
        values,
        field_name: str,
    ) -> list[str]:
        if not isinstance(values, list):
            raise TypeError(
                f"ChunkKnowledge {field_name} debe ser una lista."
            )

        normalized_values = []

        for index, value in enumerate(values, start=1):
            if not isinstance(value, str):
                raise TypeError(
                    f"ChunkKnowledge {field_name} elemento "
                    f"#{index} debe ser una cadena."
                )

            normalized = value.strip()

            if not normalized:
                raise ValueError(
                    f"ChunkKnowledge {field_name} elemento "
                    f"#{index} no puede estar vacío."
                )

            normalized_values.append(normalized)

        return normalized_values

    @staticmethod
    def _validate_domain_collection(
        values,
        expected_type: type[ItemType],
        field_name: str,
    ) -> list[ItemType]:
        if not isinstance(values, list):
            raise TypeError(
                f"ChunkKnowledge {field_name} debe ser una lista."
            )

        normalized_values = list(values)

        for index, value in enumerate(
            normalized_values,
            start=1,
        ):
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"ChunkKnowledge {field_name} elemento "
                    f"#{index} debe ser una instancia de "
                    f"{expected_type.__name__}."
                )

        return normalized_values

    def _validate_evidence_ranges(self) -> None:
        collections = (
            ("topics", self.topics),
            ("decisions", self.decisions),
            ("action_items", self.action_items),
            ("risks", self.risks),
            ("pending_items", self.pending_items),
        )

        for field_name, items in collections:
            for item_index, item in enumerate(
                items,
                start=1,
            ):
                for evidence_index, reference in enumerate(
                    item.evidence,
                    start=1,
                ):
                    if (
                        reference.start < self.start
                        or reference.end > self.end
                    ):
                        raise ValueError(
                            "ChunkKnowledge "
                            f"{field_name} elemento "
                            f"#{item_index} evidence elemento "
                            f"#{evidence_index} está fuera "
                            "del rango temporal del chunk."
                        )
