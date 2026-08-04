from datetime import date

import pytest

from models.artifacts.meeting_report import MeetingReport
from models.meeting_report import (
    ActionItem,
    ActionStatus,
    Decision,
    EvidenceReference,
    MeetingRisk,
    MeetingTopic,
    Participant,
    PendingItem,
)


def build_evidence() -> EvidenceReference:
    return EvidenceReference(
        speaker="REMOTE",
        start=15.0,
        end=21.5,
        excerpt=(
            "La implementación se moverá al próximo "
            "sprint."
        ),
    )


def build_complete_report() -> MeetingReport:
    evidence = build_evidence()

    return MeetingReport(
        artifact_type="meeting_report",
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
        title="Seguimiento del proyecto Oracle",
        objective=(
            "Revisar el avance y los próximos pasos."
        ),
        executive_summary=(
            "El equipo revisó las pruebas pendientes "
            "y acordó mover la implementación."
        ),
        key_points=[
            "Las pruebas continúan pendientes.",
            (
                "La implementación se moverá al "
                "próximo sprint."
            ),
        ],
        topics=[
            MeetingTopic(
                title="Pruebas de integración",
                summary=(
                    "Se revisó el estado de las pruebas."
                ),
                evidence=[
                    evidence,
                ],
            ),
        ],
        decisions=[
            Decision(
                description=(
                    "Mover la implementación al "
                    "próximo sprint."
                ),
                rationale=(
                    "Las pruebas todavía no están listas."
                ),
                evidence=[
                    evidence,
                ],
            ),
        ],
        action_items=[
            ActionItem(
                description=(
                    "Completar las pruebas de integración."
                ),
                owner="Equipo Oracle",
                due_date=date(
                    2026,
                    8,
                    7,
                ),
                status=ActionStatus.PENDING,
                evidence=[
                    evidence,
                ],
            ),
        ],
        risks=[
            MeetingRisk(
                description=(
                    "Las pruebas pueden retrasarse."
                ),
                impact=(
                    "El despliegue podría moverse."
                ),
                evidence=[
                    evidence,
                ],
            ),
        ],
        pending_items=[
            PendingItem(
                description=(
                    "Confirmar la ventana de mantenimiento."
                ),
                evidence=[
                    evidence,
                ],
            ),
        ],
        participants=[
            Participant(
                name="Remy",
                speaker="LOCAL",
                role="Coordinador",
            ),
        ],
        conclusions=[
            (
                "Se dará seguimiento a las pruebas "
                "durante el próximo sprint."
            ),
        ],
    )


def test_meeting_report_serializes_complete_domain() -> None:
    report = build_complete_report()

    data = report.as_dict()

    assert data["artifact_type"] == "meeting_report"
    assert data["provider"] == "ollama"
    assert data["model"] == "qwen2.5:3b"

    assert (
        data["prompt_version"]
        == "meeting_report_v1"
    )

    assert (
        data["title"]
        == "Seguimiento del proyecto Oracle"
    )

    assert len(data["topics"]) == 1
    assert len(data["decisions"]) == 1
    assert len(data["action_items"]) == 1
    assert len(data["risks"]) == 1
    assert len(data["pending_items"]) == 1
    assert len(data["participants"]) == 1

    assert (
        data["action_items"][0]["status"]
        == "pending"
    )

    assert (
        data["action_items"][0]["due_date"]
        == "2026-08-07"
    )


def test_meeting_report_accepts_empty_optional_sections() -> None:
    report = MeetingReport(
        artifact_type="meeting_report",
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
        title="Reunión de seguimiento",
        executive_summary=(
            "Se revisó el estado general del proyecto."
        ),
        key_points=[
            "Se revisó el estado del proyecto.",
        ],
    )

    data = report.as_dict()

    assert report.objective is None
    assert data["topics"] == []
    assert data["decisions"] == []
    assert data["action_items"] == []
    assert data["risks"] == []
    assert data["pending_items"] == []
    assert data["participants"] == []
    assert data["conclusions"] == []


def test_meeting_report_normalizes_text_fields() -> None:
    report = MeetingReport(
        artifact_type="meeting_report",
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
        title=" Reunión técnica ",
        objective=" Revisar la arquitectura. ",
        executive_summary=(
            " Se revisó la arquitectura del sistema. "
        ),
        key_points=[
            " Arquitectura revisada. ",
        ],
        conclusions=[
            " Continuar con las pruebas. ",
        ],
    )

    assert report.title == "Reunión técnica"
    assert report.objective == "Revisar la arquitectura."

    assert (
        report.executive_summary
        == "Se revisó la arquitectura del sistema."
    )

    assert report.key_points == [
        "Arquitectura revisada.",
    ]

    assert report.conclusions == [
        "Continuar con las pruebas.",
    ]


def test_meeting_report_requires_title() -> None:
    with pytest.raises(
        ValueError,
        match="title no puede estar vacío",
    ):
        MeetingReport(
            artifact_type="meeting_report",
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
            title="   ",
            executive_summary=(
                "Contenido del reporte."
            ),
            key_points=[
                "Punto confirmado.",
            ],
        )


def test_meeting_report_requires_executive_summary() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "executive_summary no puede estar vacío"
        ),
    ):
        MeetingReport(
            artifact_type="meeting_report",
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
            title="Reunión técnica",
            executive_summary="   ",
            key_points=[
                "Punto confirmado.",
            ],
        )


def test_meeting_report_requires_key_points() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "key_points debe contener al menos "
            "un elemento"
        ),
    ):
        MeetingReport(
            artifact_type="meeting_report",
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
            title="Reunión técnica",
            executive_summary=(
                "Contenido del reporte."
            ),
            key_points=[],
        )


def test_meeting_report_rejects_raw_dictionaries() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "topics elemento #1 debe ser una "
            "instancia de MeetingTopic"
        ),
    ):
        MeetingReport(
            artifact_type="meeting_report",
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
            title="Reunión técnica",
            executive_summary=(
                "Contenido del reporte."
            ),
            key_points=[
                "Punto confirmado.",
            ],
            topics=[
                {
                    "title": "Tema inválido",
                },
            ],
        )


def test_meeting_report_copies_collections() -> None:
    topics = [
        MeetingTopic(
            title="Arquitectura",
            summary=(
                "Se revisó la arquitectura."
            ),
        ),
    ]

    report = MeetingReport(
        artifact_type="meeting_report",
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
        title="Reunión técnica",
        executive_summary=(
            "Contenido del reporte."
        ),
        key_points=[
            "Punto confirmado.",
        ],
        topics=topics,
    )

    topics.clear()

    assert len(report.topics) == 1