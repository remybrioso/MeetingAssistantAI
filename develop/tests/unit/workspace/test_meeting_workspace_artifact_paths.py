import json
from pathlib import Path

from services.workspace_service import WorkspaceService


def test_workspace_exposes_meeting_report_json(
    tmp_path: Path,
) -> None:
    workspace = WorkspaceService().create(
        tmp_path
    )

    assert (
        workspace.meeting_report_json
        == (
            tmp_path
            / ".mai"
            / "meeting_report.json"
        )
    )


def test_workspace_exposes_meeting_report_markdown(
    tmp_path: Path,
) -> None:
    workspace = WorkspaceService().create(
        tmp_path
    )

    assert (
        workspace.meeting_report_markdown
        == (
            tmp_path
            / "Documentos"
            / "Meeting Report.md"
        )
    )


def test_workspace_preserves_legacy_summary_paths(
    tmp_path: Path,
) -> None:
    workspace = WorkspaceService().create(
        tmp_path
    )

    assert (
        workspace.summary_json
        == (
            tmp_path
            / ".mai"
            / "summary.json"
        )
    )

    assert (
        workspace.summary_markdown
        == (
            tmp_path
            / "Documentos"
            / "Resumen.md"
        )
    )


def test_workspace_does_not_create_artifacts_during_initialization(
    tmp_path: Path,
) -> None:
    workspace = WorkspaceService().create(
        tmp_path
    )

    assert (
        workspace.meeting_report_json.exists()
        is False
    )

    assert (
        workspace.meeting_report_markdown.exists()
        is False
    )

    assert (
        workspace.summary_json.exists()
        is False
    )

    assert (
        workspace.summary_markdown.exists()
        is False
    )


def test_workspace_manifest_keeps_base_structure(
    tmp_path: Path,
) -> None:
    workspace = WorkspaceService().create(
        tmp_path
    )

    data = json.loads(
        workspace.workspace_manifest.read_text(
            encoding="utf-8"
        )
    )

    assert (
        data["version"]
        == workspace.version
        == "1.0"
    )

    assert data["structure"] == {
        "audio": str(
            workspace.audio_dir
        ),
        "documents": str(
            workspace.documents_dir
        ),
        "internal": str(
            workspace.internal_dir
        ),
    }


def test_workspace_base_directories_exist(
    tmp_path: Path,
) -> None:
    workspace = WorkspaceService().create(
        tmp_path
    )

    assert workspace.audio_dir.is_dir()
    assert workspace.documents_dir.is_dir()
    assert workspace.internal_dir.is_dir()
