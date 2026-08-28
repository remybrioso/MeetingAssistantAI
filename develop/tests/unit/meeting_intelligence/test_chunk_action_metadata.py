from datetime import date

import pytest

from models.chunk_action_metadata import (
    ActionMetadataEntry,
    ChunkActionMetadata,
)
from models.meeting_report import (
    ActionOwner,
    ActionStatus,
)


def build_entry(
    item_index: int = 2,
) -> ActionMetadataEntry:
    return ActionMetadataEntry(
        classification_item_index=item_index,
        owner="  María  ",
        due_date=date(
            2026,
            8,
            30,
        ),
        status=" PENDING ",
    )


def test_entry_normalizes_domain_values() -> None:
    entry = build_entry()

    assert isinstance(
        entry.owner,
        ActionOwner,
    )
    assert (
        entry.owner.display_name
        == "María"
    )
    assert entry.due_date == date(
        2026,
        8,
        30,
    )
    assert (
        entry.status
        is ActionStatus.PENDING
    )


def test_entry_accepts_null_owner_and_due_date() -> None:
    entry = ActionMetadataEntry(
        classification_item_index=0,
        owner=None,
        due_date=None,
        status=ActionStatus.UNKNOWN,
    )

    assert entry.owner is None
    assert entry.due_date is None


def test_entry_rejects_negative_item_index() -> None:
    with pytest.raises(
        ValueError,
        match="no puede ser negativo",
    ):
        ActionMetadataEntry(
            classification_item_index=-1,
        )


def test_entry_rejects_boolean_item_index() -> None:
    with pytest.raises(
        TypeError,
        match="debe ser entero",
    ):
        ActionMetadataEntry(
            classification_item_index=True,
        )


def test_entry_rejects_non_date_due_date() -> None:
    with pytest.raises(
        TypeError,
        match="debe ser una fecha",
    ):
        ActionMetadataEntry(
            classification_item_index=0,
            due_date="2026-08-30",
        )


def test_entry_serializes_values() -> None:
    entry = build_entry()

    assert entry.as_dict() == {
        "classification_item_index": 2,
        "owner": {
            "display_name": "María",
        },
        "due_date": "2026-08-30",
        "status": "pending",
    }


def test_chunk_metadata_accepts_empty_entries() -> None:
    metadata = ChunkActionMetadata(
        chunk_index=4,
        entries=[],
    )

    assert metadata.has_actions is False
    assert metadata.as_dict() == {
        "chunk_index": 4,
        "entries": [],
    }


def test_chunk_metadata_rejects_duplicate_item_indices() -> None:
    with pytest.raises(
        ValueError,
        match="duplicados",
    ):
        ChunkActionMetadata(
            chunk_index=0,
            entries=[
                build_entry(
                    item_index=1
                ),
                build_entry(
                    item_index=1
                ),
            ],
        )


def test_chunk_metadata_finds_entry_by_classification_item() -> None:
    first = build_entry(
        item_index=1
    )
    second = ActionMetadataEntry(
        classification_item_index=3,
        status=ActionStatus.UNKNOWN,
    )

    metadata = ChunkActionMetadata(
        chunk_index=0,
        entries=[
            first,
            second,
        ],
    )

    assert (
        metadata.for_classification_item(
            3
        )
        is second
    )
    assert (
        metadata.for_classification_item(
            99
        )
        is None
    )


def test_chunk_metadata_defensively_copies_entries() -> None:
    original_entries = [
        build_entry()
    ]

    metadata = ChunkActionMetadata(
        chunk_index=0,
        entries=original_entries,
    )

    original_entries.clear()

    assert len(
        metadata.entries
    ) == 1
