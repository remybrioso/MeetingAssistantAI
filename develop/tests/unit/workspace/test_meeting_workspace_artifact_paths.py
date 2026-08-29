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


def test_workspace_exposes_action_items_json(
    tmp_path: Path,
) -> None:
    workspace = WorkspaceService().create(
        tmp_path
    )

    assert (
        workspace.action_items_json
        == (
            tmp_path
            / ".mai"
            / "action_items.json"
        )
    )


def test_workspace_exposes_decisions_json(
    tmp_path: Path,
) -> None:
    workspace = WorkspaceService().create(
        tmp_path
    )

    assert (
        workspace.decisions_json
        == (
            tmp_path
            / ".mai"
            / "decisions.json"
        )
    )


def test_workspace_exposes_meeting_minutes_docx(
    tmp_path: Path,
) -> None:
    workspace = WorkspaceService().create(
        tmp_path
    )

    assert (
        workspace.meeting_minutes_docx
        == (
            tmp_path
            / "Documentos"
            / "minutes.docx"
        )
    )


def test_workspace_exposes_meeting_pdf(
    tmp_path: Path,
) -> None:
    workspace = WorkspaceService().create(
        tmp_path
    )

    assert (
        workspace.meeting_pdf
        == (
            tmp_path
            / "Documentos"
            / "meeting.pdf"
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

    artifact_paths = [
        workspace.meeting_report_json,
        workspace.action_items_json,
        workspace.decisions_json,
        workspace.meeting_report_markdown,
        workspace.meeting_minutes_docx,
        workspace.meeting_pdf,
        workspace.summary_json,
        workspace.summary_markdown,
    ]

    assert all(
        path.exists() is False
        for path in artifact_paths
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
