from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    Table,
)

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
from services.meeting_report_pdf_exporter import (
    MeetingReportPdfExporter,
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


def flatten_flowables(flowables) -> list:
    flattened = []

    for flowable in flowables:
        flattened.append(
            flowable
        )

        if isinstance(
            flowable,
            KeepTogether,
        ):
            flattened.extend(
                flatten_flowables(
                    flowable._content
                )
            )

    return flattened


def story_text(story: list) -> str:
    texts = []

    for flowable in flatten_flowables(
        story
    ):
        if isinstance(
            flowable,
            Paragraph,
        ):
            texts.append(
                flowable.getPlainText()
            )
        elif isinstance(
            flowable,
            Table,
        ):
            for row in flowable._cellvalues:
                for cell in row:
                    if isinstance(
                        cell,
                        Paragraph,
                    ):
                        texts.append(
                            cell.getPlainText()
                        )
                    else:
                        texts.append(
                            str(
                                cell
                            )
                        )

    return "\n".join(
        texts
    )


def test_pdf_exporter_builds_complete_story() -> None:
    story = (
        MeetingReportPdfExporter()
        .build_story(
            build_report()
        )
    )

    content = story_text(
        story
    )

    expected = [
        "MINUTA DE REUNIÓN",
        "Seguimiento del proyecto Oracle",
        "Objetivo",
        "Resumen ejecutivo",
        "Puntos clave",
        "Temas tratados",
        "Decisiones",
        "Acciones y compromisos",
        "Riesgos y bloqueos",
        "Asuntos pendientes",
        "Participantes",
        "Conclusiones",
    ]

    for value in expected:
        assert value in content


def test_pdf_exporter_renders_action_metadata() -> None:
    story = (
        MeetingReportPdfExporter()
        .build_story(
            build_report()
        )
    )

    content = story_text(
        story
    )

    assert "Responsable" in content
    assert "Equipo DBA" in content
    assert "Fecha límite" in content
    assert "2026-08-14" in content
    assert "Estado" in content
    assert "Pendiente" in content


def test_pdf_exporter_renders_evidence() -> None:
    story = (
        MeetingReportPdfExporter()
        .build_story(
            build_report()
        )
    )

    content = story_text(
        story
    )

    assert "Evidencia" in content
    assert (
        "00:01:05 - 00:01:12"
        in content
    )
    assert "SPEAKER_01" in content
    assert (
        "El equipo DBA completará las pruebas"
        in content
    )


def test_pdf_exporter_renders_participants() -> None:
    story = (
        MeetingReportPdfExporter()
        .build_story(
            build_report()
        )
    )

    content = story_text(
        story
    )

    assert "Remy" in content
    assert "SPEAKER_00" in content
    assert "Coordinador" in content


def test_pdf_exporter_writes_pdf_file(
    tmp_path: Path,
) -> None:
    output_file = (
        tmp_path
        / "documents"
        / "meeting.pdf"
    )

    MeetingReportPdfExporter().export(
        build_report(),
        output_file,
    )

    assert output_file.exists()
    assert output_file.stat().st_size > 0

    prefix = output_file.read_bytes()[
        :5
    ]

    assert prefix == b"%PDF-"


def test_pdf_exporter_creates_parent_directory(
    tmp_path: Path,
) -> None:
    output_file = (
        tmp_path
        / "nested"
        / "documents"
        / "meeting.pdf"
    )

    MeetingReportPdfExporter().export(
        build_report(),
        output_file,
    )

    assert output_file.exists()


def test_pdf_exporter_handles_empty_optional_sections() -> None:
    report = MeetingReport(
        artifact_type="meeting_report",
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version=(
            "meeting_report_global_staged_v1"
        ),
        title="Reunión técnica",
        executive_summary=(
            "Se revisó el estado general del proyecto "
            "durante la reunión técnica."
        ),
        key_points=[
            "Se revisó el estado general del proyecto.",
        ],
    )

    content = story_text(
        MeetingReportPdfExporter()
        .build_story(
            report
        )
    )

    expected = [
        (
            "No se identificó un objetivo "
            "explícito en la reunión."
        ),
        "No se registraron temas adicionales.",
        "No se registraron decisiones.",
        (
            "No se registraron acciones "
            "o compromisos."
        ),
        (
            "No se registraron riesgos "
            "o bloqueos."
        ),
        (
            "No se registraron asuntos "
            "pendientes."
        ),
        (
            "No fue posible identificar "
            "participantes."
        ),
        (
            "No se registraron conclusiones "
            "explícitas."
        ),
    ]

    for value in expected:
        assert value in content


def test_pdf_exporter_does_not_mutate_report() -> None:
    report = build_report()
    original = report.as_dict()

    (
        MeetingReportPdfExporter()
        .build_story(
            report
        )
    )

    assert report.as_dict() == original


def test_pdf_exporter_escapes_xml_sensitive_text() -> None:
    exporter = MeetingReportPdfExporter()

    assert (
        exporter._escape_text(
            "DBA & Infra <Core>"
        )
        == "DBA &amp; Infra &lt;Core&gt;"
    )


def test_pdf_exporter_accepts_xml_sensitive_report_content() -> None:
    report = build_report()
    report.key_points = [
        "DBA & Infra revisaron <Core>.",
    ]

    story = (
        MeetingReportPdfExporter()
        .build_story(
            report
        )
    )

    assert (
        "DBA & Infra revisaron <Core>."
        in story_text(
            story
        )
    )


def test_pdf_exporter_rejects_invalid_report() -> None:
    with pytest.raises(
        TypeError,
        match="MeetingReport",
    ):
        (
            MeetingReportPdfExporter()
            .build_story(
                object()
            )
        )


def test_pdf_exporter_rejects_invalid_output_type() -> None:
    with pytest.raises(
        TypeError,
        match="Path",
    ):
        MeetingReportPdfExporter().export(
            build_report(),
            "meeting.pdf",
        )


def test_pdf_exporter_rejects_non_pdf_extension(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match=".pdf",
    ):
        MeetingReportPdfExporter().export(
            build_report(),
            tmp_path / "meeting.docx",
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
def test_pdf_exporter_formats_action_status(
    status: str,
    expected: str,
) -> None:
    assert (
        MeetingReportPdfExporter
        ._format_status(
            status
        )
        == expected
    )


def test_pdf_exporter_formats_unknown_status() -> None:
    assert (
        MeetingReportPdfExporter
        ._format_status(
            "other"
        )
        == "No especificado"
    )


def test_pdf_exporter_formats_long_timestamp() -> None:
    assert (
        MeetingReportPdfExporter
        ._format_timestamp(
            3723.0
        )
        == "01:02:03"
    )


def test_pdf_exporter_formats_created_at() -> None:
    assert (
        MeetingReportPdfExporter
        ._format_created_at(
            "2026-08-29T00:40:25+00:00"
        )
        == "29/08/2026 00:40 UTC"
    )


def test_pdf_exporter_preserves_unparseable_created_at() -> None:
    assert (
        MeetingReportPdfExporter
        ._format_created_at(
            "fecha-desconocida"
        )
        == "fecha-desconocida"
    )
