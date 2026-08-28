"""
chunk_knowledge_assembler.py

Construye ChunkKnowledge de forma determinista a partir de una
clasificación staged y los metadatos enriquecidos de sus acciones.

No realiza llamadas al proveedor de IA y no interpreta nuevamente
el contenido de la reunión.
"""

from models.chunk_action_metadata import (
    ChunkActionMetadata,
)
from models.chunk_classification import (
    ChunkClassification,
    ChunkKnowledgeKind,
    ClassifiedKnowledgeItem,
)
from models.chunk_knowledge import ChunkKnowledge
from models.meeting_report import (
    ActionItem,
    Decision,
    EvidenceReference,
    MeetingRisk,
    MeetingTopic,
    PendingItem,
)
from models.transcript_chunk import TranscriptChunk


class ChunkKnowledgeAssembler:
    """
    Convierte los resultados staged de un chunk al dominio
    ChunkKnowledge existente.

    Responsabilidades:

    - verificar que todos los objetos pertenezcan al mismo chunk;
    - reconstruir EvidenceReference desde segment_ids;
    - convertir cada clasificación al modelo de dominio apropiado;
    - aplicar los metadatos de J2 únicamente a las acciones.

    No resume, no consolida y no llama al LLM.
    """

    def assemble(
        self,
        chunk: TranscriptChunk,
        classification: ChunkClassification,
        action_metadata: ChunkActionMetadata,
    ) -> ChunkKnowledge:
        """
        Construye conocimiento de dominio para un único chunk.
        """

        self._validate_input_types(
            chunk=chunk,
            classification=classification,
            action_metadata=action_metadata,
        )

        self._validate_source_identity(
            chunk=chunk,
            classification=classification,
            action_metadata=action_metadata,
        )

        self._validate_segment_references(
            chunk=chunk,
            classification=classification,
        )

        self._validate_action_metadata(
            classification=classification,
            action_metadata=action_metadata,
        )

        topics: list[MeetingTopic] = []
        decisions: list[Decision] = []
        action_items: list[ActionItem] = []
        risks: list[MeetingRisk] = []
        pending_items: list[PendingItem] = []

        for item_index, item in enumerate(
            classification.items
        ):
            evidence = self._build_evidence(
                chunk=chunk,
                item=item,
            )

            if item.kind is ChunkKnowledgeKind.TOPIC:
                topics.append(
                    MeetingTopic(
                        title=item.description,
                        summary=item.description,
                        evidence=evidence,
                    )
                )
                continue

            if item.kind is ChunkKnowledgeKind.DECISION:
                decisions.append(
                    Decision(
                        description=item.description,
                        rationale=None,
                        evidence=evidence,
                    )
                )
                continue

            if item.kind is ChunkKnowledgeKind.ACTION:
                metadata = (
                    action_metadata.for_classification_item(
                        item_index
                    )
                )

                if metadata is None:
                    raise ValueError(
                        "ChunkKnowledgeAssembler requiere "
                        "metadatos para toda acción clasificada."
                    )

                action_items.append(
                    ActionItem(
                        description=item.description,
                        evidence=evidence,
                        owner=metadata.owner,
                        due_date=metadata.due_date,
                        status=metadata.status,
                    )
                )
                continue

            if item.kind is ChunkKnowledgeKind.RISK:
                risks.append(
                    MeetingRisk(
                        description=item.description,
                        impact=None,
                        evidence=evidence,
                    )
                )
                continue

            if item.kind is ChunkKnowledgeKind.PENDING:
                pending_items.append(
                    PendingItem(
                        description=item.description,
                        evidence=evidence,
                    )
                )
                continue

            raise ValueError(
                "ChunkKnowledgeAssembler encontró un kind "
                "no soportado."
            )

        return ChunkKnowledge(
            chunk_index=chunk.index,
            start=chunk.start,
            end=chunk.end,
            key_points=[],
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
        chunk,
        classification,
        action_metadata,
    ) -> None:
        if not isinstance(
            chunk,
            TranscriptChunk,
        ):
            raise TypeError(
                "chunk debe ser una instancia de "
                "TranscriptChunk."
            )

        if not isinstance(
            classification,
            ChunkClassification,
        ):
            raise TypeError(
                "classification debe ser una instancia de "
                "ChunkClassification."
            )

        if not isinstance(
            action_metadata,
            ChunkActionMetadata,
        ):
            raise TypeError(
                "action_metadata debe ser una instancia de "
                "ChunkActionMetadata."
            )

    @staticmethod
    def _validate_source_identity(
        chunk: TranscriptChunk,
        classification: ChunkClassification,
        action_metadata: ChunkActionMetadata,
    ) -> None:
        if (
            classification.chunk_index
            != chunk.index
        ):
            raise ValueError(
                "ChunkClassification no corresponde al "
                "TranscriptChunk recibido."
            )

        if (
            action_metadata.chunk_index
            != chunk.index
        ):
            raise ValueError(
                "ChunkActionMetadata no corresponde al "
                "TranscriptChunk recibido."
            )

        if (
            classification.start
            != float(
                chunk.start
            )
            or classification.end
            != float(
                chunk.end
            )
        ):
            raise ValueError(
                "ChunkClassification no corresponde al rango "
                "temporal del TranscriptChunk recibido."
            )

    @staticmethod
    def _validate_segment_references(
        chunk: TranscriptChunk,
        classification: ChunkClassification,
    ) -> None:
        maximum_segment_id = (
            len(
                chunk.segments
            )
            - 1
        )

        for item_index, item in enumerate(
            classification.items,
            start=1,
        ):
            for segment_id in item.segment_ids:
                if (
                    segment_id
                    > maximum_segment_id
                ):
                    raise ValueError(
                        "ChunkClassification item "
                        f"#{item_index} contiene segment_id "
                        f"fuera de rango: {segment_id}."
                    )

    @staticmethod
    def _validate_action_metadata(
        classification: ChunkClassification,
        action_metadata: ChunkActionMetadata,
    ) -> None:
        action_indices = {
            index
            for index, item in enumerate(
                classification.items
            )
            if (
                item.kind
                is ChunkKnowledgeKind.ACTION
            )
        }

        metadata_indices: set[int] = set()

        for entry_index, entry in enumerate(
            action_metadata.entries,
            start=1,
        ):
            item_index = (
                entry.classification_item_index
            )

            if (
                item_index
                >= len(
                    classification.items
                )
            ):
                raise ValueError(
                    "ChunkActionMetadata entry "
                    f"#{entry_index} referencia un "
                    "classification_item_index fuera "
                    "de rango."
                )

            classified_item = (
                classification.items[
                    item_index
                ]
            )

            if (
                classified_item.kind
                is not ChunkKnowledgeKind.ACTION
            ):
                raise ValueError(
                    "ChunkActionMetadata solo puede "
                    "referenciar items kind=action."
                )

            metadata_indices.add(
                item_index
            )

        missing_indices = (
            action_indices
            - metadata_indices
        )

        if missing_indices:
            raise ValueError(
                "ChunkKnowledgeAssembler requiere "
                "metadatos para todas las acciones "
                "clasificadas."
            )

    @staticmethod
    def _build_evidence(
        chunk: TranscriptChunk,
        item: ClassifiedKnowledgeItem,
    ) -> list[EvidenceReference]:
        evidence: list[EvidenceReference] = []

        for segment_id in item.segment_ids:
            segment = chunk.segments[
                segment_id
            ]

            evidence.append(
                EvidenceReference(
                    speaker=segment.speaker,
                    start=segment.start,
                    end=segment.end,
                    excerpt=segment.text,
                )
            )

        return evidence