from datetime import UTC, datetime

import pytest

from models.artifacts.decisions_artifact import (
    DecisionsArtifact,
)
from models.meeting_report import (
    Decision,
    EvidenceReference,
)


def build_decision() -> Decision:
    return Decision(
        description=(
            "Se aprobó migrar la base de datos."
        ),
        rationale=(
            "Reducir dependencia del servidor local."
        ),
        evidence=[
            EvidenceReference(
                speaker="LOCAL",
                start=0.0,
                end=8.0,
                excerpt=(
                    "El equipo aprobó migrar "
                    "la base de datos."
                ),
            )
        ],
    )


def build_artifact(
    items=None,
) -> DecisionsArtifact:
    return DecisionsArtifact(
        artifact_type="meeting_decisions",
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
            [build_decision()]
            if items is None
            else items
        ),
    )


def test_decisions_artifact_accepts_valid_items() -> None:
    artifact = build_artifact()

    assert (
        artifact.artifact_type
        == "meeting_decisions"
    )
    assert len(
        artifact.items
    ) == 1


def test_decisions_artifact_normalizes_title() -> None:
    artifact = DecisionsArtifact(
        artifact_type="meeting_decisions",
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


def test_decisions_artifact_allows_empty_items() -> None:
    artifact = build_artifact(
        items=[]
    )

    assert artifact.items == []


def test_decisions_artifact_defensively_copies_items() -> None:
    source = [
        build_decision()
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
def test_decisions_artifact_rejects_empty_title(
    meeting_title,
) -> None:
    with pytest.raises(
        ValueError,
        match="meeting_title",
    ):
        DecisionsArtifact(
            artifact_type="meeting_decisions",
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="v1",
            meeting_title=meeting_title,
            source_report_created_at=datetime.now(
                UTC
            ),
            items=[],
        )


def test_decisions_artifact_rejects_non_string_title() -> None:
    with pytest.raises(
        TypeError,
        match="meeting_title",
    ):
        DecisionsArtifact(
            artifact_type="meeting_decisions",
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="v1",
            meeting_title=1,
            source_report_created_at=datetime.now(
                UTC
            ),
            items=[],
        )


def test_decisions_artifact_rejects_invalid_source_timestamp() -> None:
    with pytest.raises(
        TypeError,
        match="source_report_created_at",
    ):
        DecisionsArtifact(
            artifact_type="meeting_decisions",
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="v1",
            meeting_title="Migración",
            source_report_created_at=None,
            items=[],
        )


def test_decisions_artifact_rejects_non_list_items() -> None:
    with pytest.raises(
        TypeError,
        match="items",
    ):
        build_artifact(
            items=(
                build_decision(),
            )
        )


def test_decisions_artifact_rejects_wrong_item_type() -> None:
    with pytest.raises(
        TypeError,
        match="Decision",
    ):
        build_artifact(
            items=[
                object()
            ]
        )


def test_decisions_artifact_serializes_complete_decision() -> None:
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
        data["items"][0]["description"]
        == "Se aprobó migrar la base de datos."
    )
    assert (
        data["items"][0]["rationale"]
        == (
            "Reducir dependencia del servidor local."
        )
    )
    assert (
        data["items"][0]["evidence"][0][
            "speaker"
        ]
        == "LOCAL"
    )
