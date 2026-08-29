import json
from datetime import date

import pytest

from models.chunk_classification import (
    ChunkKnowledgeKind,
)
from models.chunk_knowledge import ChunkKnowledge
from models.meeting_knowledge import MeetingKnowledge
from models.meeting_report import (
    ActionItem,
    ActionStatus,
    Decision,
    EvidenceReference,
    MeetingRisk,
    MeetingTopic,
    PendingItem,
)
from models.meeting_semantic_consolidation import (
    MeetingSemanticConsolidation,
)
from services.meeting_semantic_consolidation_parser import (
    MeetingSemanticConsolidationParser,
)


def evidence(
    text: str,
    start: float,
    end: float,
) -> list[EvidenceReference]:
    return [
        EvidenceReference(
            speaker="LOCAL",
            start=start,
            end=end,
            excerpt=text,
        )
    ]


def build_meeting_knowledge() -> MeetingKnowledge:
    return MeetingKnowledge(
        source_chunk_count=2,
        chunks=[
            ChunkKnowledge(
                chunk_index=0,
                start=0.0,
                end=20.0,
                topics=[
                    MeetingTopic(
                        title="Arquitectura",
                        summary=(
                            "Se revisó la arquitectura."
                        ),
                        evidence=evidence(
                            "Se revisó la arquitectura.",
                            0.0,
                            4.0,
                        ),
                    ),
                ],
                decisions=[
                    Decision(
                        description=(
                            "Se aprobó migrar."
                        ),
                        evidence=evidence(
                            "Se aprobó migrar.",
                            4.0,
                            8.0,
                        ),
                    ),
                ],
                action_items=[
                    ActionItem(
                        description=(
                            "María preparará el plan."
                        ),
                        owner="María",
                        due_date=date(
                            2026,
                            8,
                            30,
                        ),
                        status=(
                            ActionStatus.PENDING
                        ),
                        evidence=evidence(
                            "María preparará el plan.",
                            8.0,
                            12.0,
                        ),
                    ),
                ],
            ),
            ChunkKnowledge(
                chunk_index=1,
                start=20.0,
                end=40.0,
                risks=[
                    MeetingRisk(
                        description=(
                            "Existe riesgo de interrupción."
                        ),
                        evidence=evidence(
                            "Existe riesgo de interrupción.",
                            20.0,
                            24.0,
                        ),
                    ),
                ],
                pending_items=[
                    PendingItem(
                        description=(
                            "Confirmar la ventana."
                        ),
                        evidence=evidence(
                            "Confirmar la ventana.",
                            24.0,
                            28.0,
                        ),
                    ),
                ],
            ),
        ],
    )


def valid_payload() -> dict:
    return {
        "items": [
            {
                "kind": "topic",
                "description": (
                    "Arquitectura actual."
                ),
                "source_refs": [
                    {
                        "chunk_index": 0,
                        "item_index": 0,
                    },
                ],
            },
            {
                "kind": "decision",
                "description": (
                    "Se aprobó migrar."
                ),
                "source_refs": [
                    {
                        "chunk_index": 0,
                        "item_index": 0,
                    },
                ],
            },
            {
                "kind": "action",
                "description": (
                    "María preparará el plan."
                ),
                "source_refs": [
                    {
                        "chunk_index": 0,
                        "item_index": 0,
                    },
                ],
            },
            {
                "kind": "risk",
                "description": (
                    "Existe riesgo de interrupción."
                ),
                "source_refs": [
                    {
                        "chunk_index": 1,
                        "item_index": 0,
                    },
                ],
            },
            {
                "kind": "pending",
                "description": (
                    "Confirmar la ventana."
                ),
                "source_refs": [
                    {
                        "chunk_index": 1,
                        "item_index": 0,
                    },
                ],
            },
        ],
    }


def parse_payload(
    payload: dict,
):
    return (
        MeetingSemanticConsolidationParser()
        .parse(
            response=json.dumps(
                payload,
                ensure_ascii=False,
            ),
            meeting_knowledge=(
                build_meeting_knowledge()
            ),
        )
    )


def test_parser_returns_semantic_consolidation() -> None:
    result = parse_payload(
        valid_payload()
    )

    assert isinstance(
        result,
        MeetingSemanticConsolidation,
    )
    assert result.has_content
    assert len(result.items) == 5


def test_parser_preserves_kind_and_source_refs() -> None:
    result = parse_payload(
        valid_payload()
    )

    action = result.items_of_kind(
        ChunkKnowledgeKind.ACTION
    )[0]

    assert (
        action.description
        == "María preparará el plan."
    )
    assert len(
        action.source_refs
    ) == 1
    assert (
        action.source_refs[0].chunk_index
        == 0
    )
    assert (
        action.source_refs[0].item_index
        == 0
    )


def test_parser_accepts_wrapped_json_text() -> None:
    response = (
        "Resultado:\n"
        + json.dumps(
            valid_payload(),
            ensure_ascii=False,
        )
        + "\nFin."
    )

    result = (
        MeetingSemanticConsolidationParser()
        .parse(
            response=response,
            meeting_knowledge=(
                build_meeting_knowledge()
            ),
        )
    )

    assert len(result.items) == 5


def test_parser_rejects_invalid_meeting_knowledge() -> None:
    with pytest.raises(
        TypeError,
        match="instancia de MeetingKnowledge",
    ):
        (
            MeetingSemanticConsolidationParser()
            .parse(
                response='{"items":[]}',
                meeting_knowledge=object(),
            )
        )


def test_parser_rejects_extra_root_field() -> None:
    payload = valid_payload()
    payload["title"] = "No permitido"

    with pytest.raises(
        ValueError,
        match="campos no soportados",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_extra_item_field() -> None:
    payload = valid_payload()
    payload["items"][0][
        "evidence"
    ] = []

    with pytest.raises(
        ValueError,
        match="campos no soportados",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_extra_reference_field() -> None:
    payload = valid_payload()
    payload["items"][0][
        "source_refs"
    ][0]["kind"] = "topic"

    with pytest.raises(
        ValueError,
        match="campos no soportados",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_unknown_kind() -> None:
    payload = valid_payload()
    payload["items"][0][
        "kind"
    ] = "conclusion"

    with pytest.raises(
        ValueError,
        match="kind no contiene un valor válido",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_empty_description() -> None:
    payload = valid_payload()
    payload["items"][0][
        "description"
    ] = "   "

    with pytest.raises(
        ValueError,
        match="description no puede estar vacío",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_non_integer_reference() -> None:
    payload = valid_payload()
    payload["items"][0][
        "source_refs"
    ][0]["chunk_index"] = 1.5

    with pytest.raises(
        TypeError,
        match="chunk_index debe ser entero",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_missing_chunk() -> None:
    payload = valid_payload()
    payload["items"][0][
        "source_refs"
    ][0]["chunk_index"] = 8

    with pytest.raises(
        ValueError,
        match="chunk inexistente",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_missing_item_for_kind() -> None:
    payload = valid_payload()
    payload["items"][0][
        "source_refs"
    ][0]["item_index"] = 7

    with pytest.raises(
        ValueError,
        match="item fuente inexistente",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_duplicate_reference_within_item() -> None:
    payload = valid_payload()
    payload["items"][0][
        "source_refs"
    ].append(
        {
            "chunk_index": 0,
            "item_index": 0,
        }
    )

    with pytest.raises(
        ValueError,
        match="referencias duplicadas",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_reused_reference_across_items() -> None:
    payload = valid_payload()
    payload["items"].append(
        {
            "kind": "decision",
            "description": (
                "Decisión duplicada."
            ),
            "source_refs": [
                {
                    "chunk_index": 0,
                    "item_index": 0,
                },
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match="reutilizar un item fuente",
    ):
        parse_payload(
            payload
        )


def test_parser_rejects_omitted_source_item() -> None:
    payload = valid_payload()
    payload["items"] = [
        item
        for item in payload["items"]
        if item["kind"] != "topic"
    ]

    with pytest.raises(
        ValueError,
        match="omitió items fuente obligatorios",
    ):
        parse_payload(
            payload
        )


def test_parser_allows_real_same_kind_merge() -> None:
    knowledge = (
        build_meeting_knowledge()
    )

    second_decision = Decision(
        description=(
            "Se confirmó la migración."
        ),
        evidence=evidence(
            "Se confirmó la migración.",
            12.0,
            16.0,
        ),
    )

    knowledge.chunks[0].decisions.append(
        second_decision
    )

    payload = valid_payload()

    decision = next(
        item
        for item in payload["items"]
        if item["kind"] == "decision"
    )

    decision["description"] = (
        "Se aprobó y confirmó la migración."
    )
    decision["source_refs"].append(
        {
            "chunk_index": 0,
            "item_index": 1,
        }
    )

    result = (
        MeetingSemanticConsolidationParser()
        .parse(
            response=json.dumps(
                payload,
                ensure_ascii=False,
            ),
            meeting_knowledge=knowledge,
        )
    )

    decisions = result.items_of_kind(
        ChunkKnowledgeKind.DECISION
    )

    assert len(decisions) == 1
    assert len(
        decisions[0].source_refs
    ) == 2


def test_parser_accepts_empty_catalog_with_empty_items() -> None:
    knowledge = MeetingKnowledge(
        source_chunk_count=1,
        chunks=[
            ChunkKnowledge(
                chunk_index=0,
                start=0.0,
                end=10.0,
                key_points=[
                    "Contenido legacy."
                ],
            ),
        ],
    )

    result = (
        MeetingSemanticConsolidationParser()
        .parse(
            response='{"items":[]}',
            meeting_knowledge=knowledge,
        )
    )

    assert not result.has_content


def test_parser_propagates_json_decode_error() -> None:
    with pytest.raises(
        ValueError,
        match="JSON válido",
    ):
        (
            MeetingSemanticConsolidationParser()
            .parse(
                response="{invalid}",
                meeting_knowledge=(
                    build_meeting_knowledge()
                ),
            )
        )


def test_parser_does_not_mutate_meeting_knowledge() -> None:
    knowledge = (
        build_meeting_knowledge()
    )
    original = knowledge.as_dict()

    (
        MeetingSemanticConsolidationParser()
        .parse(
            response=json.dumps(
                valid_payload(),
                ensure_ascii=False,
            ),
            meeting_knowledge=knowledge,
        )
    )

    assert (
        knowledge.as_dict()
        == original
    )
