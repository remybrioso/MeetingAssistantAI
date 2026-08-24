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

def test_parser_builds_topics_with_evidence() -> None:
    response = """
    {
        "title": "Reunión técnica",
        "executive_summary": "Se revisó la arquitectura.",
        "key_points": [
            "La arquitectura fue validada."
        ],
        "topics": [
            {
                "title": "Arquitectura",
                "summary": "Se revisó el diseño del sistema.",
                "evidence": [
                    {
                        "speaker": "REMOTE",
                        "start": 10.0,
                        "end": 15.5,
                        "excerpt": "La arquitectura queda aprobada."
                    }
                ]
            }
        ]
    }
    """

    report = build_parser().parse(
        response=response,
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
    )

    assert len(report.topics) == 1

    topic = report.topics[0]

    assert topic.title == "Arquitectura"

    assert (
        topic.summary
        == "Se revisó el diseño del sistema."
    )

    assert len(topic.evidence) == 1
    assert topic.evidence[0].speaker == "REMOTE"
    assert topic.evidence[0].start == 10.0
    assert topic.evidence[0].end == 15.5


def test_parser_builds_participants() -> None:
    response = """
    {
        "title": "Reunión técnica",
        "executive_summary": "Se revisó la arquitectura.",
        "key_points": [
            "La arquitectura fue validada."
        ],
        "participants": [
            {
                "name": "Remy",
                "speaker": "LOCAL",
                "role": "Coordinador"
            },
            {
                "name": null,
                "speaker": "REMOTE",
                "role": null
            }
        ]
    }
    """

    report = build_parser().parse(
        response=response,
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
    )

    assert len(report.participants) == 2

    first_participant = report.participants[0]

    assert first_participant.name == "Remy"
    assert first_participant.speaker == "LOCAL"

    second_participant = report.participants[1]

    assert second_participant.name is None
    assert second_participant.speaker == "REMOTE"
    assert second_participant.role is None


def test_parser_accepts_empty_topics_and_participants() -> None:
    response = """
    {
        "title": "Reunión técnica",
        "executive_summary": "Se revisó la arquitectura.",
        "key_points": [
            "La arquitectura fue validada."
        ],
        "topics": [],
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
    assert report.participants == []


def test_parser_rejects_non_list_topics() -> None:
    response = """
    {
        "title": "Reunión técnica",
        "executive_summary": "Se revisó la arquitectura.",
        "key_points": [
            "La arquitectura fue validada."
        ],
        "topics": {}
    }
    """

    with pytest.raises(
        TypeError,
        match="topics debe ser una lista",
    ):
        build_parser().parse(
            response=response,
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
        )


def test_parser_rejects_non_object_topic() -> None:
    response = """
    {
        "title": "Reunión técnica",
        "executive_summary": "Se revisó la arquitectura.",
        "key_points": [
            "La arquitectura fue validada."
        ],
        "topics": [
            "tema inválido"
        ]
    }
    """

    with pytest.raises(
        TypeError,
        match=(
            "topics elemento #1 debe ser un objeto"
        ),
    ):
        build_parser().parse(
            response=response,
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
        )


def test_parser_reports_missing_topic_fields() -> None:
    response = """
    {
        "title": "Reunión técnica",
        "executive_summary": "Se revisó la arquitectura.",
        "key_points": [
            "La arquitectura fue validada."
        ],
        "topics": [
            {
                "title": "Arquitectura"
            }
        ]
    }
    """

    with pytest.raises(
        ValueError,
        match="topics elemento #1",
    ) as error:
        build_parser().parse(
            response=response,
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
        )

    assert "summary" in str(
        error.value
    )


def test_parser_rejects_invalid_topic_evidence_type() -> None:
    response = """
    {
        "title": "Reunión técnica",
        "executive_summary": "Se revisó la arquitectura.",
        "key_points": [
            "La arquitectura fue validada."
        ],
        "topics": [
            {
                "title": "Arquitectura",
                "summary": "Se revisó el diseño.",
                "evidence": {}
            }
        ]
    }
    """

    with pytest.raises(
        TypeError,
        match=(
            "topics elemento #1 evidence "
            "debe ser una lista"
        ),
    ):
        build_parser().parse(
            response=response,
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
        )


def test_parser_rejects_incomplete_evidence() -> None:
    response = """
    {
        "title": "Reunión técnica",
        "executive_summary": "Se revisó la arquitectura.",
        "key_points": [
            "La arquitectura fue validada."
        ],
        "topics": [
            {
                "title": "Arquitectura",
                "summary": "Se revisó el diseño.",
                "evidence": [
                    {
                        "speaker": "REMOTE",
                        "start": 10.0
                    }
                ]
            }
        ]
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

    assert "end" in message
    assert "excerpt" in message


def test_parser_rejects_non_list_participants() -> None:
    response = """
    {
        "title": "Reunión técnica",
        "executive_summary": "Se revisó la arquitectura.",
        "key_points": [
            "La arquitectura fue validada."
        ],
        "participants": {}
    }
    """

    with pytest.raises(
        TypeError,
        match="participants debe ser una lista",
    ):
        build_parser().parse(
            response=response,
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
        )


def test_parser_rejects_completely_empty_participant() -> None:
    response = """
    {
        "title": "Reunión técnica",
        "executive_summary": "Se revisó la arquitectura.",
        "key_points": [
            "La arquitectura fue validada."
        ],
        "participants": [
            {}
        ]
    }
    """

    with pytest.raises(
        ValueError,
        match="requiere al menos un dato",
    ):
        build_parser().parse(
            response=response,
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
        )

def test_parser_builds_decisions() -> None:
    response = """
    {
        "title": "Reunión técnica",
        "executive_summary": "Se revisó el proyecto.",
        "key_points": [
            "Se aprobó mover la implementación."
        ],
        "decisions": [
            {
                "description": "Mover la implementación.",
                "rationale": "Las pruebas no están listas.",
                "evidence": [
                    {
                        "speaker": "REMOTE",
                        "start": 20.0,
                        "end": 25.0,
                        "excerpt": "Moveremos la implementación."
                    }
                ]
            }
        ]
    }
    """

    report = build_parser().parse(
        response=response,
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
    )

    assert len(report.decisions) == 1

    decision = report.decisions[0]

    assert (
        decision.description
        == "Mover la implementación."
    )

    assert (
        decision.rationale
        == "Las pruebas no están listas."
    )

    assert len(decision.evidence) == 1


def test_parser_builds_risks() -> None:
    response = """
    {
        "title": "Reunión técnica",
        "executive_summary": "Se revisó el proyecto.",
        "key_points": [
            "Existe riesgo de retraso."
        ],
        "risks": [
            {
                "description": "Las pruebas pueden retrasarse.",
                "impact": "El despliegue podría moverse.",
                "evidence": []
            }
        ]
    }
    """

    report = build_parser().parse(
        response=response,
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
    )

    assert len(report.risks) == 1

    risk = report.risks[0]

    assert (
        risk.description
        == "Las pruebas pueden retrasarse."
    )

    assert (
        risk.impact
        == "El despliegue podría moverse."
    )


def test_parser_builds_pending_items() -> None:
    response = """
    {
        "title": "Reunión técnica",
        "executive_summary": "Se revisó el proyecto.",
        "key_points": [
            "Falta confirmar la ventana."
        ],
        "pending_items": [
            {
                "description": "Confirmar la ventana.",
                "evidence": []
            }
        ]
    }
    """

    report = build_parser().parse(
        response=response,
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
    )

    assert len(report.pending_items) == 1

    assert (
        report.pending_items[0].description
        == "Confirmar la ventana."
    )


@pytest.mark.parametrize(
    (
        "field_name",
        "expected_message",
    ),
    [
        (
            "decisions",
            "decisions debe ser una lista",
        ),
        (
            "risks",
            "risks debe ser una lista",
        ),
        (
            "pending_items",
            "pending_items debe ser una lista",
        ),
    ],
)
def test_parser_rejects_non_list_supported_sections(
    field_name: str,
    expected_message: str,
) -> None:
    response = f"""
    {{
        "title": "Reunión técnica",
        "executive_summary": "Contenido.",
        "key_points": [
            "Punto confirmado."
        ],
        "{field_name}": {{}}
    }}
    """

    with pytest.raises(
        TypeError,
        match=expected_message,
    ):
        build_parser().parse(
            response=response,
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "decisions",
        "risks",
        "pending_items",
    ],
)
def test_parser_rejects_non_object_supported_items(
    field_name: str,
) -> None:
    response = f"""
    {{
        "title": "Reunión técnica",
        "executive_summary": "Contenido.",
        "key_points": [
            "Punto confirmado."
        ],
        "{field_name}": [
            "elemento inválido"
        ]
    }}
    """

    with pytest.raises(
        TypeError,
        match=(
            f"{field_name} elemento #1 debe ser "
            "un objeto"
        ),
    ):
        build_parser().parse(
            response=response,
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "decisions",
        "risks",
        "pending_items",
    ],
)
def test_parser_requires_description_in_operational_items(
    field_name: str,
) -> None:
    response = f"""
    {{
        "title": "Reunión técnica",
        "executive_summary": "Contenido.",
        "key_points": [
            "Punto confirmado."
        ],
        "{field_name}": [
            {{}}
        ]
    }}
    """

    with pytest.raises(
        ValueError,
        match=(
            f"{field_name} elemento #1"
        ),
    ) as error:
        build_parser().parse(
            response=response,
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
        )

    assert "description" in str(
        error.value
    )

def test_parser_ignores_completely_empty_topic_placeholder() -> None:
    response = """
    {
        "title": "Reunión técnica",
        "executive_summary": "Se revisó el estado general del proyecto.",
        "key_points": [
            "Se revisó el estado actual del proyecto."
        ],
        "topics": [
            {
                "title": "",
                "summary": "",
                "evidence": [
                    {
                        "speaker": "USER",
                        "start": 10.0,
                        "end": 12.0,
                        "excerpt": "Fragmento sin tema identificable."
                    }
                ]
            }
        ]
    }
    """

    report = build_parser().parse(
        response=response,
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
    )

    assert report.topics == []


def test_parser_rejects_partially_empty_topic() -> None:
    response = """
    {
        "title": "Reunión técnica",
        "executive_summary": "Se revisó el estado general del proyecto.",
        "key_points": [
            "Se revisó el estado actual del proyecto."
        ],
        "topics": [
            {
                "title": "",
                "summary": "Se revisó la arquitectura del sistema.",
                "evidence": []
            }
        ]
    }
    """

    with pytest.raises(
        ValueError,
        match="MeetingTopic title no puede estar vacío",
    ):
        build_parser().parse(
            response=response,
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="meeting_report_v1",
        )

