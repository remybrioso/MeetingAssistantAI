import pytest

from models.artifacts.meeting_report import MeetingReport
from models.meeting_report import (
    ActionItem,
    Decision,
    EvidenceReference,
    MeetingRisk,
    MeetingTopic,
    PendingItem,
)
from services.validators.meeting_report_validator import (
    MeetingReportValidator,
)


def build_report(
    **overrides,
) -> MeetingReport:
    data = {
        "artifact_type": "meeting_report",
        "provider": "ollama",
        "model": "qwen2.5:3b",
        "prompt_version": "meeting_report_v1",
        "title": "Reunión de seguimiento",
        "objective": "Revisar el avance del proyecto.",
        "executive_summary": (
            "Durante la reunión se revisó el avance general "
            "del proyecto y se definieron los próximos pasos."
        ),
        "key_points": [
            "El proyecto continúa en ejecución.",
            "Se revisaron los bloqueos actuales.",
            "Se definieron las siguientes acciones.",
        ],
        "topics": [],
        "decisions": [],
        "action_items": [],
        "risks": [],
        "pending_items": [],
        "participants": [],
        "conclusions": [],
    }

    data.update(
        overrides
    )

    return MeetingReport(
        **data
    )


def build_validator() -> MeetingReportValidator:
    return MeetingReportValidator()


def assert_contains_error(
    errors: list[str],
    expected_text: str,
) -> None:
    assert any(
        expected_text in error
        for error in errors
    )


def test_validator_accepts_valid_minimal_report() -> None:
    valid, errors = build_validator().validate(
        build_report()
    )

    assert valid
    assert errors == []


def test_validator_allows_empty_optional_sections() -> None:
    report = build_report(
        objective=None,
        topics=[],
        decisions=[],
        action_items=[],
        risks=[],
        pending_items=[],
        participants=[],
        conclusions=[],
    )

    valid, errors = build_validator().validate(
        report
    )

    assert valid
    assert errors == []


def test_validator_rejects_short_title() -> None:
    report = build_report(
        title="AI",
    )

    valid, errors = build_validator().validate(
        report
    )

    assert not valid
    assert_contains_error(
        errors,
        "título es demasiado corto",
    )


def test_validator_rejects_long_title() -> None:
    report = build_report(
        title="A" * 201,
    )

    valid, errors = build_validator().validate(
        report
    )

    assert not valid
    assert_contains_error(
        errors,
        "título es demasiado largo",
    )


def test_validator_rejects_short_objective() -> None:
    report = build_report(
        objective="Ver",
    )

    valid, errors = build_validator().validate(
        report
    )

    assert not valid
    assert_contains_error(
        errors,
        "objetivo es demasiado corto",
    )


def test_validator_rejects_short_executive_summary() -> None:
    report = build_report(
        executive_summary="Resumen demasiado breve.",
    )

    valid, errors = build_validator().validate(
        report
    )

    assert not valid
    assert_contains_error(
        errors,
        "resumen ejecutivo es demasiado corto",
    )


def test_validator_rejects_excessive_key_points() -> None:
    report = build_report(
        key_points=[
            f"Punto confirmado número {index}."
            for index in range(
                1,
                22,
            )
        ],
    )

    valid, errors = build_validator().validate(
        report
    )

    assert not valid
    assert_contains_error(
        errors,
        "no debe contener más de 20 elementos",
    )


def test_validator_rejects_short_key_point() -> None:
    report = build_report(
        key_points=[
            "Ok.",
        ],
    )

    valid, errors = build_validator().validate(
        report
    )

    assert not valid
    assert_contains_error(
        errors,
        "punto clave #1 es demasiado corto",
    )


def test_validator_detects_duplicate_key_points() -> None:
    report = build_report(
        key_points=[
            "Se aprobó la arquitectura.",
            "  SE APROBÓ   LA ARQUITECTURA. ",
        ],
    )

    valid, errors = build_validator().validate(
        report
    )

    assert not valid
    assert_contains_error(
        errors,
        "puntos clave contiene elementos duplicados",
    )


def test_validator_detects_duplicate_conclusions() -> None:
    report = build_report(
        conclusions=[
            "Continuar con las pruebas.",
            "continuar con las pruebas.",
        ],
    )

    valid, errors = build_validator().validate(
        report
    )

    assert not valid
    assert_contains_error(
        errors,
        "conclusiones contiene elementos duplicados",
    )


def test_validator_rejects_short_topic_title() -> None:
    report = build_report(
        topics=[
            MeetingTopic(
                title="API",
                summary=(
                    "Se revisó el diseño general de la API."
                ),
            ),
        ],
    )

    valid, errors = build_validator().validate(
        report
    )

    assert not valid
    assert_contains_error(
        errors,
        "título del tema #1 es demasiado corto",
    )


def test_validator_detects_duplicate_topics() -> None:
    report = build_report(
        topics=[
            MeetingTopic(
                title="Arquitectura del sistema",
                summary="Se revisó el diseño actual.",
            ),
            MeetingTopic(
                title=" arquitectura del sistema ",
                summary="Se revisaron los componentes.",
            ),
        ],
    )

    valid, errors = build_validator().validate(
        report
    )

    assert not valid
    assert_contains_error(
        errors,
        "temas contiene elementos duplicados",
    )


@pytest.mark.parametrize(
    (
        "field_name",
        "items",
        "expected_section",
    ),
    [
        (
            "decisions",
            [
                Decision(
                    description="Aprobar el diseño.",
                ),
                Decision(
                    description=" aprobar el diseño. ",
                ),
            ],
            "decisiones",
        ),
        (
            "action_items",
            [
                ActionItem(
                    description="Ejecutar las pruebas.",
                ),
                ActionItem(
                    description=" EJECUTAR LAS PRUEBAS. ",
                ),
            ],
            "acciones",
        ),
        (
            "risks",
            [
                MeetingRisk(
                    description="Posible retraso.",
                ),
                MeetingRisk(
                    description="posible retraso.",
                ),
            ],
            "riesgos",
        ),
        (
            "pending_items",
            [
                PendingItem(
                    description="Confirmar la fecha.",
                ),
                PendingItem(
                    description=" confirmar la fecha. ",
                ),
            ],
            "asuntos pendientes",
        ),
    ],
)
def test_validator_detects_duplicate_operational_items(
    field_name: str,
    items: list,
    expected_section: str,
) -> None:
    report = build_report(
        **{
            field_name: items,
        }
    )

    valid, errors = build_validator().validate(
        report
    )

    assert not valid
    assert_contains_error(
        errors,
        (
            f"{expected_section} contiene "
            "elementos duplicados"
        ),
    )


def test_validator_rejects_short_action_description() -> None:
    report = build_report(
        action_items=[
            ActionItem(
                description="Ver.",
            ),
        ],
    )

    valid, errors = build_validator().validate(
        report
    )

    assert not valid
    assert_contains_error(
        errors,
        (
            "descripción de la acción #1 "
            "es demasiado corta"
        ),
    )


def test_validator_accepts_items_without_evidence() -> None:
    report = build_report(
        decisions=[
            Decision(
                description="Aprobar la arquitectura.",
            ),
        ],
        action_items=[
            ActionItem(
                description="Ejecutar las pruebas.",
            ),
        ],
        risks=[
            MeetingRisk(
                description="Posible retraso del proyecto.",
            ),
        ],
        pending_items=[
            PendingItem(
                description="Confirmar la fecha final.",
            ),
        ],
    )

    valid, errors = build_validator().validate(
        report
    )

    assert valid
    assert errors == []


def test_validator_rejects_short_evidence_excerpt() -> None:
    evidence = EvidenceReference(
        speaker="REMOTE",
        start=10.0,
        end=12.0,
        excerpt="Sí",
    )

    report = build_report(
        decisions=[
            Decision(
                description="Aprobar la arquitectura.",
                evidence=[
                    evidence,
                ],
            ),
        ],
    )

    valid, errors = build_validator().validate(
        report
    )

    assert not valid
    assert_contains_error(
        errors,
        (
            "evidencia #1 de la decisión #1 "
            "es demasiado corta"
        ),
    )


def test_validator_returns_all_detected_errors() -> None:
    report = build_report(
        title="AI",
        objective="Ver",
        executive_summary="Resumen breve.",
        key_points=[
            "Bien.",
            "Bien.",
        ],
    )

    valid, errors = build_validator().validate(
        report
    )

    assert not valid
    assert len(errors) >= 4

    assert_contains_error(
        errors,
        "título es demasiado corto",
    )

    assert_contains_error(
        errors,
        "objetivo es demasiado corto",
    )

    assert_contains_error(
        errors,
        "resumen ejecutivo es demasiado corto",
    )

    assert_contains_error(
        errors,
        "puntos clave contiene elementos duplicados",
    )