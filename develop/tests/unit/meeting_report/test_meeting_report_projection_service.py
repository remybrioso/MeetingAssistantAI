from datetime import UTC, date, datetime

import pytest

from models.artifacts.action_items_artifact import (
    ActionItemsArtifact,
)
from models.artifacts.decisions_artifact import (
    DecisionsArtifact,
)
from models.artifacts.meeting_report import (
    MeetingReport,
)
from models.meeting_report import (
    ActionItem,
    ActionStatus,
    Decision,
    EvidenceReference,
)
from services.meeting_report_projection_service import (
    MeetingReportProjectionService,
)


def build_report() -> MeetingReport:
    created_at = datetime(
        2026,
        8,
        29,
        0,
        40,
        tzinfo=UTC,
    )

    return MeetingReport(
        artifact_type="meeting_report",
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version=(
            "meeting_report_global_staged_v1"
        ),
        created_at=created_at,
        title=(
            "Migración de base de datos"
        ),
        executive_summary=(
            "Se aprobó la migración de la base "
            "de datos y se definieron acciones."
        ),
        key_points=[
            (
                "Migrar la base de datos."
            )
        ],
        decisions=[
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
                status=(
                    ActionStatus.PENDING
                ),
                evidence=[
                    EvidenceReference(
                        speaker="REMOTE",
                        start=8.0,
                        end=16.0,
                        excerpt=(
                            "María preparará "
                            "el plan."
                        ),
                    )
                ],
            )
        ],
    )


def test_projection_service_projects_action_items() -> None:
    report = build_report()

    artifact = (
        MeetingReportProjectionService()
        .project_action_items(
            report
        )
    )

    assert isinstance(
        artifact,
        ActionItemsArtifact,
    )
    assert (
        artifact.artifact_type
        == "meeting_action_items"
    )
    assert (
        artifact.meeting_title
        == report.title
    )
    assert artifact.provider == report.provider
    assert artifact.model == report.model
    assert (
        artifact.prompt_version
        == report.prompt_version
    )
    assert (
        artifact.source_report_created_at
        is report.created_at
    )
    assert (
        artifact.items[0]
        is report.action_items[0]
    )


def test_projection_service_projects_decisions() -> None:
    report = build_report()

    artifact = (
        MeetingReportProjectionService()
        .project_decisions(
            report
        )
    )

    assert isinstance(
        artifact,
        DecisionsArtifact,
    )
    assert (
        artifact.artifact_type
        == "meeting_decisions"
    )
    assert (
        artifact.meeting_title
        == report.title
    )
    assert (
        artifact.items[0]
        is report.decisions[0]
    )


def test_projection_service_project_returns_stable_order() -> None:
    report = build_report()

    (
        actions,
        decisions,
    ) = (
        MeetingReportProjectionService()
        .project(
            report
        )
    )

    assert isinstance(
        actions,
        ActionItemsArtifact,
    )
    assert isinstance(
        decisions,
        DecisionsArtifact,
    )


def test_projection_service_allows_empty_source_sections() -> None:
    report = build_report()
    report.action_items = []
    report.decisions = []

    (
        actions,
        decisions,
    ) = (
        MeetingReportProjectionService()
        .project(
            report
        )
    )

    assert actions.items == []
    assert decisions.items == []


def test_projection_service_copies_output_collections() -> None:
    report = build_report()

    service = (
        MeetingReportProjectionService()
    )

    actions = (
        service.project_action_items(
            report
        )
    )
    decisions = (
        service.project_decisions(
            report
        )
    )

    assert (
        actions.items
        is not report.action_items
    )
    assert (
        decisions.items
        is not report.decisions
    )


def test_projection_service_does_not_mutate_report() -> None:
    report = build_report()
    original = report.as_dict()

    MeetingReportProjectionService().project(
        report
    )

    assert (
        report.as_dict()
        == original
    )


@pytest.mark.parametrize(
    "method_name",
    [
        "project_action_items",
        "project_decisions",
        "project",
    ],
)
def test_projection_service_rejects_invalid_report(
    method_name,
) -> None:
    service = (
        MeetingReportProjectionService()
    )

    method = getattr(
        service,
        method_name,
    )

    with pytest.raises(
        TypeError,
        match="MeetingReport",
    ):
        method(
            object()
        )
