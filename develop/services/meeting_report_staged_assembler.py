"""
meeting_report_staged_assembler.py

Construye MeetingReport de forma determinista a partir de:

- MeetingKnowledge original;
- MeetingSemanticConsolidation (G1);
- MeetingReportNarrative (G2).

No realiza llamadas al proveedor de IA y no reinterpreta el contenido.
"""

from models.artifacts.meeting_report import MeetingReport
from models.chunk_classification import (
    ChunkKnowledgeKind,
)
from models.meeting_knowledge import MeetingKnowledge
from models.meeting_report import (
    ActionItem,
    ActionStatus,
    Decision,
    EvidenceReference,
    MeetingRisk,
    MeetingTopic,
    PendingItem,
)
from models.meeting_report_narrative import (
    GroundedNarrativeText,
    MeetingReportNarrative,
)
from models.meeting_semantic_consolidation import (
    ConsolidatedMeetingKnowledgeItem,
    MeetingSemanticConsolidation,
)


class MeetingReportStagedAssembler:
    """
    Ensambla el artefacto final sin delegar estructura al LLM.

    Responsabilidades:

    - revalidar referencias G1 contra MeetingKnowledge;
    - exigir cobertura exacta de los items semánticos fuente;
    - reconstruir evidence en orden y sin duplicados;
    - reconstruir owner/due_date/status de acciones;
    - rechazar fusiones de acciones con metadata incompatible;
    - validar referencias G2 contra los items consolidados;
    - construir MeetingReport con narrativa G2 y dominio reconstruido.
    """

    KIND_TO_SECTION = {
        ChunkKnowledgeKind.TOPIC: (
            "topics"
        ),
        ChunkKnowledgeKind.DECISION: (
            "decisions"
        ),
        ChunkKnowledgeKind.ACTION: (
            "action_items"
        ),
        ChunkKnowledgeKind.RISK: (
            "risks"
        ),
        ChunkKnowledgeKind.PENDING: (
            "pending_items"
        ),
    }

    def assemble(
        self,
        meeting_knowledge: MeetingKnowledge,
        semantic_consolidation: MeetingSemanticConsolidation,
        narrative: MeetingReportNarrative,
        provider: str,
        model: str,
        prompt_version: str,
    ) -> MeetingReport:
        self._validate_input_types(
            meeting_knowledge=(
                meeting_knowledge
            ),
            semantic_consolidation=(
                semantic_consolidation
            ),
            narrative=narrative,
        )

        normalized_provider = (
            self._normalize_metadata_text(
                value=provider,
                field_name="provider",
            )
        )
        normalized_model = (
            self._normalize_metadata_text(
                value=model,
                field_name="model",
            )
        )
        normalized_prompt_version = (
            self._normalize_metadata_text(
                value=prompt_version,
                field_name="prompt_version",
            )
        )

        self._validate_semantic_coverage(
            meeting_knowledge=(
                meeting_knowledge
            ),
            semantic_consolidation=(
                semantic_consolidation
            ),
        )

        self._validate_narrative_references(
            narrative=narrative,
            semantic_consolidation=(
                semantic_consolidation
            ),
        )

        topics: list[MeetingTopic] = []
        decisions: list[Decision] = []
        action_items: list[ActionItem] = []
        risks: list[MeetingRisk] = []
        pending_items: list[PendingItem] = []

        for item in (
            semantic_consolidation.items
        ):
            source_items = (
                self._resolve_source_items(
                    meeting_knowledge=(
                        meeting_knowledge
                    ),
                    item=item,
                )
            )

            evidence = (
                self._collect_unique_evidence(
                    source_items
                )
            )

            if not evidence:
                raise ValueError(
                    "MeetingReportStagedAssembler requiere "
                    "evidencia fuente para cada item "
                    "semántico consolidado."
                )

            if (
                item.kind
                is ChunkKnowledgeKind.TOPIC
            ):
                topics.append(
                    MeetingTopic(
                        title=item.description,
                        summary=item.description,
                        evidence=evidence,
                    )
                )
                continue

            if (
                item.kind
                is ChunkKnowledgeKind.DECISION
            ):
                decisions.append(
                    Decision(
                        description=item.description,
                        rationale=None,
                        evidence=evidence,
                    )
                )
                continue

            if (
                item.kind
                is ChunkKnowledgeKind.ACTION
            ):
                (
                    owner,
                    due_date,
                    status,
                ) = self._resolve_action_metadata(
                    source_items
                )

                action_items.append(
                    ActionItem(
                        description=item.description,
                        evidence=evidence,
                        owner=owner,
                        due_date=due_date,
                        status=status,
                    )
                )
                continue

            if (
                item.kind
                is ChunkKnowledgeKind.RISK
            ):
                risks.append(
                    MeetingRisk(
                        description=item.description,
                        impact=None,
                        evidence=evidence,
                    )
                )
                continue

            if (
                item.kind
                is ChunkKnowledgeKind.PENDING
            ):
                pending_items.append(
                    PendingItem(
                        description=item.description,
                        evidence=evidence,
                    )
                )
                continue

            raise ValueError(
                "MeetingReportStagedAssembler encontró "
                "un kind no soportado."
            )

        return MeetingReport(
            artifact_type="meeting_report",
            provider=normalized_provider,
            model=normalized_model,
            prompt_version=(
                normalized_prompt_version
            ),
            title=narrative.title.text,
            objective=(
                narrative.objective.text
                if narrative.objective
                is not None
                else None
            ),
            executive_summary=(
                narrative.executive_summary.text
            ),
            key_points=[
                key_point.text
                for key_point
                in narrative.key_points
            ],
            topics=topics,
            decisions=decisions,
            action_items=action_items,
            risks=risks,
            pending_items=pending_items,
            participants=[],
            conclusions=[],
        )

    @staticmethod
    def _validate_input_types(
        meeting_knowledge,
        semantic_consolidation,
        narrative,
    ) -> None:
        if not isinstance(
            meeting_knowledge,
            MeetingKnowledge,
        ):
            raise TypeError(
                "meeting_knowledge debe ser una "
                "instancia de MeetingKnowledge."
            )

        if not isinstance(
            semantic_consolidation,
            MeetingSemanticConsolidation,
        ):
            raise TypeError(
                "semantic_consolidation debe ser una "
                "instancia de "
                "MeetingSemanticConsolidation."
            )

        if not isinstance(
            narrative,
            MeetingReportNarrative,
        ):
            raise TypeError(
                "narrative debe ser una instancia de "
                "MeetingReportNarrative."
            )

        if not meeting_knowledge.has_content:
            raise ValueError(
                "meeting_knowledge no contiene "
                "conocimiento suficiente."
            )

        if not semantic_consolidation.has_content:
            raise ValueError(
                "semantic_consolidation no contiene "
                "items suficientes."
            )

    @staticmethod
    def _normalize_metadata_text(
        value,
        field_name: str,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} debe ser una cadena."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} no puede estar vacío."
            )

        return normalized

    def _validate_semantic_coverage(
        self,
        meeting_knowledge: MeetingKnowledge,
        semantic_consolidation: MeetingSemanticConsolidation,
    ) -> None:
        expected_keys = (
            self._build_expected_source_keys(
                meeting_knowledge
            )
        )

        actual_keys: set[
            tuple[str, int, int]
        ] = set()

        for output_index, item in enumerate(
            semantic_consolidation.items,
            start=1,
        ):
            section_name = (
                self.KIND_TO_SECTION.get(
                    item.kind
                )
            )

            if section_name is None:
                raise ValueError(
                    "MeetingReportStagedAssembler "
                    "encontró un kind no soportado."
                )

            for reference in item.source_refs:
                key = (
                    item.kind.value,
                    reference.chunk_index,
                    reference.item_index,
                )

                if key in actual_keys:
                    raise ValueError(
                        "MeetingReportStagedAssembler no "
                        "puede reutilizar una referencia "
                        "fuente. Referencia: "
                        f"{key}."
                    )

                self._resolve_source_item(
                    meeting_knowledge=(
                        meeting_knowledge
                    ),
                    kind=item.kind,
                    chunk_index=(
                        reference.chunk_index
                    ),
                    item_index=(
                        reference.item_index
                    ),
                    output_index=(
                        output_index
                    ),
                )

                actual_keys.add(
                    key
                )

        missing_keys = (
            expected_keys
            - actual_keys
        )

        if missing_keys:
            raise ValueError(
                "MeetingReportStagedAssembler requiere "
                "cobertura semántica completa; faltan "
                "referencias fuente: "
                + ", ".join(
                    str(key)
                    for key in sorted(
                        missing_keys
                    )
                )
                + "."
            )

        unexpected_keys = (
            actual_keys
            - expected_keys
        )

        if unexpected_keys:
            raise ValueError(
                "MeetingReportStagedAssembler encontró "
                "referencias fuente inesperadas: "
                + ", ".join(
                    str(key)
                    for key in sorted(
                        unexpected_keys
                    )
                )
                + "."
            )

    def _build_expected_source_keys(
        self,
        meeting_knowledge: MeetingKnowledge,
    ) -> set[
        tuple[str, int, int]
    ]:
        expected: set[
            tuple[str, int, int]
        ] = set()

        for chunk in meeting_knowledge.chunks:
            for (
                kind,
                section_name,
            ) in self.KIND_TO_SECTION.items():
                items = getattr(
                    chunk,
                    section_name,
                )

                for item_index in range(
                    len(items)
                ):
                    expected.add(
                        (
                            kind.value,
                            chunk.chunk_index,
                            item_index,
                        )
                    )

        return expected

    def _resolve_source_items(
        self,
        meeting_knowledge: MeetingKnowledge,
        item: ConsolidatedMeetingKnowledgeItem,
    ) -> list:
        return [
            self._resolve_source_item(
                meeting_knowledge=(
                    meeting_knowledge
                ),
                kind=item.kind,
                chunk_index=(
                    reference.chunk_index
                ),
                item_index=(
                    reference.item_index
                ),
                output_index=None,
            )
            for reference in item.source_refs
        ]

    def _resolve_source_item(
        self,
        meeting_knowledge: MeetingKnowledge,
        kind: ChunkKnowledgeKind,
        chunk_index: int,
        item_index: int,
        output_index: int | None,
    ):
        if (
            chunk_index < 0
            or chunk_index
            >= len(
                meeting_knowledge.chunks
            )
        ):
            raise ValueError(
                "MeetingReportStagedAssembler "
                "referencia un chunk inexistente"
                + (
                    f" desde item consolidado "
                    f"#{output_index}"
                    if output_index is not None
                    else ""
                )
                + "."
            )

        chunk = meeting_knowledge.chunks[
            chunk_index
        ]

        if (
            chunk.chunk_index
            != chunk_index
        ):
            raise ValueError(
                "MeetingKnowledge no conserva la "
                "cobertura contigua esperada."
            )

        section_name = (
            self.KIND_TO_SECTION[
                kind
            ]
        )

        source_items = getattr(
            chunk,
            section_name,
        )

        if (
            item_index < 0
            or item_index
            >= len(
                source_items
            )
        ):
            raise ValueError(
                "MeetingReportStagedAssembler "
                "referencia un item fuente inexistente "
                f"para kind={kind.value}."
            )

        return source_items[
            item_index
        ]

    @staticmethod
    def _collect_unique_evidence(
        source_items: list,
    ) -> list[EvidenceReference]:
        evidence: list[
            EvidenceReference
        ] = []

        seen_keys: set[tuple] = set()

        for source_item in source_items:
            for reference in (
                source_item.evidence
            ):
                key = (
                    reference.speaker,
                    float(
                        reference.start
                    ),
                    float(
                        reference.end
                    ),
                    reference.excerpt,
                )

                if key in seen_keys:
                    continue

                seen_keys.add(
                    key
                )
                evidence.append(
                    reference
                )

        return evidence

    @classmethod
    def _resolve_action_metadata(
        cls,
        source_items: list[ActionItem],
    ):
        owners = cls._unique_known_values(
            [
                item.owner
                for item in source_items
            ],
            unknown_value=None,
        )

        due_dates = cls._unique_known_values(
            [
                item.due_date
                for item in source_items
            ],
            unknown_value=None,
        )

        statuses = cls._unique_known_values(
            [
                item.status
                for item in source_items
            ],
            unknown_value=(
                ActionStatus.UNKNOWN
            ),
        )

        if len(owners) > 1:
            raise ValueError(
                "MeetingReportStagedAssembler no puede "
                "fusionar acciones con owners "
                "incompatibles."
            )

        if len(due_dates) > 1:
            raise ValueError(
                "MeetingReportStagedAssembler no puede "
                "fusionar acciones con due_dates "
                "incompatibles."
            )

        if len(statuses) > 1:
            raise ValueError(
                "MeetingReportStagedAssembler no puede "
                "fusionar acciones con status "
                "incompatibles."
            )

        owner = (
            owners[0]
            if owners
            else None
        )

        due_date = (
            due_dates[0]
            if due_dates
            else None
        )

        status = (
            statuses[0]
            if statuses
            else ActionStatus.UNKNOWN
        )

        return (
            owner,
            due_date,
            status,
        )

    @staticmethod
    def _unique_known_values(
        values: list,
        unknown_value,
    ) -> list:
        unique_values = []

        for value in values:
            if value == unknown_value:
                continue

            if not any(
                existing == value
                for existing in unique_values
            ):
                unique_values.append(
                    value
                )

        return unique_values

    def _validate_narrative_references(
        self,
        narrative: MeetingReportNarrative,
        semantic_consolidation: MeetingSemanticConsolidation,
    ) -> None:
        maximum_id = (
            len(
                semantic_consolidation.items
            )
            - 1
        )

        fields: list[
            tuple[
                str,
                GroundedNarrativeText,
            ]
        ] = [
            (
                "title",
                narrative.title,
            ),
            (
                "executive_summary",
                narrative.executive_summary,
            ),
        ]

        if narrative.objective is not None:
            fields.append(
                (
                    "objective",
                    narrative.objective,
                )
            )

        fields.extend(
            (
                f"key_points elemento #{index}",
                key_point,
            )
            for index, key_point in enumerate(
                narrative.key_points,
                start=1,
            )
        )

        for (
            field_name,
            grounded_text,
        ) in fields:
            for source_item_id in (
                grounded_text.source_item_ids
            ):
                if (
                    source_item_id < 0
                    or source_item_id
                    > maximum_id
                ):
                    raise ValueError(
                        "MeetingReportStagedAssembler "
                        f"{field_name} referencia un "
                        "item semántico inexistente."
                    )

        expected_summary_ids = set(
            range(
                len(
                    semantic_consolidation.items
                )
            )
        )

        actual_summary_ids = set(
            narrative.executive_summary.source_item_ids
        )

        if (
            actual_summary_ids
            != expected_summary_ids
        ):
            raise ValueError(
                "MeetingReportStagedAssembler requiere "
                "que executive_summary cubra todos los "
                "items semánticos consolidados."
            )
