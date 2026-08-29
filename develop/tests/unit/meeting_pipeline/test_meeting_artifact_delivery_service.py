from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from models.artifacts.meeting_report import MeetingReport
from models.meeting_report import (
    ActionItem,
    ActionStatus,
    Decision,
    EvidenceReference,
)
from services.meeting_artifact_delivery_service import (
    MeetingArtifactDeliveryService,
)
from services.workspace_service import WorkspaceService


class FakeStorageService:

    def __init__(self) -> None:
        self.calls = []

    def save(
        self,
        artifact,
        filename,
    ) -> None:
        self.calls.append(
            (
                artifact,
                filename,
            )
        )


class FakeProjectionService:

    def __init__(self) -> None:
        self.received_report = None
        self.action_items_artifact = object()
        self.decisions_artifact = object()

    def project(
        self,
        report,
    ):
        self.received_report = report

        return (
            self.action_items_artifact,
            self.decisions_artifact,
        )


class FakeExporter:

    def __init__(self) -> None:
        self.calls = []

    def export(
        self,
        report,
        filename,
    ) -> None:
        self.calls.append(
            (
                report,
                filename,
            )
        )


def build_report() -> MeetingReport:
    evidence = EvidenceReference(
        speaker="SPEAKER_01",
        start=8.0,
        end=16.0,
        excerpt=(
            "María debe preparar el plan "
            "de migración."
        ),
    )

    return MeetingReport(
        artifact_type="meeting_report",
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version=(
            "meeting_report_global_staged_v1"
        ),
        created_at=datetime(
            2026,
            8,
            29,
            0,
            40,
            tzinfo=UTC,
        ),
        title=(
            "Migración de base de datos"
        ),
        executive_summary=(
            "Se aprobó la migración de la base "
            "de datos y se definieron acciones."
        ),
        key_points=[
            (
                "Se aprobó migrar la base "
                "de datos."
            )
        ],
        decisions=[
            Decision(
                description=(
                    "Se aprobó migrar la base "
                    "de datos."
                ),
                evidence=[
                    evidence,
                ],
            )
        ],
        action_items=[
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
                    evidence,
                ],
            )
        ],
    )


def build_service():
    storage = FakeStorageService()
    projection = FakeProjectionService()
    markdown = FakeExporter()
    docx = FakeExporter()
    pdf = FakeExporter()

    service = MeetingArtifactDeliveryService(
        storage_service=storage,
        projection_service=projection,
        markdown_exporter=markdown,
        docx_exporter=docx,
        pdf_exporter=pdf,
    )

    return (
        service,
        storage,
        projection,
        markdown,
        docx,
        pdf,
    )


def test_delivery_projects_report_once(
    tmp_path: Path,
) -> None:
    (
        service,
        _,
        projection,
        _,
        _,
        _,
    ) = build_service()

    report = build_report()
    workspace = WorkspaceService().create(
        tmp_path
    )

    service.deliver(
        report,
        workspace,
    )

    assert (
        projection.received_report
        is report
    )


def test_delivery_persists_all_structured_artifacts(
    tmp_path: Path,
) -> None:
    (
        service,
        storage,
        projection,
        _,
        _,
        _,
    ) = build_service()

    report = build_report()
    workspace = WorkspaceService().create(
        tmp_path
    )

    service.deliver(
        report,
        workspace,
    )

    assert storage.calls == [
        (
            report,
            workspace.meeting_report_json,
        ),
        (
            projection.action_items_artifact,
            workspace.action_items_json,
        ),
        (
            projection.decisions_artifact,
            workspace.decisions_json,
        ),
    ]


def test_delivery_exports_markdown(
    tmp_path: Path,
) -> None:
    (
        service,
        _,
        _,
        markdown,
        _,
        _,
    ) = build_service()

    report = build_report()
    workspace = WorkspaceService().create(
        tmp_path
    )

    service.deliver(
        report,
        workspace,
    )

    assert markdown.calls == [
        (
            report,
            workspace.meeting_report_markdown,
        )
    ]


def test_delivery_exports_docx(
    tmp_path: Path,
) -> None:
    (
        service,
        _,
        _,
        _,
        docx,
        _,
    ) = build_service()

    report = build_report()
    workspace = WorkspaceService().create(
        tmp_path
    )

    service.deliver(
        report,
        workspace,
    )

    assert docx.calls == [
        (
            report,
            workspace.meeting_minutes_docx,
        )
    ]


def test_delivery_exports_pdf(
    tmp_path: Path,
) -> None:
    (
        service,
        _,
        _,
        _,
        _,
        pdf,
    ) = build_service()

    report = build_report()
    workspace = WorkspaceService().create(
        tmp_path
    )

    service.deliver(
        report,
        workspace,
    )

    assert pdf.calls == [
        (
            report,
            workspace.meeting_pdf,
        )
    ]


def test_delivery_does_not_mutate_report(
    tmp_path: Path,
) -> None:
    (
        service,
        _,
        _,
        _,
        _,
        _,
    ) = build_service()

    report = build_report()
    original = report.as_dict()

    service.deliver(
        report,
        WorkspaceService().create(
            tmp_path
        ),
    )

    assert report.as_dict() == original


def test_delivery_rejects_invalid_report(
    tmp_path: Path,
) -> None:
    (
        service,
        _,
        _,
        _,
        _,
        _,
    ) = build_service()

    with pytest.raises(
        TypeError,
        match="MeetingReport",
    ):
        service.deliver(
            object(),
            WorkspaceService().create(
                tmp_path
            ),
        )


def test_delivery_rejects_invalid_workspace() -> None:
    (
        service,
        _,
        _,
        _,
        _,
        _,
    ) = build_service()

    with pytest.raises(
        TypeError,
        match="MeetingWorkspace",
    ):
        service.deliver(
            build_report(),
            object(),
        )


@pytest.mark.parametrize(
    "missing_dependency",
    [
        "storage_service",
        "projection_service",
        "markdown_exporter",
        "docx_exporter",
        "pdf_exporter",
    ],
)
def test_delivery_rejects_missing_dependency(
    missing_dependency: str,
) -> None:
    dependencies = {
        "storage_service": object(),
        "projection_service": object(),
        "markdown_exporter": object(),
        "docx_exporter": object(),
        "pdf_exporter": object(),
    }

    dependencies[
        missing_dependency
    ] = None

    with pytest.raises(
        ValueError,
        match=missing_dependency,
    ):
        MeetingArtifactDeliveryService(
            **dependencies
        )
