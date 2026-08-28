"""
chunk_classification.py

Representación intermedia y liviana de la clasificación semántica
de un TranscriptChunk.
"""

from dataclasses import dataclass, field
from enum import Enum
from numbers import Real


class ChunkKnowledgeKind(str, Enum):
    TOPIC = "topic"
    DECISION = "decision"
    ACTION = "action"
    RISK = "risk"
    PENDING = "pending"

    @classmethod
    def from_value(
        cls,
        value: str,
    ) -> "ChunkKnowledgeKind":
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "ChunkKnowledgeKind value debe ser una cadena."
            )

        normalized = value.strip().casefold()

        try:
            return cls(
                normalized
            )
        except ValueError as ex:
            raise ValueError(
                "ChunkKnowledgeKind no contiene un valor válido."
            ) from ex


@dataclass(frozen=True)
class ClassifiedKnowledgeItem:
    kind: ChunkKnowledgeKind
    description: str
    segment_ids: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(
            self.kind,
            ChunkKnowledgeKind,
        ):
            raise TypeError(
                "ClassifiedKnowledgeItem kind debe ser una "
                "instancia de ChunkKnowledgeKind."
            )

        if not isinstance(
            self.description,
            str,
        ):
            raise TypeError(
                "ClassifiedKnowledgeItem description debe ser "
                "una cadena."
            )

        normalized_description = self.description.strip()

        if not normalized_description:
            raise ValueError(
                "ClassifiedKnowledgeItem description no puede "
                "estar vacío."
            )

        object.__setattr__(
            self,
            "description",
            normalized_description,
        )

        if not isinstance(
            self.segment_ids,
            list,
        ):
            raise TypeError(
                "ClassifiedKnowledgeItem segment_ids debe ser "
                "una lista."
            )

        if not self.segment_ids:
            raise ValueError(
                "ClassifiedKnowledgeItem requiere al menos un "
                "segment_id."
            )

        normalized_ids: list[int] = []
        seen_ids: set[int] = set()

        for index, segment_id in enumerate(
            self.segment_ids,
            start=1,
        ):
            if (
                not isinstance(
                    segment_id,
                    int,
                )
                or isinstance(
                    segment_id,
                    bool,
                )
            ):
                raise TypeError(
                    "ClassifiedKnowledgeItem segment_ids elemento "
                    f"#{index} debe ser entero."
                )

            if segment_id < 0:
                raise ValueError(
                    "ClassifiedKnowledgeItem segment_ids elemento "
                    f"#{index} no puede ser negativo."
                )

            if segment_id in seen_ids:
                raise ValueError(
                    "ClassifiedKnowledgeItem segment_ids no puede "
                    "contener valores duplicados."
                )

            seen_ids.add(
                segment_id
            )
            normalized_ids.append(
                segment_id
            )

        object.__setattr__(
            self,
            "segment_ids",
            normalized_ids,
        )

    def as_dict(self) -> dict:
        return {
            "kind": self.kind.value,
            "description": self.description,
            "segment_ids": list(
                self.segment_ids
            ),
        }


@dataclass
class ChunkClassification:
    chunk_index: int
    start: float
    end: float
    items: list[ClassifiedKnowledgeItem] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        self._validate_source_metadata()

        if not isinstance(
            self.items,
            list,
        ):
            raise TypeError(
                "ChunkClassification items debe ser una lista."
            )

        normalized_items = list(
            self.items
        )

        for index, item in enumerate(
            normalized_items,
            start=1,
        ):
            if not isinstance(
                item,
                ClassifiedKnowledgeItem,
            ):
                raise TypeError(
                    "ChunkClassification items elemento "
                    f"#{index} debe ser una instancia de "
                    "ClassifiedKnowledgeItem."
                )

        self.items = normalized_items

    @property
    def has_content(self) -> bool:
        return bool(
            self.items
        )

    def items_of_kind(
        self,
        kind: ChunkKnowledgeKind,
    ) -> list[ClassifiedKnowledgeItem]:
        if not isinstance(
            kind,
            ChunkKnowledgeKind,
        ):
            raise TypeError(
                "kind debe ser una instancia de "
                "ChunkKnowledgeKind."
            )

        return [
            item
            for item in self.items
            if item.kind is kind
        ]

    def as_dict(self) -> dict:
        return {
            "chunk_index": self.chunk_index,
            "start": self.start,
            "end": self.end,
            "items": [
                item.as_dict()
                for item in self.items
            ],
        }

    def _validate_source_metadata(self) -> None:
        if (
            not isinstance(
                self.chunk_index,
                int,
            )
            or isinstance(
                self.chunk_index,
                bool,
            )
        ):
            raise TypeError(
                "ChunkClassification chunk_index debe ser entero."
            )

        if self.chunk_index < 0:
            raise ValueError(
                "ChunkClassification chunk_index no puede ser "
                "negativo."
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
                "ChunkClassification end no puede ser menor "
                "que start."
            )

    @staticmethod
    def _normalize_timestamp(
        value,
        field_name: str,
    ) -> float:
        if (
            not isinstance(
                value,
                Real,
            )
            or isinstance(
                value,
                bool,
            )
        ):
            raise TypeError(
                "ChunkClassification "
                f"{field_name} debe ser numérico."
            )

        normalized_value = float(
            value
        )

        if normalized_value < 0:
            raise ValueError(
                "ChunkClassification "
                f"{field_name} no puede ser negativo."
            )

        return normalized_value
