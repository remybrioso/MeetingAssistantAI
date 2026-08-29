import pytest

from models.chunk_classification import (
    ChunkKnowledgeKind,
)
from models.meeting_semantic_consolidation import (
    ConsolidatedMeetingKnowledgeItem,
    MeetingKnowledgeItemReference,
    MeetingSemanticConsolidation,
)


def build_reference(
    chunk_index: int = 0,
    item_index: int = 0,
) -> MeetingKnowledgeItemReference:
    return MeetingKnowledgeItemReference(
        chunk_index=chunk_index,
        item_index=item_index,
    )


def build_item(
    kind=ChunkKnowledgeKind.DECISION,
    description="Se aprobó la migración.",
    source_refs=None,
) -> ConsolidatedMeetingKnowledgeItem:
    return ConsolidatedMeetingKnowledgeItem(
        kind=kind,
        description=description,
        source_refs=(
            source_refs
            if source_refs is not None
            else [
                build_reference(),
            ]
        ),
    )


def test_reference_normalizes_valid_indices() -> None:
    reference = build_reference(
        chunk_index=2,
        item_index=3,
    )

    assert reference.chunk_index == 2
    assert reference.item_index == 3

    assert reference.as_dict() == {
        "chunk_index": 2,
        "item_index": 3,
    }


@pytest.mark.parametrize(
    "field_name",
    [
        "chunk_index",
        "item_index",
    ],
)
def test_reference_rejects_non_integer_indices(
    field_name: str,
) -> None:
    values = {
        "chunk_index": 0,
        "item_index": 0,
    }
    values[field_name] = 1.5

    with pytest.raises(
        TypeError,
        match="debe ser entero",
    ):
        MeetingKnowledgeItemReference(
            **values
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "chunk_index",
        "item_index",
    ],
)
def test_reference_rejects_negative_indices(
    field_name: str,
) -> None:
    values = {
        "chunk_index": 0,
        "item_index": 0,
    }
    values[field_name] = -1

    with pytest.raises(
        ValueError,
        match="no puede ser negativo",
    ):
        MeetingKnowledgeItemReference(
            **values
        )


def test_item_normalizes_description() -> None:
    item = build_item(
        description="  Se aprobó la migración.  "
    )

    assert (
        item.description
        == "Se aprobó la migración."
    )


def test_item_rejects_invalid_kind() -> None:
    with pytest.raises(
        TypeError,
        match="ChunkKnowledgeKind",
    ):
        build_item(
            kind="decision"
        )


def test_item_rejects_empty_description() -> None:
    with pytest.raises(
        ValueError,
        match="no puede estar vacío",
    ):
        build_item(
            description="   "
        )


def test_item_requires_source_refs() -> None:
    with pytest.raises(
        ValueError,
        match="al menos una source_ref",
    ):
        build_item(
            source_refs=[]
        )


def test_item_rejects_duplicate_source_refs() -> None:
    with pytest.raises(
        ValueError,
        match="referencias duplicadas",
    ):
        build_item(
            source_refs=[
                build_reference(),
                build_reference(),
            ]
        )


def test_consolidation_accepts_empty_items() -> None:
    result = MeetingSemanticConsolidation(
        items=[]
    )

    assert not result.has_content
    assert result.as_dict() == {
        "items": [],
    }


def test_consolidation_filters_items_by_kind() -> None:
    result = MeetingSemanticConsolidation(
        items=[
            build_item(
                kind=(
                    ChunkKnowledgeKind.DECISION
                ),
                source_refs=[
                    build_reference(
                        item_index=0
                    ),
                ],
            ),
            build_item(
                kind=(
                    ChunkKnowledgeKind.ACTION
                ),
                description=(
                    "Preparar el plan."
                ),
                source_refs=[
                    build_reference(
                        item_index=1
                    ),
                ],
            ),
        ]
    )

    actions = result.items_of_kind(
        ChunkKnowledgeKind.ACTION
    )

    assert len(actions) == 1
    assert (
        actions[0].description
        == "Preparar el plan."
    )


def test_consolidation_rejects_reused_source_across_items() -> None:
    reference = build_reference()

    with pytest.raises(
        ValueError,
        match="reutilizar una referencia fuente",
    ):
        MeetingSemanticConsolidation(
            items=[
                build_item(
                    source_refs=[
                        reference,
                    ],
                ),
                build_item(
                    description=(
                        "Otra decisión."
                    ),
                    source_refs=[
                        reference,
                    ],
                ),
            ]
        )


def test_consolidation_source_uniqueness_is_scoped_by_kind() -> None:
    result = MeetingSemanticConsolidation(
        items=[
            build_item(
                kind=(
                    ChunkKnowledgeKind.DECISION
                ),
                source_refs=[
                    build_reference(),
                ],
            ),
            build_item(
                kind=(
                    ChunkKnowledgeKind.ACTION
                ),
                description=(
                    "Ejecutar la migración."
                ),
                source_refs=[
                    build_reference(),
                ],
            ),
        ]
    )

    assert len(
        result.items
    ) == 2


def test_consolidation_rejects_invalid_items_collection() -> None:
    with pytest.raises(
        TypeError,
        match="items debe ser una lista",
    ):
        MeetingSemanticConsolidation(
            items=()
        )


def test_items_of_kind_rejects_invalid_kind() -> None:
    result = MeetingSemanticConsolidation()

    with pytest.raises(
        TypeError,
        match="ChunkKnowledgeKind",
    ):
        result.items_of_kind(
            "decision"
        )
