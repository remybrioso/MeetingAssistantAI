from datetime import date

import pytest

from models.meeting_report import (
    ActionOwner,
    ActionStatus,
)
from services.meeting_report_parser import (
    MeetingReportParser,
)


def build_parser() -> MeetingReportParser:
    return MeetingReportParser()


def build_response(
    action_items_json: str,
) -> str:
    return f"""
    {{
        "title": "Reunión técnica",
        "executive_summary": "Se revisaron los compromisos.",
        "key_points": [
            "Se definieron acciones de seguimiento."
        ],
        "action_items": {action_items_json}
    }}
    """


def parse_action_items(
    action_items_json: str,
):
    return build_parser().parse(
        response=build_response(
            action_items_json
        ),
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
    )


def test_parser_builds_complete_action_item() -> None:
    report = parse_action_items(
        """
        [
            {
                "description": "Actualizar el servidor Oracle.",
                "owner": {
                    "display_name": "Equipo DBA"
                },
                "due_date": "2026-08-15",
                "status": "pending",
                "evidence": [
                    {
                        "speaker": "REMOTE",
                        "start": 40.0,
                        "end": 46.5,
                        "excerpt": "El equipo DBA actualizará el servidor."
                    }
                ]
            }
        ]
        """
    )

    assert len(report.action_items) == 1

    action = report.action_items[0]

    assert (
        action.description
        == "Actualizar el servidor Oracle."
    )

    assert isinstance(
        action.owner,
        ActionOwner,
    )

    assert (
        action.owner.display_name
        == "Equipo DBA"
    )

    assert action.due_date == date(
        2026,
        8,
        15,
    )

    assert action.status is ActionStatus.PENDING
    assert len(action.evidence) == 1


def test_parser_accepts_owner_as_string() -> None:
    report = parse_action_items(
        """
        [
            {
                "description": "Preparar el informe.",
                "owner": " Remy "
            }
        ]
        """
    )

    action = report.action_items[0]

    assert isinstance(
        action.owner,
        ActionOwner,
    )

    assert action.owner.display_name == "Remy"


def test_parser_accepts_null_owner() -> None:
    report = parse_action_items(
        """
        [
            {
                "description": "Revisar la documentación.",
                "owner": null
            }
        ]
        """
    )

    assert report.action_items[0].owner is None


def test_parser_accepts_missing_owner() -> None:
    report = parse_action_items(
        """
        [
            {
                "description": "Revisar la documentación."
            }
        ]
        """
    )

    assert report.action_items[0].owner is None


def test_parser_uses_unknown_for_missing_status() -> None:
    report = parse_action_items(
        """
        [
            {
                "description": "Ejecutar las pruebas."
            }
        ]
        """
    )

    assert (
        report.action_items[0].status
        is ActionStatus.UNKNOWN
    )


def test_parser_uses_unknown_for_null_status() -> None:
    report = parse_action_items(
        """
        [
            {
                "description": "Ejecutar las pruebas.",
                "status": null
            }
        ]
        """
    )

    assert (
        report.action_items[0].status
        is ActionStatus.UNKNOWN
    )


def test_parser_normalizes_status_text() -> None:
    report = parse_action_items(
        """
        [
            {
                "description": "Ejecutar las pruebas.",
                "status": " COMPLETED "
            }
        ]
        """
    )

    assert (
        report.action_items[0].status
        is ActionStatus.COMPLETED
    )


def test_parser_rejects_unknown_status() -> None:
    with pytest.raises(
        ValueError,
        match="status es inválido",
    ):
        parse_action_items(
            """
            [
                {
                    "description": "Ejecutar las pruebas.",
                    "status": "in progress"
                }
            ]
            """
        )


def test_parser_accepts_null_due_date() -> None:
    report = parse_action_items(
        """
        [
            {
                "description": "Ejecutar las pruebas.",
                "due_date": null
            }
        ]
        """
    )

    assert report.action_items[0].due_date is None


def test_parser_accepts_missing_due_date() -> None:
    report = parse_action_items(
        """
        [
            {
                "description": "Ejecutar las pruebas."
            }
        ]
        """
    )

    assert report.action_items[0].due_date is None


def test_parser_rejects_invalid_iso_due_date() -> None:
    with pytest.raises(
        ValueError,
        match="fecha ISO válida",
    ):
        parse_action_items(
            """
            [
                {
                    "description": "Ejecutar las pruebas.",
                    "due_date": "15-08-2026"
                }
            ]
            """
        )


def test_parser_rejects_ambiguous_due_date() -> None:
    with pytest.raises(
        ValueError,
        match="fecha ISO válida",
    ):
        parse_action_items(
            """
            [
                {
                    "description": "Ejecutar las pruebas.",
                    "due_date": "el próximo viernes"
                }
            ]
            """
        )


def test_parser_rejects_non_string_due_date() -> None:
    with pytest.raises(
        TypeError,
        match="due_date debe ser una cadena ISO",
    ):
        parse_action_items(
            """
            [
                {
                    "description": "Ejecutar las pruebas.",
                    "due_date": 20260815
                }
            ]
            """
        )


def test_parser_rejects_empty_due_date() -> None:
    with pytest.raises(
        ValueError,
        match="due_date no puede estar vacío",
    ):
        parse_action_items(
            """
            [
                {
                    "description": "Ejecutar las pruebas.",
                    "due_date": "   "
                }
            ]
            """
        )


def test_parser_rejects_owner_object_without_display_name() -> None:
    with pytest.raises(
        ValueError,
        match="display_name",
    ):
        parse_action_items(
            """
            [
                {
                    "description": "Ejecutar las pruebas.",
                    "owner": {
                        "name": "Remy"
                    }
                }
            ]
            """
        )


def test_parser_rejects_invalid_owner_type() -> None:
    with pytest.raises(
        TypeError,
        match="owner debe ser una cadena",
    ):
        parse_action_items(
            """
            [
                {
                    "description": "Ejecutar las pruebas.",
                    "owner": 123
                }
            ]
            """
        )


def test_parser_rejects_non_list_action_items() -> None:
    with pytest.raises(
        TypeError,
        match="action_items debe ser una lista",
    ):
        parse_action_items(
            """
            {
                "description": "Ejecutar las pruebas."
            }
            """
        )


def test_parser_rejects_non_object_action_item() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "action_items elemento #1 debe ser "
            "un objeto"
        ),
    ):
        parse_action_items(
            """
            [
                "acción inválida"
            ]
            """
        )


def test_parser_requires_action_description() -> None:
    with pytest.raises(
        ValueError,
        match="action_items elemento #1",
    ) as error:
        parse_action_items(
            """
            [
                {
                    "owner": "Remy"
                }
            ]
            """
        )

    assert "description" in str(
        error.value
    )


def test_parser_accepts_empty_action_items() -> None:
    report = parse_action_items(
        "[]"
    )

    assert report.action_items == []


def test_action_item_serialization_matches_contract() -> None:
    report = parse_action_items(
        """
        [
            {
                "description": "Preparar el informe.",
                "owner": "Remy",
                "due_date": "2026-08-15",
                "status": "pending"
            }
        ]
        """
    )

    assert report.as_dict()["action_items"] == [
        {
            "description": "Preparar el informe.",
            "evidence": [],
            "owner": {
                "display_name": "Remy",
            },
            "due_date": "2026-08-15",
            "status": "pending",
        },
    ]