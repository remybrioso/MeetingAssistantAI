"""
meeting_semantic_coverage_service.py

Reconcilia determinísticamente la cobertura de la consolidación
semántica global contra todos los items fuente de MeetingKnowledge.
"""

from models.chunk_classification import (
    ChunkKnowledgeKind,
)
from models.meeting_knowledge import MeetingKnowledge
from models.meeting_semantic_consolidation import (
    ConsolidatedMeetingKnowledgeItem,
    MeetingKnowledgeItemReference,
    MeetingSemanticConsolidation,
)
from services.meeting_semantic_consolidation_prompt_formatter import (
    MeetingSemanticConsolidationPromptFormatter,
)


class MeetingSemanticCoverageService:
    """
    Completa únicamente referencias fuente omitidas por G1.

    Las referencias inválidas, inventadas, duplicadas, reutilizadas o
    incompatibles con su kind son errores y nunca se reparan aquí.
    """

    def build_identity_consolidation(
        self,
        meeting_knowledge: MeetingKnowledge,
    ) -> MeetingSemanticConsolidation:
        """
        Construye una partición canónica de un item por fuente.
        """

        if not isinstance(
            meeting_knowledge,
            MeetingKnowledge,
        ):
            raise TypeError(
                "meeting_knowledge debe ser una instancia "
                "de MeetingKnowledge."
            )

        expected_sources = (
            self._build_expected_sources(
                meeting_knowledge
            )
        )

        identity_consolidation = (
            MeetingSemanticConsolidation(
                items=[
                    self._build_standalone_item(
                        source
                    )
                    for source in expected_sources
                ]
            )
        )

        self._assert_exact_coverage(
            semantic_consolidation=(
                identity_consolidation
            ),
            expected_keys={
                source_key
                for (
                    source_key,
                    _,
                    _,
                ) in expected_sources
            },
        )

        return identity_consolidation

    def reconcile(
        self,
        semantic_consolidation: MeetingSemanticConsolidation,
        meeting_knowledge: MeetingKnowledge,
    ) -> MeetingSemanticConsolidation:
        if not isinstance(
            semantic_consolidation,
            MeetingSemanticConsolidation,
        ):
            raise TypeError(
                "semantic_consolidation debe ser una instancia "
                "de MeetingSemanticConsolidation."
            )

        if not isinstance(
            meeting_knowledge,
            MeetingKnowledge,
        ):
            raise TypeError(
                "meeting_knowledge debe ser una instancia "
                "de MeetingKnowledge."
            )

        expected_sources = (
            self._build_expected_sources(
                meeting_knowledge
            )
        )

        expected_keys = {
            source_key
            for (
                source_key,
                _,
                _,
            ) in expected_sources
        }

        actual_keys = (
            self._collect_actual_source_keys(
                semantic_consolidation
            )
        )

        self._reject_unexpected_references(
            actual_keys=actual_keys,
            expected_keys=expected_keys,
        )

        missing_sources = [
            source
            for source in expected_sources
            if source[0] not in actual_keys
        ]

        if not missing_sources:
            self._assert_exact_coverage(
                semantic_consolidation=(
                    semantic_consolidation
                ),
                expected_keys=expected_keys,
            )

            return semantic_consolidation

        recovered_items = [
            self._build_standalone_item(
                source
            )
            for source in missing_sources
        ]

        reconciled = (
            MeetingSemanticConsolidation(
                items=[
                    *semantic_consolidation.items,
                    *recovered_items,
                ]
            )
        )

        self._assert_exact_coverage(
            semantic_consolidation=reconciled,
            expected_keys=expected_keys,
        )

        return reconciled

    @staticmethod
    def _build_standalone_item(
        source: tuple[
            tuple[str, int, int],
            ChunkKnowledgeKind,
            str,
        ],
    ) -> ConsolidatedMeetingKnowledgeItem:
        source_key, kind, description = source

        return ConsolidatedMeetingKnowledgeItem(
            kind=kind,
            description=description,
            source_refs=[
                MeetingKnowledgeItemReference(
                    chunk_index=source_key[1],
                    item_index=source_key[2],
                )
            ],
        )

    def _build_expected_sources(
        self,
        meeting_knowledge: MeetingKnowledge,
    ) -> list[
        tuple[
            tuple[str, int, int],
            ChunkKnowledgeKind,
            str,
        ]
    ]:
        expected_sources: list[
            tuple[
                tuple[str, int, int],
                ChunkKnowledgeKind,
                str,
            ]
        ] = []

        catalog = (
            MeetingSemanticConsolidationPromptFormatter
            .build_catalog(
                meeting_knowledge
            )
        )

        for source in catalog:
            kind = ChunkKnowledgeKind.from_value(
                source["kind"]
            )

            expected_sources.append(
                (
                    (
                        kind.value,
                        source["chunk_index"],
                        source["item_index"],
                    ),
                    kind,
                    source["text"],
                )
            )

        return expected_sources

    @staticmethod
    def _collect_actual_source_keys(
        semantic_consolidation: MeetingSemanticConsolidation,
    ) -> set[
        tuple[str, int, int]
    ]:
        actual_keys: set[
            tuple[str, int, int]
        ] = set()

        for item in semantic_consolidation.items:
            for reference in item.source_refs:
                source_key = (
                    item.kind.value,
                    reference.chunk_index,
                    reference.item_index,
                )

                if source_key in actual_keys:
                    raise ValueError(
                        "MeetingSemanticCoverageService no puede "
                        "reconciliar una referencia fuente "
                        "duplicada o reutilizada: "
                        f"{source_key}."
                    )

                actual_keys.add(
                    source_key
                )

        return actual_keys

    @staticmethod
    def _reject_unexpected_references(
        actual_keys: set[
            tuple[str, int, int]
        ],
        expected_keys: set[
            tuple[str, int, int]
        ],
    ) -> None:
        unexpected_keys = (
            actual_keys
            - expected_keys
        )

        if unexpected_keys:
            raise ValueError(
                "MeetingSemanticCoverageService no puede "
                "reconciliar referencias fuente inválidas o "
                "inesperadas: "
                + ", ".join(
                    str(key)
                    for key in sorted(
                        unexpected_keys
                    )
                )
                + "."
            )

    def _assert_exact_coverage(
        self,
        semantic_consolidation: MeetingSemanticConsolidation,
        expected_keys: set[
            tuple[str, int, int]
        ],
    ) -> None:
        actual_keys = (
            self._collect_actual_source_keys(
                semantic_consolidation
            )
        )

        self._reject_unexpected_references(
            actual_keys=actual_keys,
            expected_keys=expected_keys,
        )

        missing_keys = (
            expected_keys
            - actual_keys
        )

        if missing_keys:
            raise ValueError(
                "MeetingSemanticCoverageService requiere "
                "cobertura exacta; faltan referencias fuente: "
                + ", ".join(
                    str(key)
                    for key in sorted(
                        missing_keys
                    )
                )
                + "."
            )
