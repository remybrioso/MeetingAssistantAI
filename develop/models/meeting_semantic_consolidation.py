"""
meeting_semantic_consolidation.py

Representación intermedia de la consolidación semántica global
de MeetingKnowledge mediante referencias a items fuente.
"""

from dataclasses import dataclass, field

from models.chunk_classification import ChunkKnowledgeKind


@dataclass(
    frozen=True,
    slots=True,
)
class MeetingKnowledgeItemReference:
    """
    Referencia estable a un item semántico dentro de un chunk.

    kind no forma parte de la referencia porque pertenece al
    ConsolidatedMeetingKnowledgeItem que la contiene.
    """

    chunk_index: int
    item_index: int

    def __post_init__(self) -> None:
        self._validate_index(
            value=self.chunk_index,
            field_name="chunk_index",
        )
        self._validate_index(
            value=self.item_index,
            field_name="item_index",
        )

    @staticmethod
    def _validate_index(
        value,
        field_name: str,
    ) -> None:
        if (
            not isinstance(
                value,
                int,
            )
            or isinstance(
                value,
                bool,
            )
        ):
            raise TypeError(
                "MeetingKnowledgeItemReference "
                f"{field_name} debe ser entero."
            )

        if value < 0:
            raise ValueError(
                "MeetingKnowledgeItemReference "
                f"{field_name} no puede ser negativo."
            )

    def as_dict(self) -> dict:
        return {
            "chunk_index": self.chunk_index,
            "item_index": self.item_index,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class ConsolidatedMeetingKnowledgeItem:
    """
    Item semántico global respaldado por uno o más items fuente.
    """

    kind: ChunkKnowledgeKind
    description: str
    source_refs: list[
        MeetingKnowledgeItemReference
    ] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.kind,
            ChunkKnowledgeKind,
        ):
            raise TypeError(
                "ConsolidatedMeetingKnowledgeItem kind debe ser "
                "una instancia de ChunkKnowledgeKind."
            )

        if not isinstance(
            self.description,
            str,
        ):
            raise TypeError(
                "ConsolidatedMeetingKnowledgeItem description "
                "debe ser una cadena."
            )

        normalized_description = (
            self.description.strip()
        )

        if not normalized_description:
            raise ValueError(
                "ConsolidatedMeetingKnowledgeItem description "
                "no puede estar vacío."
            )

        object.__setattr__(
            self,
            "description",
            normalized_description,
        )

        if not isinstance(
            self.source_refs,
            list,
        ):
            raise TypeError(
                "ConsolidatedMeetingKnowledgeItem source_refs "
                "debe ser una lista."
            )

        if not self.source_refs:
            raise ValueError(
                "ConsolidatedMeetingKnowledgeItem requiere "
                "al menos una source_ref."
            )

        normalized_refs = list(
            self.source_refs
        )
        seen_refs: set[tuple[int, int]] = set()

        for index, reference in enumerate(
            normalized_refs,
            start=1,
        ):
            if not isinstance(
                reference,
                MeetingKnowledgeItemReference,
            ):
                raise TypeError(
                    "ConsolidatedMeetingKnowledgeItem "
                    "source_refs elemento "
                    f"#{index} debe ser una instancia de "
                    "MeetingKnowledgeItemReference."
                )

            key = (
                reference.chunk_index,
                reference.item_index,
            )

            if key in seen_refs:
                raise ValueError(
                    "ConsolidatedMeetingKnowledgeItem "
                    "source_refs no puede contener "
                    "referencias duplicadas."
                )

            seen_refs.add(
                key
            )

        object.__setattr__(
            self,
            "source_refs",
            normalized_refs,
        )

    def as_dict(self) -> dict:
        return {
            "kind": self.kind.value,
            "description": self.description,
            "source_refs": [
                reference.as_dict()
                for reference in self.source_refs
            ],
        }


@dataclass
class MeetingSemanticConsolidation:
    """
    Resultado estructurado de la etapa global G1.

    La cobertura frente al MeetingKnowledge original se valida
    en el parser, donde el contexto fuente está disponible.
    """

    items: list[
        ConsolidatedMeetingKnowledgeItem
    ] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.items,
            list,
        ):
            raise TypeError(
                "MeetingSemanticConsolidation items "
                "debe ser una lista."
            )

        normalized_items = list(
            self.items
        )
        seen_source_keys: set[
            tuple[str, int, int]
        ] = set()

        for index, item in enumerate(
            normalized_items,
            start=1,
        ):
            if not isinstance(
                item,
                ConsolidatedMeetingKnowledgeItem,
            ):
                raise TypeError(
                    "MeetingSemanticConsolidation items elemento "
                    f"#{index} debe ser una instancia de "
                    "ConsolidatedMeetingKnowledgeItem."
                )

            for reference in item.source_refs:
                source_key = (
                    item.kind.value,
                    reference.chunk_index,
                    reference.item_index,
                )

                if source_key in seen_source_keys:
                    raise ValueError(
                        "MeetingSemanticConsolidation no puede "
                        "reutilizar una referencia fuente en "
                        "más de un item consolidado."
                    )

                seen_source_keys.add(
                    source_key
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
    ) -> list[
        ConsolidatedMeetingKnowledgeItem
    ]:
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
            "items": [
                item.as_dict()
                for item in self.items
            ],
        }
