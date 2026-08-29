import json
from datetime import UTC, date, datetime
from pathlib import Path

from models.artifacts.action_items_artifact import (
    ActionItemsArtifact,
)
from models.artifacts.decisions_artifact import (
    DecisionsArtifact,
)
from models.meeting_report import (
    ActionItem,
    ActionStatus,
    Decision,
    EvidenceReference,
)
from services.artifact_storage_service import (
    ArtifactStorageService,
)
from services.workspace_service import (
    WorkspaceService,
)


def build_source_timestamp() -> datetime:
    return datetime(
        2026,
        8,
        29,
        0,
        40,
        tzinfo=UTC,
    )


def build_action_artifact() -> ActionItemsArtifact:
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
        source_report_created_at=(
            build_source_timestamp()
        ),
        items=[
            ActionItem(
                description=(
                    "Preparar el plan de migración."
                ),
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
                            "María debe preparar "
                            "el plan de migración."
                        ),
                    )
                ],
            )
        ],
    )


def build_decisions_artifact() -> DecisionsArtifact:
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
        source_report_created_at=(
            build_source_timestamp()
        ),
        items=[
            Decision(
                description=(
                    "Se aprobó migrar la base "
                    "de datos."
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
        ],
    )


def load_json(
    path: Path,
) -> dict:
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def test_storage_persists_action_items_to_official_workspace_path(
    tmp_path: Path,
) -> None:
    workspace = WorkspaceService().create(
        tmp_path
    )
    artifact = build_action_artifact()

    ArtifactStorageService().save(
        artifact,
        workspace.action_items_json,
    )

    assert (
        workspace.action_items_json.exists()
        is True
    )

    assert (
        load_json(
            workspace.action_items_json
        )
        == artifact.as_dict()
    )


def test_storage_persists_decisions_to_official_workspace_path(
    tmp_path: Path,
) -> None:
    workspace = WorkspaceService().create(
        tmp_path
    )
    artifact = build_decisions_artifact()

    ArtifactStorageService().save(
        artifact,
        workspace.decisions_json,
    )

    assert (
        workspace.decisions_json.exists()
        is True
    )

    assert (
        load_json(
            workspace.decisions_json
        )
        == artifact.as_dict()
    )


def test_structured_artifacts_can_coexist_in_same_workspace(
    tmp_path: Path,
) -> None:
    workspace = WorkspaceService().create(
        tmp_path
    )
    storage = ArtifactStorageService()

    action_artifact = (
        build_action_artifact()
    )
    decisions_artifact = (
        build_decisions_artifact()
    )

    storage.save(
        action_artifact,
        workspace.action_items_json,
    )
    storage.save(
        decisions_artifact,
        workspace.decisions_json,
    )

    action_data = load_json(
        workspace.action_items_json
    )
    decision_data = load_json(
        workspace.decisions_json
    )

    assert (
        action_data["artifact_type"]
        == "meeting_action_items"
    )
    assert (
        decision_data["artifact_type"]
        == "meeting_decisions"
    )
    assert (
        action_data["items"][0][
            "description"
        ]
        != decision_data["items"][0][
            "description"
        ]
    )


def test_storage_preserves_complete_action_evidence_and_metadata(
    tmp_path: Path,
) -> None:
    workspace = WorkspaceService().create(
        tmp_path
    )

    ArtifactStorageService().save(
        build_action_artifact(),
        workspace.action_items_json,
    )

    data = load_json(
        workspace.action_items_json
    )

    assert (
        data["provider"]
        == "ollama"
    )
    assert (
        data["model"]
        == "qwen2.5:3b"
    )
    assert (
        data["prompt_version"]
        == "meeting_report_global_staged_v1"
    )
    assert (
        data["source_report_created_at"]
        == "2026-08-29T00:40:00+00:00"
    )
    assert (
        data["items"][0]["owner"][
            "display_name"
        ]
        == "María"
    )
    assert (
        data["items"][0]["evidence"][0][
            "excerpt"
        ]
        == (
            "María debe preparar "
            "el plan de migración."
        )
    )


def test_storage_preserves_complete_decision_evidence_and_metadata(
    tmp_path: Path,
) -> None:
    workspace = WorkspaceService().create(
        tmp_path
    )

    ArtifactStorageService().save(
        build_decisions_artifact(),
        workspace.decisions_json,
    )

    data = load_json(
        workspace.decisions_json
    )

    assert (
        data["provider"]
        == "ollama"
    )
    assert (
        data["source_report_created_at"]
        == "2026-08-29T00:40:00+00:00"
    )
    assert (
        data["items"][0]["description"]
        == (
            "Se aprobó migrar la base "
            "de datos."
        )
    )
    assert (
        data["items"][0]["evidence"][0][
            "speaker"
        ]
        == "LOCAL"
    )
