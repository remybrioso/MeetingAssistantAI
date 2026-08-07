from datetime import date
from pathlib import Path

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
from services.meeting_report_markdown_exporter import (
    MeetingReportMarkdownExporter,
)


def build_report() -> MeetingReport:
    evidence = EvidenceReference(
        speaker="SPEAKER_01",
        start=65.0,
        end=72.0,
        excerpt=(
            "El equipo DBA completará las pruebas "
            "antes del viernes."
        ),
    )

    return MeetingReport(
        artifact_type="meeting_report",
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
        title="Seguimiento del proyecto Oracle",
        objective=(
            "Revisar el avance y definir próximos pasos."
        ),
        executive_summary=(
            "Se revisó el avance del proyecto Oracle, "
            "los riesgos actuales y las acciones necesarias "
            "antes del próximo despliegue."
        ),
        key_points=[
            "Las pruebas de integración continúan.",
            "Se confirmó un posible retraso.",
            "El equipo DBA completará las pruebas.",
        ],
        topics=[
            MeetingTopic(
                title="Pruebas de integración",
                summary=(
                    "Se revisó el estado de las pruebas "
                    "previas al despliegue."
                ),
                evidence=[
                    evidence,
                ],
            ),
        ],
        decisions=[
            Decision(
                description=(
                    "Mantener el despliegue condicionado "
                    "a completar las pruebas."
                ),
                rationale=(
                    "Las pruebas todavía no han finalizado."
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
                owner="Equipo DBA",
                due_date=date(
                    2026,
                    8,
                    14,
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
                    "Las pruebas podrían retrasar "
                    "el despliegue."
                ),
                impact=(
                    "La fecha de implementación podría "
                    "modificarse."
                ),
                evidence=[
                    evidence,
                ],
            ),
        ],
        pending_items=[
            PendingItem(
                description=(
                    "Confirmar la ventana definitiva "
                    "de mantenimiento."
                ),
                evidence=[
                    evidence,
                ],
            ),
        ],
        participants=[
            Participant(
                name="Remy",
                speaker="SPEAKER_00",
                role="Coordinador",
            ),
        ],
        conclusions=[
            (
                "El despliegue dependerá del resultado "
                "de las pruebas."
            ),
        ],
    )


def test_exporter_renders_complete_document() -> None:
    exporter = MeetingReportMarkdownExporter()

    content = exporter.render(
        build_report()
    )

    assert (
        "# Seguimiento del proyecto Oracle"
        in content
    )

    assert "## Objetivo" in content
    assert "## Resumen ejecutivo" in content
    assert "## Puntos clave" in content
    assert "## Temas tratados" in content
    assert "## Decisiones" in content
    assert "## Acciones y compromisos" in content
    assert "## Riesgos y bloqueos" in content
    assert "## Asuntos pendientes" in content
    assert "## Participantes" in content
    assert "## Conclusiones" in content


def test_exporter_renders_action_details() -> None:
    content = (
        MeetingReportMarkdownExporter()
        .render(
            build_report()
        )
    )

    assert (
        "**Responsable:** Equipo DBA"
        in content
    )

    assert (
        "**Fecha límite:** 2026-08-14"
        in content
    )

    assert (
        "**Estado:** Pendiente"
        in content
    )


def test_exporter_renders_evidence_with_timestamp() -> None:
    content = (
        MeetingReportMarkdownExporter()
        .render(
            build_report()
        )
    )

    assert (
        "`00:01:05–00:01:12`"
        in content
    )

    assert "**SPEAKER_01:**" in content

    assert (
        "El equipo DBA completará las pruebas"
        in content
    )


def test_exporter_renders_participant_information() -> None:
    content = (
        MeetingReportMarkdownExporter()
        .render(
            build_report()
        )
    )

    assert (
        "**Remy**"
        in content
    )

    assert (
        "speaker: SPEAKER_00"
        in content
    )

    assert (
        "rol: Coordinador"
        in content
    )


def test_exporter_writes_markdown_file(
    tmp_path: Path,
) -> None:
    output_file = (
        tmp_path
        / "documents"
        / "meeting_report.md"
    )

    exporter = MeetingReportMarkdownExporter()

    exporter.export(
        build_report(),
        output_file,
    )

    assert output_file.exists()

    content = output_file.read_text(
        encoding="utf-8"
    )

    assert (
        "# Seguimiento del proyecto Oracle"
        in content
    )


def test_exporter_creates_parent_directory(
    tmp_path: Path,
) -> None:
    output_file = (
        tmp_path
        / "nested"
        / "documents"
        / "meeting_report.md"
    )

    MeetingReportMarkdownExporter().export(
        build_report(),
        output_file,
    )

    assert output_file.exists()


def test_exporter_handles_empty_optional_sections() -> None:
    report = MeetingReport(
        artifact_type="meeting_report",
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
        title="Reunión técnica",
        executive_summary=(
            "Se revisó el estado general del proyecto "
            "durante la reunión técnica."
        ),
        key_points=[
            "Se revisó el estado general del proyecto.",
        ],
    )

    content = (
        MeetingReportMarkdownExporter()
        .render(
            report
        )
    )

    assert (
        "No se identificó un objetivo explícito"
        in content
    )

    assert (
        "No se registraron decisiones."
        in content
    )

    assert (
        "No se registraron acciones o compromisos."
        in content
    )

    assert (
        "No se registraron riesgos o bloqueos."
        in content
    )

    assert (
        "No se registraron asuntos pendientes."
        in content
    )

    assert (
        "No fue posible identificar participantes."
        in content
    )


def test_exporter_rejects_invalid_report() -> None:
    exporter = MeetingReportMarkdownExporter()

    with pytest.raises(
        TypeError,
        match=(
            "report debe ser una instancia "
            "de MeetingReport"
        ),
    ):
        exporter.render(
            object()
        )


def test_exporter_rejects_invalid_output_file() -> None:
    exporter = MeetingReportMarkdownExporter()

    with pytest.raises(
        TypeError,
        match=(
            "output_file debe ser una instancia "
            "de Path"
        ),
    ):
        exporter.export(
            build_report(),
            "meeting_report.md",
        )


@pytest.mark.parametrize(
    (
        "status",
        "expected",
    ),
    [
        (
            "unknown",
            "No especificado",
        ),
        (
            "pending",
            "Pendiente",
        ),
        (
            "completed",
            "Completado",
        ),
        (
            "cancelled",
            "Cancelado",
        ),
    ],
)
def test_exporter_formats_action_status(
    status: str,
    expected: str,
) -> None:
    assert (
        MeetingReportMarkdownExporter
        ._format_status(
            status
        )
        == expected
    )


def test_exporter_formats_long_timestamp() -> None:
    assert (
        MeetingReportMarkdownExporter
        ._format_timestamp(
            3723.0
        )
        == "01:02:03"
    )