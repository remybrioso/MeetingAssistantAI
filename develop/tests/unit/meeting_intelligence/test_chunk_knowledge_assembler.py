from datetime import date

import pytest

from models.chunk_action_metadata import (
    ActionMetadataEntry,
    ChunkActionMetadata,
)
from models.chunk_classification import (
    ChunkClassification,
    ChunkKnowledgeKind,
    ClassifiedKnowledgeItem,
)
from models.chunk_knowledge import ChunkKnowledge
from models.meeting_report import (
    ActionStatus,
)
from models.transcript import Segment
from models.transcript_chunk import TranscriptChunk
from services.chunk_knowledge_assembler import (
    ChunkKnowledgeAssembler,
)


def build_chunk(
    index: int = 3,
) -> TranscriptChunk:
    return TranscriptChunk(
        index=index,
        segments=[
            Segment(
                start=0.0,
                end=8.0,
                speaker="LOCAL",
                text=(
                    "El equipo aprobó migrar la base de "
                    "datos principal a la nube."
                ),
            ),
            Segment(
                start=8.0,
                end=16.0,
                speaker="REMOTE",
                text=(
                    "María debe preparar el plan de "
                    "migración antes del 30 de agosto "
                    "de 2026."
                ),
            ),
            Segment(
                start=16.0,
                end=24.0,
                speaker="LOCAL",
                text=(
                    "Existe riesgo de interrupción del "
                    "servicio durante la migración."
                ),
            ),
            Segment(
                start=24.0,
                end=32.0,
                speaker="REMOTE",
                text=(
                    "Quedó pendiente confirmar la ventana "
                    "de mantenimiento con Operaciones."
                ),
            ),
            Segment(
                start=32.0,
                end=40.0,
                speaker="LOCAL",
                text=(
                    "Se revisó la arquitectura actual y "
                    "la capacidad del servidor."
                ),
            ),
        ],
    )


def build_items() -> list[ClassifiedKnowledgeItem]:
    return [
        ClassifiedKnowledgeItem(
            kind=ChunkKnowledgeKind.DECISION,
            description=(
                "Migrar la base de datos principal "
                "a la nube."
            ),
            segment_ids=[
                0,
            ],
        ),
        ClassifiedKnowledgeItem(
            kind=ChunkKnowledgeKind.ACTION,
            description=(
                "Preparar el plan de migración."
            ),
            segment_ids=[
                1,
            ],
        ),
        ClassifiedKnowledgeItem(
            kind=ChunkKnowledgeKind.RISK,
            description=(
                "Interrupción del servicio durante "
                "la migración."
            ),
            segment_ids=[
                2,
            ],
        ),
        ClassifiedKnowledgeItem(
            kind=ChunkKnowledgeKind.PENDING,
            description=(
                "Confirmar la ventana de mantenimiento "
                "con Operaciones."
            ),
            segment_ids=[
                3,
            ],
        ),
        ClassifiedKnowledgeItem(
            kind=ChunkKnowledgeKind.TOPIC,
            description=(
                "Arquitectura actual y capacidad "
                "del servidor."
            ),
            segment_ids=[
                4,
            ],
        ),
    ]


def build_classification(
    chunk: TranscriptChunk,
    items=None,
) -> ChunkClassification:
    return ChunkClassification(
        chunk_index=chunk.index,
        start=chunk.start,
        end=chunk.end,
        items=(
            build_items()
            if items is None
            else items
        ),
    )


def build_action_metadata(
    chunk_index: int = 3,
    item_index: int = 1,
) -> ChunkActionMetadata:
    return ChunkActionMetadata(
        chunk_index=chunk_index,
        entries=[
            ActionMetadataEntry(
                classification_item_index=(
                    item_index
                ),
                owner="María",
                due_date=date(
                    2026,
                    8,
                    30,
                ),
                status=ActionStatus.PENDING,
            ),
        ],
    )


def test_assembler_builds_complete_chunk_knowledge() -> None:
    chunk = build_chunk()
    classification = build_classification(
        chunk
    )
    metadata = build_action_metadata(
        chunk_index=chunk.index
    )

    result = ChunkKnowledgeAssembler().assemble(
        chunk=chunk,
        classification=classification,
        action_metadata=metadata,
    )

    assert isinstance(
        result,
        ChunkKnowledge,
    )

    assert result.chunk_index == chunk.index
    assert result.start == chunk.start
    assert result.end == chunk.end

    assert len(
        result.topics
    ) == 1
    assert len(
        result.decisions
    ) == 1
    assert len(
        result.action_items
    ) == 1
    assert len(
        result.risks
    ) == 1
    assert len(
        result.pending_items
    ) == 1

    assert result.key_points == []
    assert result.participants == []
    assert result.conclusions == []

    topic = result.topics[0]

    assert (
        topic.title
        == "Arquitectura actual y capacidad del servidor."
    )
    assert (
        topic.summary
        == topic.title
    )

    decision = result.decisions[0]

    assert decision.rationale is None

    risk = result.risks[0]

    assert risk.impact is None

    action = result.action_items[0]

    assert action.owner is not None
    assert (
        action.owner.display_name
        == "María"
    )
    assert action.due_date == date(
        2026,
        8,
        30,
    )
    assert (
        action.status
        is ActionStatus.PENDING
    )


def test_assembler_reconstructs_evidence_from_segments() -> None:
    chunk = build_chunk()

    item = ClassifiedKnowledgeItem(
        kind=ChunkKnowledgeKind.DECISION,
        description=(
            "Revisar la migración considerando "
            "la capacidad actual."
        ),
        segment_ids=[
            0,
            4,
        ],
    )

    classification = build_classification(
        chunk,
        items=[
            item,
        ],
    )

    result = ChunkKnowledgeAssembler().assemble(
        chunk=chunk,
        classification=classification,
        action_metadata=ChunkActionMetadata(
            chunk_index=chunk.index,
            entries=[],
        ),
    )

    evidence = result.decisions[
        0
    ].evidence

    assert len(
        evidence
    ) == 2

    assert evidence[0].speaker == "LOCAL"
    assert evidence[0].start == 0.0
    assert evidence[0].end == 8.0
    assert (
        evidence[0].excerpt
        == chunk.segments[0].text
    )

    assert evidence[1].speaker == "LOCAL"
    assert evidence[1].start == 32.0
    assert evidence[1].end == 40.0
    assert (
        evidence[1].excerpt
        == chunk.segments[4].text
    )


def test_assembler_accepts_empty_classification() -> None:
    chunk = build_chunk()

    result = ChunkKnowledgeAssembler().assemble(
        chunk=chunk,
        classification=build_classification(
            chunk,
            items=[],
        ),
        action_metadata=ChunkActionMetadata(
            chunk_index=chunk.index,
            entries=[],
        ),
    )

    assert result.has_content is False
    assert result.topics == []
    assert result.decisions == []
    assert result.action_items == []
    assert result.risks == []
    assert result.pending_items == []


@pytest.mark.parametrize(
    (
        "chunk",
        "classification",
        "action_metadata",
        "expected_message",
    ),
    [
        (
            object(),
            None,
            None,
            "chunk debe ser una instancia",
        ),
        (
            build_chunk(),
            object(),
            None,
            "classification debe ser una instancia",
        ),
        (
            build_chunk(),
            build_classification(
                build_chunk()
            ),
            object(),
            "action_metadata debe ser una instancia",
        ),
    ],
)
def test_assembler_rejects_invalid_input_types(
    chunk,
    classification,
    action_metadata,
    expected_message: str,
) -> None:
    with pytest.raises(
        TypeError,
        match=expected_message,
    ):
        ChunkKnowledgeAssembler().assemble(
            chunk=chunk,
            classification=classification,
            action_metadata=action_metadata,
        )


def test_assembler_rejects_classification_from_other_chunk() -> None:
    chunk = build_chunk(
        index=3
    )

    classification = ChunkClassification(
        chunk_index=4,
        start=chunk.start,
        end=chunk.end,
        items=[],
    )

    with pytest.raises(
        ValueError,
        match=(
            "ChunkClassification no corresponde"
        ),
    ):
        ChunkKnowledgeAssembler().assemble(
            chunk=chunk,
            classification=classification,
            action_metadata=ChunkActionMetadata(
                chunk_index=chunk.index,
                entries=[],
            ),
        )


def test_assembler_rejects_action_metadata_from_other_chunk() -> None:
    chunk = build_chunk(
        index=3
    )

    with pytest.raises(
        ValueError,
        match=(
            "ChunkActionMetadata no corresponde"
        ),
    ):
        ChunkKnowledgeAssembler().assemble(
            chunk=chunk,
            classification=build_classification(
                chunk,
                items=[],
            ),
            action_metadata=ChunkActionMetadata(
                chunk_index=4,
                entries=[],
            ),
        )


def test_assembler_rejects_classification_with_wrong_range() -> None:
    chunk = build_chunk()

    classification = ChunkClassification(
        chunk_index=chunk.index,
        start=1.0,
        end=chunk.end,
        items=[],
    )

    with pytest.raises(
        ValueError,
        match="rango temporal",
    ):
        ChunkKnowledgeAssembler().assemble(
            chunk=chunk,
            classification=classification,
            action_metadata=ChunkActionMetadata(
                chunk_index=chunk.index,
                entries=[],
            ),
        )


def test_assembler_rejects_out_of_range_segment_id() -> None:
    chunk = build_chunk()

    classification = build_classification(
        chunk,
        items=[
            ClassifiedKnowledgeItem(
                kind=ChunkKnowledgeKind.DECISION,
                description=(
                    "Decisión con referencia inválida."
                ),
                segment_ids=[
                    99,
                ],
            ),
        ],
    )

    with pytest.raises(
        ValueError,
        match="segment_id fuera de rango",
    ):
        ChunkKnowledgeAssembler().assemble(
            chunk=chunk,
            classification=classification,
            action_metadata=ChunkActionMetadata(
                chunk_index=chunk.index,
                entries=[],
            ),
        )


def test_assembler_requires_metadata_for_every_action() -> None:
    chunk = build_chunk()

    classification = build_classification(
        chunk,
        items=[
            ClassifiedKnowledgeItem(
                kind=ChunkKnowledgeKind.ACTION,
                description=(
                    "Preparar el plan."
                ),
                segment_ids=[
                    1,
                ],
            ),
        ],
    )

    with pytest.raises(
        ValueError,
        match=(
            "metadatos para todas las acciones"
        ),
    ):
        ChunkKnowledgeAssembler().assemble(
            chunk=chunk,
            classification=classification,
            action_metadata=ChunkActionMetadata(
                chunk_index=chunk.index,
                entries=[],
            ),
        )


def test_assembler_rejects_metadata_for_non_action_item() -> None:
    chunk = build_chunk()

    classification = build_classification(
        chunk,
        items=[
            ClassifiedKnowledgeItem(
                kind=ChunkKnowledgeKind.DECISION,
                description=(
                    "Migrar la plataforma."
                ),
                segment_ids=[
                    0,
                ],
            ),
        ],
    )

    metadata = ChunkActionMetadata(
        chunk_index=chunk.index,
        entries=[
            ActionMetadataEntry(
                classification_item_index=0,
            ),
        ],
    )

    with pytest.raises(
        ValueError,
        match="solo puede referenciar items kind=action",
    ):
        ChunkKnowledgeAssembler().assemble(
            chunk=chunk,
            classification=classification,
            action_metadata=metadata,
        )


def test_assembler_rejects_out_of_range_metadata_index() -> None:
    chunk = build_chunk()

    classification = build_classification(
        chunk,
        items=[],
    )

    metadata = ChunkActionMetadata(
        chunk_index=chunk.index,
        entries=[
            ActionMetadataEntry(
                classification_item_index=99,
            ),
        ],
    )

    with pytest.raises(
        ValueError,
        match=(
            "classification_item_index fuera de rango"
        ),
    ):
        ChunkKnowledgeAssembler().assemble(
            chunk=chunk,
            classification=classification,
            action_metadata=metadata,
        )


def test_assembler_does_not_modify_inputs() -> None:
    chunk = build_chunk()
    classification = build_classification(
        chunk
    )
    metadata = build_action_metadata(
        chunk_index=chunk.index
    )

    chunk_before = chunk.as_dict()
    classification_before = (
        classification.as_dict()
    )
    metadata_before = metadata.as_dict()

    ChunkKnowledgeAssembler().assemble(
        chunk=chunk,
        classification=classification,
        action_metadata=metadata,
    )

    assert chunk.as_dict() == chunk_before
    assert (
        classification.as_dict()
        == classification_before
    )
    assert metadata.as_dict() == metadata_before