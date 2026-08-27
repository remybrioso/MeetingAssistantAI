from datetime import date

import pytest

from models.artifacts.meeting_report import MeetingReport
from models.chunk_knowledge import ChunkKnowledge
from models.meeting_knowledge import MeetingKnowledge
from models.meeting_report import (
    ActionItem,
    ActionStatus,
    Decision,
    EvidenceReference,
    MeetingRisk,
    MeetingTopic,
    PendingItem,
)
from services.validators.meeting_report_grounding_validator import (
    MeetingReportGroundingValidator,
)


def evidence(
    speaker: str,
    start: float,
    end: float,
    excerpt: str,
) -> EvidenceReference:
    return EvidenceReference(
        speaker=speaker,
        start=start,
        end=end,
        excerpt=excerpt,
    )


EARLY_EVIDENCE = evidence(
    speaker="LOCAL",
    start=10.0,
    end=15.0,
    excerpt="Se revisó la arquitectura propuesta.",
)

LATE_EVIDENCE = evidence(
    speaker="REMOTE",
    start=90.0,
    end=96.0,
    excerpt="La migración se realizará el viernes.",
)


def build_meeting_knowledge() -> MeetingKnowledge:
    return MeetingKnowledge(
        source_chunk_count=2,
        chunks=[
            ChunkKnowledge(
                chunk_index=0,
                start=0.0,
                end=50.0,
                topics=[
                    MeetingTopic(
                        title="Arquitectura",
                        summary=(
                            "Se revisó la arquitectura."
                        ),
                        evidence=[
                            EARLY_EVIDENCE,
                        ],
                    ),
                ],
                decisions=[
                    Decision(
                        description=(
                            "Mantener la arquitectura propuesta."
                        ),
                        evidence=[
                            EARLY_EVIDENCE,
                        ],
                    ),
                ],
            ),
            ChunkKnowledge(
                chunk_index=1,
                start=50.0,
                end=100.0,
                action_items=[
                    ActionItem(
                        description=(
                            "Ejecutar la migración."
                        ),
                        owner="Equipo Infraestructura",
                        due_date=date(
                            2026,
                            8,
                            28,
                        ),
                        status=ActionStatus.PENDING,
                        evidence=[
                            LATE_EVIDENCE,
                        ],
                    ),
                ],
                risks=[
                    MeetingRisk(
                        description=(
                            "La migración puede afectar "
                            "la ventana de servicio."
                        ),
                        evidence=[
                            LATE_EVIDENCE,
                        ],
                    ),
                ],
                pending_items=[
                    PendingItem(
                        description=(
                            "Confirmar la ventana final."
                        ),
                        evidence=[
                            LATE_EVIDENCE,
                        ],
                    ),
                ],
            ),
        ],
    )


def build_report(
    **overrides,
) -> MeetingReport:
    data = {
        "artifact_type": "meeting_report",
        "provider": "ollama",
        "model": "qwen2.5:3b",
        "prompt_version": (
            "meeting_report_consolidation_v1"
        ),
        "title": (
            "Arquitectura y migración de infraestructura"
        ),
        "objective": None,
        "executive_summary": (
            "Se revisó la arquitectura propuesta y se "
            "definieron elementos para la migración."
        ),
        "key_points": [
            "Se revisó la arquitectura propuesta.",
        ],
        "topics": [
            MeetingTopic(
                title="Arquitectura propuesta",
                summary=(
                    "Se revisó la arquitectura."
                ),
                evidence=[
                    EARLY_EVIDENCE,
                ],
            ),
        ],
        "decisions": [
            Decision(
                description=(
                    "Mantener la arquitectura propuesta."
                ),
                evidence=[
                    EARLY_EVIDENCE,
                ],
            ),
        ],
        "action_items": [
            ActionItem(
                description=(
                    "Ejecutar la migración."
                ),
                owner="Equipo Infraestructura",
                due_date=date(
                    2026,
                    8,
                    28,
                ),
                status=ActionStatus.PENDING,
                evidence=[
                    LATE_EVIDENCE,
                ],
            ),
        ],
        "risks": [
            MeetingRisk(
                description=(
                    "La migración puede afectar "
                    "la ventana de servicio."
                ),
                evidence=[
                    LATE_EVIDENCE,
                ],
            ),
        ],
        "pending_items": [
            PendingItem(
                description=(
                    "Confirmar la ventana final."
                ),
                evidence=[
                    LATE_EVIDENCE,
                ],
            ),
        ],
        "participants": [],
        "conclusions": [],
    }

    data.update(
        overrides
    )

    return MeetingReport(
        **data
    )


def test_validator_accepts_grounded_report() -> None:
    valid, errors = (
        MeetingReportGroundingValidator().validate(
            report=build_report(),
            meeting_knowledge=build_meeting_knowledge(),
        )
    )

    assert valid is True
    assert errors == []


def test_validator_preserves_early_and_late_evidence() -> None:
    report = build_report()

    valid, errors = (
        MeetingReportGroundingValidator().validate(
            report=report,
            meeting_knowledge=build_meeting_knowledge(),
        )
    )

    assert valid is True
    assert errors == []

    assert (
        report.topics[0].evidence[0]
        == EARLY_EVIDENCE
    )

    assert (
        report.action_items[0].evidence[0]
        == LATE_EVIDENCE
    )


def test_validator_rejects_missing_evidence() -> None:
    report = build_report(
        decisions=[
            Decision(
                description=(
                    "Mantener la arquitectura propuesta."
                ),
                evidence=[],
            ),
        ]
    )

    valid, errors = (
        MeetingReportGroundingValidator().validate(
            report=report,
            meeting_knowledge=build_meeting_knowledge(),
        )
    )

    assert valid is False
    assert any(
        "decisions elemento #1 no contiene evidencia"
        in error
        for error in errors
    )


def test_validator_rejects_fabricated_excerpt() -> None:
    fabricated = evidence(
        speaker="LOCAL",
        start=10.0,
        end=15.0,
        excerpt=(
            "Se aprobó una arquitectura completamente nueva."
        ),
    )

    report = build_report(
        topics=[
            MeetingTopic(
                title="Arquitectura",
                summary=(
                    "Se revisó la arquitectura."
                ),
                evidence=[
                    fabricated,
                ],
            ),
        ]
    )

    valid, errors = (
        MeetingReportGroundingValidator().validate(
            report=report,
            meeting_knowledge=build_meeting_knowledge(),
        )
    )

    assert valid is False
    assert any(
        "topics elemento #1 evidence #1 no existe"
        in error
        for error in errors
    )


def test_validator_rejects_modified_timestamp() -> None:
    modified = evidence(
        speaker="REMOTE",
        start=91.0,
        end=96.0,
        excerpt=(
            "La migración se realizará el viernes."
        ),
    )

    report = build_report(
        risks=[
            MeetingRisk(
                description=(
                    "La migración puede afectar "
                    "la ventana de servicio."
                ),
                evidence=[
                    modified,
                ],
            ),
        ]
    )

    valid, errors = (
        MeetingReportGroundingValidator().validate(
            report=report,
            meeting_knowledge=build_meeting_knowledge(),
        )
    )

    assert valid is False
    assert any(
        "risks elemento #1 evidence #1 no existe"
        in error
        for error in errors
    )


def test_validator_rejects_cross_section_reclassification() -> None:
    report = build_report(
        action_items=[
            ActionItem(
                description=(
                    "Cambiar la arquitectura."
                ),
                status=ActionStatus.UNKNOWN,
                evidence=[
                    EARLY_EVIDENCE,
                ],
            ),
        ]
    )

    valid, errors = (
        MeetingReportGroundingValidator().validate(
            report=report,
            meeting_knowledge=build_meeting_knowledge(),
        )
    )

    assert valid is False
    assert any(
        "action_items elemento #1 evidence #1 no existe"
        in error
        for error in errors
    )


def test_validator_rejects_invented_action_owner() -> None:
    report = build_report(
        action_items=[
            ActionItem(
                description=(
                    "Ejecutar la migración."
                ),
                owner="Equipo Seguridad",
                due_date=date(
                    2026,
                    8,
                    28,
                ),
                status=ActionStatus.PENDING,
                evidence=[
                    LATE_EVIDENCE,
                ],
            ),
        ]
    )

    valid, errors = (
        MeetingReportGroundingValidator().validate(
            report=report,
            meeting_knowledge=build_meeting_knowledge(),
        )
    )

    assert valid is False
    assert any(
        "owner no respaldado"
        in error
        for error in errors
    )


def test_validator_rejects_invented_action_due_date() -> None:
    report = build_report(
        action_items=[
            ActionItem(
                description=(
                    "Ejecutar la migración."
                ),
                owner="Equipo Infraestructura",
                due_date=date(
                    2026,
                    9,
                    1,
                ),
                status=ActionStatus.PENDING,
                evidence=[
                    LATE_EVIDENCE,
                ],
            ),
        ]
    )

    valid, errors = (
        MeetingReportGroundingValidator().validate(
            report=report,
            meeting_knowledge=build_meeting_knowledge(),
        )
    )

    assert valid is False
    assert any(
        "due_date no respaldado"
        in error
        for error in errors
    )


def test_validator_rejects_invented_action_status() -> None:
    report = build_report(
        action_items=[
            ActionItem(
                description=(
                    "Ejecutar la migración."
                ),
                owner="Equipo Infraestructura",
                due_date=date(
                    2026,
                    8,
                    28,
                ),
                status=ActionStatus.COMPLETED,
                evidence=[
                    LATE_EVIDENCE,
                ],
            ),
        ]
    )

    valid, errors = (
        MeetingReportGroundingValidator().validate(
            report=report,
            meeting_knowledge=build_meeting_knowledge(),
        )
    )

    assert valid is False
    assert any(
        "status no respaldado"
        in error
        for error in errors
    )


def test_validator_rejects_invalid_report_type() -> None:
    with pytest.raises(
        TypeError,
        match="instancia de MeetingReport",
    ):
        MeetingReportGroundingValidator().validate(
            report=object(),
            meeting_knowledge=build_meeting_knowledge(),
        )


def test_validator_rejects_invalid_meeting_knowledge_type() -> None:
    with pytest.raises(
        TypeError,
        match="instancia de MeetingKnowledge",
    ):
        MeetingReportGroundingValidator().validate(
            report=build_report(),
            meeting_knowledge=object(),
        )
