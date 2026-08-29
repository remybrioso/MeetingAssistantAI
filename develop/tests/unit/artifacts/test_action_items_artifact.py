from datetime import UTC, date, datetime

import pytest

from models.artifacts.action_items_artifact import (
    ActionItemsArtifact,
)
from models.meeting_report import (
    ActionItem,
    ActionStatus,
    EvidenceReference,
)


def build_action() -> ActionItem:
    return ActionItem(
        description="Preparar el plan de migración.",
        owner="María",
        due_date=date(
            2026,
            8,
            30,
        ),
        status=ActionStatus.PENDING,
        evidence=[
            EvidenceReference(
                speaker="REMOTE",
                start=8.0,
                end=16.0,
                excerpt=(
                    "María debe preparar el plan "
                    "de migración."
                ),
            )
        ],
    )


def build_artifact(
    items=None,
) -> ActionItemsArtifact:
    return ActionItemsArtifact(
        artifact_type="meeting_action_items",
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version=(
            "meeting_report_global_staged_v1"
        ),
        meeting_title=(
            "Migración de base de datos"
        ),
        source_report_created_at=datetime(
            2026,
            8,
            29,
            0,
            40,
            tzinfo=UTC,
        ),
        items=(
            [build_action()]
            if items is None
            else items
        ),
    )


def test_action_items_artifact_accepts_valid_items() -> None:
    artifact = build_artifact()

    assert (
        artifact.artifact_type
        == "meeting_action_items"
    )
    assert len(
        artifact.items
    ) == 1


def test_action_items_artifact_normalizes_title() -> None:
    artifact = ActionItemsArtifact(
        artifact_type="meeting_action_items",
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="v1",
        meeting_title="  Migración  ",
        source_report_created_at=datetime.now(
            UTC
        ),
        items=[],
    )

    assert (
        artifact.meeting_title
        == "Migración"
    )


def test_action_items_artifact_allows_empty_items() -> None:
    artifact = build_artifact(
        items=[]
    )

    assert artifact.items == []


def test_action_items_artifact_defensively_copies_items() -> None:
    source = [
        build_action()
    ]

    artifact = build_artifact(
        items=source
    )

    source.clear()

    assert len(
        artifact.items
    ) == 1


@pytest.mark.parametrize(
    "meeting_title",
    [
        "",
        "   ",
    ],
)
def test_action_items_artifact_rejects_empty_title(
    meeting_title,
) -> None:
    with pytest.raises(
        ValueError,
        match="meeting_title",
    ):
        ActionItemsArtifact(
            artifact_type="meeting_action_items",
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="v1",
            meeting_title=meeting_title,
            source_report_created_at=datetime.now(
                UTC
            ),
            items=[],
        )


def test_action_items_artifact_rejects_non_string_title() -> None:
    with pytest.raises(
        TypeError,
        match="meeting_title",
    ):
        ActionItemsArtifact(
            artifact_type="meeting_action_items",
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="v1",
            meeting_title=1,
            source_report_created_at=datetime.now(
                UTC
            ),
            items=[],
        )


def test_action_items_artifact_rejects_invalid_source_timestamp() -> None:
    with pytest.raises(
        TypeError,
        match="source_report_created_at",
    ):
        ActionItemsArtifact(
            artifact_type="meeting_action_items",
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="v1",
            meeting_title="Migración",
            source_report_created_at=None,
            items=[],
        )


def test_action_items_artifact_rejects_non_list_items() -> None:
    with pytest.raises(
        TypeError,
        match="items",
    ):
        build_artifact(
            items=(
                build_action(),
            )
        )


def test_action_items_artifact_rejects_wrong_item_type() -> None:
    with pytest.raises(
        TypeError,
        match="ActionItem",
    ):
        build_artifact(
            items=[
                object()
            ]
        )


def test_action_items_artifact_serializes_complete_action() -> None:
    artifact = build_artifact()

    data = artifact.as_dict()

    assert (
        data["meeting_title"]
        == "Migración de base de datos"
    )
    assert (
        data[
            "source_report_created_at"
        ]
        == "2026-08-29T00:40:00+00:00"
    )
    assert (
        data["items"][0]["owner"][
            "display_name"
        ]
        == "María"
    )
    assert (
        data["items"][0]["due_date"]
        == "2026-08-30"
    )
    assert (
        data["items"][0]["status"]
        == "pending"
    )
    assert (
        data["items"][0]["evidence"][0][
            "excerpt"
        ]
        == (
            "María debe preparar el plan "
            "de migración."
        )
    )
