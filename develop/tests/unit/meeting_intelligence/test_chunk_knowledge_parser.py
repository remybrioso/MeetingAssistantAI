import json
from datetime import date

import pytest

from models.meeting_report import (
    ActionStatus,
)
from models.transcript import Segment
from models.transcript_chunk import TranscriptChunk
from services.chunk_knowledge_parser import (
    ChunkKnowledgeParser,
)


def build_chunk() -> TranscriptChunk:
    return TranscriptChunk(
        index=3,
        segments=[
            Segment(
                start=10.0,
                end=20.0,
                speaker="REMOTE",
                text=(
                    "Las pruebas no están listas. "
                    "Moveremos la implementación al próximo sprint."
                ),
            ),
            Segment(
                start=20.0,
                end=30.0,
                speaker="USER",
                text=(
                    "Remy completará las pruebas antes del viernes. "
                    "Existe riesgo de retraso."
                ),
            ),
        ],
    )


def empty_payload() -> dict:
    return {
        "key_points": [],
        "topics": [],
        "decisions": [],
        "action_items": [],
        "risks": [],
        "pending_items": [],
        "participants": [],
        "conclusions": [],
    }


def parse_payload(
    payload: dict,
):
    return ChunkKnowledgeParser().parse(
        response=json.dumps(
            payload,
            ensure_ascii=False,
        ),
        chunk=build_chunk(),
    )


def test_parser_builds_complete_chunk_knowledge() -> None:
    payload = empty_payload()

    payload.update(
        {
            "key_points": [
                "Las pruebas continúan pendientes.",
            ],
            "topics": [
                {
                    "title": "Pruebas",
                    "summary": (
                        "Se revisó el estado de las pruebas."
                    ),
                    "evidence": [
                        {
                            "speaker": "REMOTE",
                            "start": 10.0,
                            "end": 20.0,
                            "excerpt": (
                                "Las pruebas no están listas."
                            ),
                        }
                    ],
                }
            ],
            "decisions": [
                {
                    "description": (
                        "Mover la implementación al próximo sprint."
                    ),
                    "rationale": (
                        "Las pruebas no están listas."
                    ),
                    "evidence": [
                        {
                            "speaker": "REMOTE",
                            "start": 10.0,
                            "end": 20.0,
                            "excerpt": (
                                "Moveremos la implementación "
                                "al próximo sprint."
                            ),
                        }
                    ],
                }
            ],
            "action_items": [
                {
                    "description": (
                        "Completar las pruebas."
                    ),
                    "owner": {
                        "display_name": "Remy",
                    },
                    "due_date": "2026-08-28",
                    "status": "pending",
                    "evidence": [
                        {
                            "speaker": "USER",
                            "start": 20.0,
                            "end": 30.0,
                            "excerpt": (
                                "Remy completará las pruebas "
                                "antes del viernes."
                            ),
                        }
                    ],
                }
            ],
            "risks": [
                {
                    "description": (
                        "Existe riesgo de retraso."
                    ),
                    "impact": None,
                    "evidence": [
                        {
                            "speaker": "USER",
                            "start": 20.0,
                            "end": 30.0,
                            "excerpt": (
                                "Existe riesgo de retraso."
                            ),
                        }
                    ],
                }
            ],
            "pending_items": [
                {
                    "description": (
                        "Confirmar el resultado de las pruebas."
                    ),
                    "evidence": [
                        {
                            "speaker": "REMOTE",
                            "start": 10.0,
                            "end": 20.0,
                            "excerpt": (
                                "Las pruebas no están listas."
                            ),
                        }
                    ],
                }
            ],
            "participants": [
                {
                    "name": "Remy",
                    "speaker": "USER",
                    "role": None,
                }
            ],
            "conclusions": [
                "La implementación se moverá.",
            ],
        }
    )

    knowledge = parse_payload(
        payload
    )

    assert knowledge.chunk_index == 3
    assert knowledge.start == 10.0
    assert knowledge.end == 30.0

    assert len(
        knowledge.topics
    ) == 1

    assert len(
        knowledge.decisions
    ) == 1

    assert len(
        knowledge.action_items
    ) == 1

    action = knowledge.action_items[0]

    assert str(
        action.owner
    ) == "Remy"

    assert action.due_date == date(
        2026,
        8,
        28,
    )

    assert (
        action.status
        == ActionStatus.PENDING
    )


def test_parser_accepts_empty_sections() -> None:
    knowledge = parse_payload(
        empty_payload()
    )

    assert knowledge.has_content is False


def test_parser_uses_chunk_metadata_not_llm_metadata() -> None:
    payload = empty_payload()

    payload["chunk_index"] = 999

    with pytest.raises(
        ValueError,
        match="campos no soportados: chunk_index",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_invalid_json() -> None:
    with pytest.raises(
        ValueError,
        match="JSON válido",
    ):
        ChunkKnowledgeParser().parse(
            response="{invalid}",
            chunk=build_chunk(),
        )


def test_parser_rejects_missing_root_field() -> None:
    payload = empty_payload()

    del payload[
        "decisions"
    ]

    with pytest.raises(
        ValueError,
        match="campos requeridos: decisions",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_non_list_section() -> None:
    payload = empty_payload()

    payload[
        "risks"
    ] = {}

    with pytest.raises(
        TypeError,
        match="risks debe ser una lista",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_non_object_item() -> None:
    payload = empty_payload()

    payload[
        "decisions"
    ] = [
        "decisión inválida",
    ]

    with pytest.raises(
        TypeError,
        match="decisions elemento #1 debe ser un objeto",
    ):
        parse_payload(
            payload
        )


def test_parser_requires_operational_evidence() -> None:
    payload = empty_payload()

    payload[
        "decisions"
    ] = [
        {
            "description": (
                "Mover la implementación."
            ),
            "rationale": None,
            "evidence": [],
        }
    ]

    with pytest.raises(
        ValueError,
        match="requiere al menos una referencia",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_fabricated_excerpt() -> None:
    payload = empty_payload()

    payload[
        "decisions"
    ] = [
        {
            "description": (
                "Mover la implementación."
            ),
            "rationale": None,
            "evidence": [
                {
                    "speaker": "REMOTE",
                    "start": 10.0,
                    "end": 20.0,
                    "excerpt": (
                        "Esta frase nunca fue pronunciada."
                    ),
                }
            ],
        }
    ]

    with pytest.raises(
        ValueError,
        match="evidencia verificable del chunk",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_wrong_evidence_speaker() -> None:
    payload = empty_payload()

    payload[
        "risks"
    ] = [
        {
            "description": (
                "Existe riesgo de retraso."
            ),
            "impact": None,
            "evidence": [
                {
                    "speaker": "REMOTE",
                    "start": 20.0,
                    "end": 30.0,
                    "excerpt": (
                        "Existe riesgo de retraso."
                    ),
                }
            ],
        }
    ]

    with pytest.raises(
        ValueError,
        match="evidencia verificable del chunk",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_evidence_time_outside_source_segment() -> None:
    payload = empty_payload()

    payload[
        "topics"
    ] = [
        {
            "title": "Pruebas",
            "summary": (
                "Se revisaron las pruebas."
            ),
            "evidence": [
                {
                    "speaker": "REMOTE",
                    "start": 5.0,
                    "end": 20.0,
                    "excerpt": (
                        "Las pruebas no están listas."
                    ),
                }
            ],
        }
    ]

    with pytest.raises(
        ValueError,
        match="evidencia verificable del chunk",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_invalid_due_date() -> None:
    payload = empty_payload()

    payload[
        "action_items"
    ] = [
        {
            "description": (
                "Completar las pruebas."
            ),
            "owner": None,
            "due_date": "viernes",
            "status": "pending",
            "evidence": [
                {
                    "speaker": "USER",
                    "start": 20.0,
                    "end": 30.0,
                    "excerpt": (
                        "Remy completará las pruebas "
                        "antes del viernes."
                    ),
                }
            ],
        }
    ]

    with pytest.raises(
        ValueError,
        match="fecha ISO válida",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_invalid_action_status() -> None:
    payload = empty_payload()

    payload[
        "action_items"
    ] = [
        {
            "description": (
                "Completar las pruebas."
            ),
            "owner": None,
            "due_date": None,
            "status": "in_progress",
            "evidence": [
                {
                    "speaker": "USER",
                    "start": 20.0,
                    "end": 30.0,
                    "excerpt": (
                        "Remy completará las pruebas "
                        "antes del viernes."
                    ),
                }
            ],
        }
    ]

    with pytest.raises(
        ValueError,
        match="status no contiene un estado válido",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_participant_without_identity() -> None:
    payload = empty_payload()

    payload[
        "participants"
    ] = [
        {
            "name": None,
            "speaker": None,
            "role": None,
        }
    ]

    with pytest.raises(
        ValueError,
        match="Participant requiere al menos un dato",
    ):
        parse_payload(
            payload
        )


def test_parser_accepts_json_inside_code_fence() -> None:
    payload = empty_payload()

    response = (
        "```json\n"
        + json.dumps(
            payload
        )
        + "\n```"
    )

    knowledge = ChunkKnowledgeParser().parse(
        response=response,
        chunk=build_chunk(),
    )

    assert knowledge.chunk_index == 3


def test_parser_rejects_extra_nested_field() -> None:
    payload = empty_payload()

    payload[
        "pending_items"
    ] = [
        {
            "description": (
                "Confirmar las pruebas."
            ),
            "evidence": [
                {
                    "speaker": "REMOTE",
                    "start": 10.0,
                    "end": 20.0,
                    "excerpt": (
                        "Las pruebas no están listas."
                    ),
                }
            ],
            "invented": True,
        }
    ]

    with pytest.raises(
        ValueError,
        match="campos no soportados: invented",
    ):
        parse_payload(
            payload
        )
