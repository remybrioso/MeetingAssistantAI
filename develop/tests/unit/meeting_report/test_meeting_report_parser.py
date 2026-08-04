import pytest

from models.artifacts.meeting_report import MeetingReport
from services.meeting_report_parser import (
    MeetingReportParser,
)


def build_parser() -> MeetingReportParser:
    return MeetingReportParser()


def test_parser_creates_minimal_meeting_report() -> None:
    response = """
    {
        "title": "Reunión técnica",
        "executive_summary": "Se revisó la arquitectura.",
        "key_points": [
            "La arquitectura fue validada."
        ]
    }
    """

    report = build_parser().parse(
        response=response,
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
    )

    assert isinstance(
        report,
        MeetingReport,
    )

    assert report.artifact_type == "meeting_report"
    assert report.provider == "ollama"
    assert report.model == "qwen2.5:3b"

    assert (
        report.prompt_version
        == "meeting_report_v1"
    )

    assert report.title == "Reunión técnica"

    assert (
        report.executive_summary
        == "Se revisó la arquitectura."
    )

    assert report.key_points == [
        "La arquitectura fue validada.",
    ]

    assert report.objective is None
    assert report.topics == []
    assert report.decisions == []
    assert report.action_items == []
    assert report.risks == []
    assert report.pending_items == []
    assert report.participants == []
    assert report.conclusions == []


def test_parser_preserves_optional_base_fields() -> None:
    response = """
    {
        "title": "Seguimiento",
        "objective": "Revisar el proyecto.",
        "executive_summary": "Se revisó el avance.",
        "key_points": [
            "El proyecto continúa."
        ],
        "conclusions": [
            "Continuar con las pruebas."
        ]
    }
    """

    report = build_parser().parse(
        response=response,
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
    )

    assert (
        report.objective
        == "Revisar el proyecto."
    )

    assert report.conclusions == [
        "Continuar con las pruebas.",
    ]


def test_parser_accepts_json_markdown_block() -> None:
    response = """
    ```json
    {
        "title": "Reunión técnica",
        "executive_summary": "Se revisó el sistema.",
        "key_points": [
            "El sistema fue revisado."
        ]
    }
    ```
    """

    report = build_parser().parse(
        response=response,
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
    )

    assert report.title == "Reunión técnica"


def test_parser_extracts_json_from_external_text() -> None:
    response = """
    Resultado generado:

    {
        "title": "Reunión técnica",
        "executive_summary": "Se revisó el sistema.",
        "key_points": [
            "El sistema fue revisado."
        ]
    }

    Fin de la respuesta.
    """

    report = build_parser().parse(
        response=response,
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
    )

    assert report.title == "Reunión técnica"


def test_parser_rejects_empty_response() -> None:
    with pytest.raises(
        ValueError,
        match="respuesta de IA está vacía",
    ):
        build_parser().parse(
            response="   ",
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
        )


def test_parser_rejects_invalid_json() -> None:
    response = """
    {
        "title": "Reunión",
        "executive_summary": "Contenido",
    }
    """

    with pytest.raises(
        ValueError,
        match="no contiene JSON válido",
    ):
        build_parser().parse(
            response=response,
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
        )


def test_parser_rejects_non_object_json_root() -> None:
    with pytest.raises(
        TypeError,
        match="debe contener un objeto JSON",
    ):
        MeetingReportParser._validate_root_object(
            [
                {
                    "title": "Reunión",
                },
            ]
        )


def test_parser_reports_missing_required_fields() -> None:
    response = """
    {
        "title": "Reunión"
    }
    """

    with pytest.raises(
        ValueError,
        match="campos requeridos",
    ) as error:
        build_parser().parse(
            response=response,
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
        )

    message = str(
        error.value
    )

    assert "executive_summary" in message
    assert "key_points" in message


def test_parser_rejects_non_list_key_points() -> None:
    response = """
    {
        "title": "Reunión",
        "executive_summary": "Contenido",
        "key_points": "Punto único"
    }
    """

    with pytest.raises(
        TypeError,
        match="key_points debe ser una lista",
    ):
        build_parser().parse(
            response=response,
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
        )


def test_parser_rejects_non_list_conclusions() -> None:
    response = """
    {
        "title": "Reunión",
        "executive_summary": "Contenido",
        "key_points": [
            "Punto confirmado."
        ],
        "conclusions": "Continuar."
    }
    """

    with pytest.raises(
        TypeError,
        match="conclusions debe ser una lista",
    ):
        build_parser().parse(
            response=response,
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
        )


def test_parser_accepts_empty_nested_sections() -> None:
    response = """
    {
        "title": "Reunión",
        "executive_summary": "Contenido",
        "key_points": [
            "Punto confirmado."
        ],
        "topics": [],
        "decisions": [],
        "action_items": [],
        "risks": [],
        "pending_items": [],
        "participants": []
    }
    """

    report = build_parser().parse(
        response=response,
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
    )

    assert report.topics == []
    assert report.decisions == []
    assert report.action_items == []


def test_parser_rejects_non_empty_unsupported_section() -> None:
    response = """
    {
        "title": "Reunión",
        "executive_summary": "Contenido",
        "key_points": [
            "Punto confirmado."
        ],
        "topics": [
            {
                "title": "Arquitectura",
                "summary": "Se revisó el diseño."
            }
        ]
    }
    """

    with pytest.raises(
        ValueError,
        match="topics todavía no está soportado",
    ):
        build_parser().parse(
            response=response,
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
        )


def test_parser_delegates_text_validation_to_domain() -> None:
    response = """
    {
        "title": "   ",
        "executive_summary": "Contenido",
        "key_points": [
            "Punto confirmado."
        ]
    }
    """

    with pytest.raises(
        ValueError,
        match="title no puede estar vacío",
    ):
        build_parser().parse(
            response=response,
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
        )