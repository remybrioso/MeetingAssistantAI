from collections.abc import Callable

import pytest

from models.artifacts.meeting_report import MeetingReport
from models.meeting_report import (
    ActionItem,
    Decision,
    MeetingRisk,
    MeetingTopic,
    Participant,
    PendingItem,
)


def build_report(
    **overrides,
) -> MeetingReport:
    """
    Construye un MeetingReport válido y permite sustituir
    únicamente los campos necesarios para cada prueba.
    """

    data = {
        "artifact_type": "meeting_report",
        "provider": "ollama",
        "model": "qwen2.5:3b",
        "prompt_version": "meeting_report_v1",
        "title": "Reunión de seguimiento",
        "objective": "Revisar el estado del proyecto.",
        "executive_summary": (
            "Se revisó el avance general y se definieron "
            "los próximos pasos."
        ),
        "key_points": [
            "El proyecto continúa en ejecución.",
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


def test_meeting_report_converts_empty_objective_to_none() -> None:
    report = build_report(
        objective="   ",
    )

    assert report.objective is None
    assert report.as_dict()["objective"] is None


@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
        "expected_message",
    ),
    [
        (
            "title",
            123,
            "MeetingReport title debe ser una cadena",
        ),
        (
            "objective",
            123,
            (
                "MeetingReport objective debe ser "
                "una cadena o None"
            ),
        ),
        (
            "executive_summary",
            [],
            (
                "MeetingReport executive_summary "
                "debe ser una cadena"
            ),
        ),
    ],
)
def test_meeting_report_rejects_invalid_text_field_types(
    field_name: str,
    invalid_value,
    expected_message: str,
) -> None:
    with pytest.raises(
        TypeError,
        match=expected_message,
    ):
        build_report(
            **{
                field_name: invalid_value,
            }
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "key_points",
        "conclusions",
        "topics",
        "decisions",
        "action_items",
        "risks",
        "pending_items",
        "participants",
    ],
)
def test_meeting_report_requires_list_collections(
    field_name: str,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            f"MeetingReport {field_name} "
            "debe ser una lista"
        ),
    ):
        build_report(
            **{
                field_name: (),
            }
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "values",
        "expected_message",
    ),
    [
        (
            "key_points",
            [
                123,
            ],
            (
                "MeetingReport key_points elemento #1 "
                "debe ser una cadena"
            ),
        ),
        (
            "conclusions",
            [
                None,
            ],
            (
                "MeetingReport conclusions elemento #1 "
                "debe ser una cadena"
            ),
        ),
    ],
)
def test_meeting_report_rejects_non_string_text_items(
    field_name: str,
    values: list,
    expected_message: str,
) -> None:
    with pytest.raises(
        TypeError,
        match=expected_message,
    ):
        build_report(
            **{
                field_name: values,
            }
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "values",
        "expected_message",
    ),
    [
        (
            "key_points",
            [
                "   ",
            ],
            (
                "MeetingReport key_points elemento #1 "
                "no puede estar vacío"
            ),
        ),
        (
            "conclusions",
            [
                "",
            ],
            (
                "MeetingReport conclusions elemento #1 "
                "no puede estar vacío"
            ),
        ),
    ],
)
def test_meeting_report_rejects_empty_text_items(
    field_name: str,
    values: list[str],
    expected_message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=expected_message,
    ):
        build_report(
            **{
                field_name: values,
            }
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_item",
        "expected_type_name",
    ),
    [
        (
            "topics",
            {
                "title": "Tema crudo",
            },
            "MeetingTopic",
        ),
        (
            "decisions",
            {
                "description": "Decisión cruda",
            },
            "Decision",
        ),
        (
            "action_items",
            {
                "description": "Acción cruda",
            },
            "ActionItem",
        ),
        (
            "risks",
            {
                "description": "Riesgo crudo",
            },
            "MeetingRisk",
        ),
        (
            "pending_items",
            {
                "description": "Pendiente crudo",
            },
            "PendingItem",
        ),
        (
            "participants",
            {
                "name": "Participante crudo",
            },
            "Participant",
        ),
    ],
)
def test_meeting_report_rejects_raw_domain_dictionaries(
    field_name: str,
    invalid_item: dict,
    expected_type_name: str,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            f"MeetingReport {field_name} "
            "elemento #1 debe ser una instancia de "
            f"{expected_type_name}"
        ),
    ):
        build_report(
            **{
                field_name: [
                    invalid_item,
                ],
            }
        )


def test_meeting_report_reports_invalid_item_position() -> None:
    valid_topic = MeetingTopic(
        title="Arquitectura",
        summary="Se revisó el diseño del sistema.",
    )

    with pytest.raises(
        TypeError,
        match=(
            "MeetingReport topics elemento #2 "
            "debe ser una instancia de MeetingTopic"
        ),
    ):
        build_report(
            topics=[
                valid_topic,
                "tema inválido",
            ],
        )


def test_meeting_report_normalizes_all_text_collections() -> None:
    report = build_report(
        key_points=[
            " Primer punto. ",
            " Segundo punto. ",
        ],
        conclusions=[
            " Continuar con las pruebas. ",
            " Preparar la siguiente tarea. ",
        ],
    )

    assert report.key_points == [
        "Primer punto.",
        "Segundo punto.",
    ]

    assert report.conclusions == [
        "Continuar con las pruebas.",
        "Preparar la siguiente tarea.",
    ]


@pytest.mark.parametrize(
    (
        "field_name",
        "factory",
    ),
    [
        (
            "topics",
            lambda: MeetingTopic(
                title="Arquitectura",
                summary="Se revisó la arquitectura.",
            ),
        ),
        (
            "decisions",
            lambda: Decision(
                description="Aprobar el diseño.",
            ),
        ),
        (
            "action_items",
            lambda: ActionItem(
                description="Ejecutar las pruebas.",
            ),
        ),
        (
            "risks",
            lambda: MeetingRisk(
                description="Posible retraso.",
            ),
        ),
        (
            "pending_items",
            lambda: PendingItem(
                description="Confirmar la fecha.",
            ),
        ),
        (
            "participants",
            lambda: Participant(
                speaker="REMOTE",
            ),
        ),
    ],
)
def test_meeting_report_copies_domain_collections(
    field_name: str,
    factory: Callable,
) -> None:
    item = factory()

    original_collection = [
        item,
    ]

    report = build_report(
        **{
            field_name: original_collection,
        }
    )

    original_collection.clear()

    assert getattr(
        report,
        field_name,
    ) == [
        item,
    ]


def test_meeting_report_copies_key_points() -> None:
    key_points = [
        "Punto confirmado.",
    ]

    report = build_report(
        key_points=key_points,
    )

    key_points.clear()

    assert report.key_points == [
        "Punto confirmado.",
    ]


def test_meeting_report_copies_conclusions() -> None:
    conclusions = [
        "Continuar con las pruebas.",
    ]

    report = build_report(
        conclusions=conclusions,
    )

    conclusions.clear()

    assert report.conclusions == [
        "Continuar con las pruebas.",
    ]


def test_meeting_report_as_dict_returns_new_text_lists() -> None:
    report = build_report(
        key_points=[
            "Punto confirmado.",
        ],
        conclusions=[
            "Continuar con las pruebas.",
        ],
    )

    data = report.as_dict()

    data["key_points"].append(
        "Punto agregado externamente."
    )

    data["conclusions"].clear()

    assert report.key_points == [
        "Punto confirmado.",
    ]

    assert report.conclusions == [
        "Continuar con las pruebas.",
    ]


def test_meeting_report_as_dict_contains_all_sections() -> None:
    data = build_report().as_dict()

    expected_fields = {
        "artifact_type",
        "provider",
        "model",
        "prompt_version",
        "created_at",
        "title",
        "objective",
        "executive_summary",
        "key_points",
        "topics",
        "decisions",
        "action_items",
        "risks",
        "pending_items",
        "participants",
        "conclusions",
    }

    assert set(
        data.keys()
    ) == expected_fields