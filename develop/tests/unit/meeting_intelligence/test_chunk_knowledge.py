import json
from datetime import date
from pathlib import Path

import pytest

from models.chunk_knowledge import ChunkKnowledge
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


def build_evidence(
    start: float = 12.0,
    end: float = 18.0,
) -> EvidenceReference:
    return EvidenceReference(
        speaker="REMOTE",
        start=start,
        end=end,
        excerpt=(
            "La implementación se moverá al próximo sprint."
        ),
    )


def test_chunk_knowledge_accepts_empty_knowledge() -> None:
    knowledge = ChunkKnowledge(
        chunk_index=0,
        start=0.0,
        end=30.0,
    )

    assert knowledge.has_content is False
    assert knowledge.key_points == []
    assert knowledge.decisions == []


def test_chunk_knowledge_accepts_complete_domain() -> None:
    evidence = build_evidence()

    knowledge = ChunkKnowledge(
        chunk_index=2,
        start=10.0,
        end=30.0,
        key_points=[
            "Las pruebas continúan pendientes.",
        ],
        topics=[
            MeetingTopic(
                title="Pruebas",
                summary="Se revisó el estado de las pruebas.",
                evidence=[evidence],
            ),
        ],
        decisions=[
            Decision(
                description="Mover la implementación.",
                rationale="Las pruebas no están listas.",
                evidence=[evidence],
            ),
        ],
        action_items=[
            ActionItem(
                description="Completar las pruebas.",
                owner="Equipo Oracle",
                due_date=date(2026, 8, 30),
                status=ActionStatus.PENDING,
                evidence=[evidence],
            ),
        ],
        risks=[
            MeetingRisk(
                description="Posible retraso.",
                impact="La fecha podría moverse.",
                evidence=[evidence],
            ),
        ],
        pending_items=[
            PendingItem(
                description="Confirmar la ventana.",
                evidence=[evidence],
            ),
        ],
        participants=[
            Participant(
                name="Remy",
                speaker="REMOTE",
                role="Coordinador",
            ),
        ],
        conclusions=[
            "Se dará seguimiento a las pruebas.",
        ],
    )

    assert knowledge.has_content is True

    data = knowledge.as_dict()

    assert data["chunk_index"] == 2
    assert data["start"] == 10.0
    assert data["end"] == 30.0
    assert len(data["topics"]) == 1
    assert len(data["decisions"]) == 1
    assert len(data["action_items"]) == 1
    assert len(data["risks"]) == 1
    assert len(data["pending_items"]) == 1
    assert len(data["participants"]) == 1


@pytest.mark.parametrize(
    (
        "kwargs",
        "expected_error",
    ),
    [
        (
            {
                "chunk_index": -1,
                "start": 0.0,
                "end": 10.0,
            },
            "chunk_index no puede ser negativo",
        ),
        (
            {
                "chunk_index": 0,
                "start": -1.0,
                "end": 10.0,
            },
            "start no puede ser negativo",
        ),
        (
            {
                "chunk_index": 0,
                "start": 20.0,
                "end": 10.0,
            },
            "end no puede ser menor",
        ),
    ],
)
def test_chunk_knowledge_rejects_invalid_source_metadata(
    kwargs: dict,
    expected_error: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=expected_error,
    ):
        ChunkKnowledge(
            **kwargs
        )


def test_chunk_knowledge_normalizes_text_collections() -> None:
    knowledge = ChunkKnowledge(
        chunk_index=0,
        start=0.0,
        end=10.0,
        key_points=[
            " Punto confirmado. ",
        ],
        conclusions=[
            " Cierre confirmado. ",
        ],
    )

    assert knowledge.key_points == [
        "Punto confirmado.",
    ]
    assert knowledge.conclusions == [
        "Cierre confirmado.",
    ]


def test_chunk_knowledge_rejects_empty_text_item() -> None:
    with pytest.raises(
        ValueError,
        match="key_points elemento #1 no puede estar vacío",
    ):
        ChunkKnowledge(
            chunk_index=0,
            start=0.0,
            end=10.0,
            key_points=[
                "   ",
            ],
        )


def test_chunk_knowledge_rejects_raw_domain_dictionary() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "decisions elemento #1 debe ser una instancia "
            "de Decision"
        ),
    ):
        ChunkKnowledge(
            chunk_index=0,
            start=0.0,
            end=10.0,
            decisions=[
                {
                    "description": "Decisión cruda",
                },
            ],
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "factory",
    ),
    [
        (
            "topics",
            lambda evidence: MeetingTopic(
                title="Arquitectura",
                summary="Se revisó el diseño.",
                evidence=[evidence],
            ),
        ),
        (
            "decisions",
            lambda evidence: Decision(
                description="Aprobar el diseño.",
                evidence=[evidence],
            ),
        ),
        (
            "action_items",
            lambda evidence: ActionItem(
                description="Ejecutar las pruebas.",
                evidence=[evidence],
            ),
        ),
        (
            "risks",
            lambda evidence: MeetingRisk(
                description="Posible retraso.",
                evidence=[evidence],
            ),
        ),
        (
            "pending_items",
            lambda evidence: PendingItem(
                description="Confirmar la fecha.",
                evidence=[evidence],
            ),
        ),
    ],
)
def test_chunk_knowledge_rejects_evidence_outside_chunk(
    field_name: str,
    factory,
) -> None:
    evidence = build_evidence(
        start=5.0,
        end=25.0,
    )

    with pytest.raises(
        ValueError,
        match="fuera del rango temporal del chunk",
    ):
        ChunkKnowledge(
            chunk_index=0,
            start=10.0,
            end=20.0,
            **{
                field_name: [
                    factory(evidence),
                ],
            },
        )


def test_chunk_knowledge_copies_collections() -> None:
    points = [
        "Punto confirmado.",
    ]

    decision = Decision(
        description="Aprobar el diseño.",
    )

    decisions = [
        decision,
    ]

    knowledge = ChunkKnowledge(
        chunk_index=0,
        start=0.0,
        end=10.0,
        key_points=points,
        decisions=decisions,
    )

    points.clear()
    decisions.clear()

    assert knowledge.key_points == [
        "Punto confirmado.",
    ]
    assert knowledge.decisions == [
        decision,
    ]


def test_chunk_knowledge_schema_is_valid_json() -> None:
    schema = json.loads(
        Path(
            "prompts/schemas/chunk_knowledge_v1.json"
        ).read_text(
            encoding="utf-8"
        )
    )

    assert schema["type"] == "object"

    assert set(
        schema["required"]
    ) == {
        "key_points",
        "topics",
        "decisions",
        "action_items",
        "risks",
        "pending_items",
        "participants",
        "conclusions",
    }


def test_schema_does_not_ask_llm_for_source_metadata() -> None:
    schema = json.loads(
        Path(
            "prompts/schemas/chunk_knowledge_v1.json"
        ).read_text(
            encoding="utf-8"
        )
    )

    properties = schema["properties"]

    assert "chunk_index" not in properties
    assert "start" not in properties
    assert "end" not in properties


def test_operational_schema_requires_evidence() -> None:
    schema = json.loads(
        Path(
            "prompts/schemas/chunk_knowledge_v1.json"
        ).read_text(
            encoding="utf-8"
        )
    )

    for field_name in (
        "topics",
        "decisions",
        "action_items",
        "risks",
        "pending_items",
    ):
        evidence_schema = (
            schema["properties"]
            [field_name]
            ["items"]
            ["properties"]
            ["evidence"]
        )

        assert evidence_schema["minItems"] == 1
