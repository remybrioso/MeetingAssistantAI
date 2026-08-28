import pytest

from models.chunk_classification import (
    ChunkClassification,
    ChunkKnowledgeKind,
    ClassifiedKnowledgeItem,
)


def build_item() -> ClassifiedKnowledgeItem:
    return ClassifiedKnowledgeItem(
        kind=ChunkKnowledgeKind.DECISION,
        description="  Se aprobó la migración.  ",
        segment_ids=[
            0,
            2,
        ],
    )


def test_kind_from_value_normalizes_string() -> None:
    assert (
        ChunkKnowledgeKind.from_value(
            "  ACTION  "
        )
        is ChunkKnowledgeKind.ACTION
    )


def test_kind_from_value_rejects_unknown_value() -> None:
    with pytest.raises(
        ValueError,
        match="valor válido",
    ):
        ChunkKnowledgeKind.from_value(
            "other"
        )


def test_item_normalizes_description_and_preserves_ids() -> None:
    item = build_item()

    assert (
        item.description
        == "Se aprobó la migración."
    )
    assert item.segment_ids == [
        0,
        2,
    ]


def test_item_rejects_empty_description() -> None:
    with pytest.raises(
        ValueError,
        match="description no puede estar vacío",
    ):
        ClassifiedKnowledgeItem(
            kind=ChunkKnowledgeKind.TOPIC,
            description="   ",
            segment_ids=[
                0,
            ],
        )


def test_item_requires_segment_ids() -> None:
    with pytest.raises(
        ValueError,
        match="al menos un segment_id",
    ):
        ClassifiedKnowledgeItem(
            kind=ChunkKnowledgeKind.TOPIC,
            description="Arquitectura actual.",
            segment_ids=[],
        )


def test_item_rejects_duplicate_segment_ids() -> None:
    with pytest.raises(
        ValueError,
        match="duplicados",
    ):
        ClassifiedKnowledgeItem(
            kind=ChunkKnowledgeKind.RISK,
            description="Riesgo de interrupción.",
            segment_ids=[
                1,
                1,
            ],
        )


def test_item_rejects_boolean_segment_id() -> None:
    with pytest.raises(
        TypeError,
        match="debe ser entero",
    ):
        ClassifiedKnowledgeItem(
            kind=ChunkKnowledgeKind.PENDING,
            description="Confirmar fecha.",
            segment_ids=[
                True,
            ],
        )


def test_classification_accepts_empty_items() -> None:
    classification = ChunkClassification(
        chunk_index=3,
        start=10.0,
        end=20.0,
        items=[],
    )

    assert classification.has_content is False
    assert classification.as_dict() == {
        "chunk_index": 3,
        "start": 10.0,
        "end": 20.0,
        "items": [],
    }


def test_classification_filters_items_by_kind() -> None:
    decision = build_item()
    action = ClassifiedKnowledgeItem(
        kind=ChunkKnowledgeKind.ACTION,
        description="Preparar plan.",
        segment_ids=[
            1,
        ],
    )

    classification = ChunkClassification(
        chunk_index=0,
        start=0.0,
        end=10.0,
        items=[
            decision,
            action,
        ],
    )

    assert classification.items_of_kind(
        ChunkKnowledgeKind.ACTION
    ) == [
        action
    ]


def test_classification_defensively_copies_items() -> None:
    original_items = [
        build_item()
    ]

    classification = ChunkClassification(
        chunk_index=0,
        start=0.0,
        end=10.0,
        items=original_items,
    )

    original_items.clear()

    assert len(
        classification.items
    ) == 1
