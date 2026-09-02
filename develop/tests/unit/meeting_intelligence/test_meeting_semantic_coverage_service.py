import json

import pytest

from models.chunk_classification import (
    ChunkKnowledgeKind,
)
from models.chunk_knowledge import ChunkKnowledge
from models.meeting_knowledge import MeetingKnowledge
from models.meeting_report import (
    ActionItem,
    Decision,
    EvidenceReference,
    MeetingRisk,
    MeetingTopic,
    PendingItem,
)
from models.meeting_semantic_consolidation import (
    ConsolidatedMeetingKnowledgeItem,
    MeetingKnowledgeItemReference,
    MeetingSemanticConsolidation,
)
from services.meeting_semantic_consolidation_parser import (
    CrossItemSourceReferenceReuseError,
    MeetingSemanticConsolidationParser,
)
from services.meeting_semantic_coverage_service import (
    MeetingSemanticCoverageService,
)


def evidence(
    text: str,
    start: float,
) -> list[EvidenceReference]:
    return [
        EvidenceReference(
            speaker="LOCAL",
            start=start,
            end=(
                start + 1.0
            ),
            excerpt=text,
        )
    ]


def reference(
    chunk_index: int,
    item_index: int,
) -> MeetingKnowledgeItemReference:
    return MeetingKnowledgeItemReference(
        chunk_index=chunk_index,
        item_index=item_index,
    )


def build_real_cat_005_topology() -> MeetingKnowledge:
    return MeetingKnowledge(
        source_chunk_count=4,
        chunks=[
            ChunkKnowledge(
                chunk_index=0,
                start=0.0,
                end=10.0,
                topics=[
                    MeetingTopic(
                        title="Arquitectura",
                        summary=(
                            "Se revisó la arquitectura actual."
                        ),
                        evidence=evidence(
                            "Arquitectura actual.",
                            1.0,
                        ),
                    )
                ],
                decisions=[
                    Decision(
                        description=(
                            "Se aprobó iniciar la migración."
                        ),
                        evidence=evidence(
                            "Iniciar la migración.",
                            2.0,
                        ),
                    )
                ],
                risks=[
                    MeetingRisk(
                        description=(
                            "Existe riesgo de indisponibilidad."
                        ),
                        evidence=evidence(
                            "Riesgo de indisponibilidad.",
                            3.0,
                        ),
                    )
                ],
            ),
            ChunkKnowledge(
                chunk_index=1,
                start=10.0,
                end=20.0,
                decisions=[
                    Decision(
                        description=(
                            "Se aprobó la ventana técnica."
                        ),
                        evidence=evidence(
                            "Ventana técnica aprobada.",
                            11.0,
                        ),
                    )
                ],
            ),
            ChunkKnowledge(
                chunk_index=2,
                start=20.0,
                end=30.0,
                decisions=[
                    Decision(
                        description=(
                            "Se acordó validar la recuperación."
                        ),
                        evidence=evidence(
                            "Validar la recuperación.",
                            21.0,
                        ),
                    )
                ],
                risks=[
                    MeetingRisk(
                        description=(
                            "Existe riesgo de recuperación lenta."
                        ),
                        evidence=evidence(
                            "Recuperación lenta.",
                            22.0,
                        ),
                    )
                ],
            ),
            ChunkKnowledge(
                chunk_index=3,
                start=30.0,
                end=40.0,
                risks=[
                    MeetingRisk(
                        description=(
                            "Existe riesgo de cierre tardío."
                        ),
                        evidence=evidence(
                            "Cierre tardío.",
                            31.0,
                        ),
                    )
                ],
            ),
        ],
    )


def partial_cat_005_payload() -> dict:
    return {
        "items": [
            {
                "kind": "topic",
                "description": (
                    "Arquitectura vigente de la plataforma."
                ),
                "source_refs": [
                    {
                        "chunk_index": 0,
                        "item_index": 0,
                    }
                ],
            },
            {
                "kind": "decision",
                "description": (
                    "Se autorizó comenzar la migración."
                ),
                "source_refs": [
                    {
                        "chunk_index": 0,
                        "item_index": 0,
                    }
                ],
            },
            {
                "kind": "risk",
                "description": (
                    "La migración puede causar indisponibilidad."
                ),
                "source_refs": [
                    {
                        "chunk_index": 0,
                        "item_index": 0,
                    }
                ],
            },
            {
                "kind": "decision",
                "description": (
                    "Se confirmó la ventana técnica."
                ),
                "source_refs": [
                    {
                        "chunk_index": 1,
                        "item_index": 0,
                    }
                ],
            },
            {
                "kind": "decision",
                "description": (
                    "Se validará el procedimiento de recuperación."
                ),
                "source_refs": [
                    {
                        "chunk_index": 2,
                        "item_index": 0,
                    }
                ],
            },
            {
                "kind": "risk",
                "description": (
                    "La recuperación puede exceder la ventana."
                ),
                "source_refs": [
                    {
                        "chunk_index": 2,
                        "item_index": 0,
                    }
                ],
            },
        ]
    }


def complete_cat_005_payload() -> dict:
    payload = partial_cat_005_payload()

    payload["items"].append(
        {
            "kind": "risk",
            "description": (
                "El cierre puede completarse tarde."
            ),
            "source_refs": [
                {
                    "chunk_index": 3,
                    "item_index": 0,
                }
            ],
        }
    )

    return payload


def source_keys(
    consolidation: MeetingSemanticConsolidation,
) -> list[tuple[str, int, int]]:
    return [
        (
            item.kind.value,
            source_ref.chunk_index,
            source_ref.item_index,
        )
        for item in consolidation.items
        for source_ref in item.source_refs
    ]


def single_topic_consolidation() -> MeetingSemanticConsolidation:
    return MeetingSemanticConsolidation(
        items=[
            ConsolidatedMeetingKnowledgeItem(
                kind=ChunkKnowledgeKind.TOPIC,
                description=(
                    "Arquitectura consolidada."
                ),
                source_refs=[
                    reference(
                        0,
                        0,
                    )
                ],
            )
        ]
    )


def test_reconciles_real_cat_005_missing_risk() -> None:
    knowledge = build_real_cat_005_topology()

    parsed = (
        MeetingSemanticConsolidationParser()
        .parse(
            response=json.dumps(
                partial_cat_005_payload(),
                ensure_ascii=False,
            ),
            meeting_knowledge=knowledge,
        )
    )

    original = parsed.as_dict()
    llm_items = list(
        parsed.items
    )

    assert len(parsed.items) == 6

    result = (
        MeetingSemanticCoverageService()
        .reconcile(
            semantic_consolidation=parsed,
            meeting_knowledge=knowledge,
        )
    )

    expected_keys = {
        ("topic", 0, 0),
        ("decision", 0, 0),
        ("risk", 0, 0),
        ("decision", 1, 0),
        ("decision", 2, 0),
        ("risk", 2, 0),
        ("risk", 3, 0),
    }

    actual_keys = source_keys(
        result
    )

    assert len(result.items) == 7
    assert len(actual_keys) == 7
    assert set(actual_keys) == expected_keys

    assert all(
        result.items[index]
        is llm_item
        for index, llm_item in enumerate(
            llm_items
        )
    )

    recovered = result.items[-1]

    assert recovered.kind is ChunkKnowledgeKind.RISK
    assert (
        recovered.description
        == "Existe riesgo de cierre tardío."
    )
    assert recovered.source_refs == [
        reference(
            3,
            0,
        )
    ]

    assert parsed.as_dict() == original


def test_real_cat_005_reused_risk_requires_identity_fallback() -> None:
    knowledge = build_real_cat_005_topology()
    payload = complete_cat_005_payload()
    payload["items"].append(
        {
            "kind": "risk",
            "description": (
                "Riesgo de cierre duplicado ambiguamente."
            ),
            "source_refs": [
                {
                    "chunk_index": 3,
                    "item_index": 0,
                }
            ],
        }
    )

    with pytest.raises(
        CrossItemSourceReferenceReuseError,
    ) as error:
        (
            MeetingSemanticConsolidationParser()
            .parse(
                response=json.dumps(
                    payload,
                    ensure_ascii=False,
                ),
                meeting_knowledge=knowledge,
            )
        )

    assert error.value.reused_source_keys == (
        (
            "risk",
            3,
            0,
        ),
    )

    identity = (
        MeetingSemanticCoverageService()
        .build_identity_consolidation(
            knowledge
        )
    )

    assert source_keys(identity).count(
        (
            "risk",
            3,
            0,
        )
    ) == 1
    assert len(source_keys(identity)) == len(
        set(source_keys(identity))
    ) == 7


def test_preserves_complete_consolidation_unchanged() -> None:
    knowledge = build_real_cat_005_topology()

    complete = (
        MeetingSemanticConsolidationParser()
        .parse(
            response=json.dumps(
                complete_cat_005_payload(),
                ensure_ascii=False,
            ),
            meeting_knowledge=knowledge,
        )
    )

    original = complete.as_dict()

    result = (
        MeetingSemanticCoverageService()
        .reconcile(
            semantic_consolidation=complete,
            meeting_knowledge=knowledge,
        )
    )

    assert result is complete
    assert result.as_dict() == original


def test_reconciliation_is_idempotent() -> None:
    knowledge = build_real_cat_005_topology()
    service = MeetingSemanticCoverageService()

    partial = (
        MeetingSemanticConsolidationParser()
        .parse(
            response=json.dumps(
                partial_cat_005_payload(),
                ensure_ascii=False,
            ),
            meeting_knowledge=knowledge,
        )
    )

    first_result = service.reconcile(
        semantic_consolidation=partial,
        meeting_knowledge=knowledge,
    )

    second_result = service.reconcile(
        semantic_consolidation=first_result,
        meeting_knowledge=knowledge,
    )

    assert second_result is first_result
    assert (
        second_result.as_dict()
        == first_result.as_dict()
    )


def test_appends_multiple_missing_refs_in_canonical_order() -> None:
    source_evidence = evidence(
        "Conocimiento fuente.",
        1.0,
    )

    knowledge = MeetingKnowledge(
        source_chunk_count=1,
        chunks=[
            ChunkKnowledge(
                chunk_index=0,
                start=0.0,
                end=10.0,
                topics=[
                    MeetingTopic(
                        title="Arquitectura",
                        summary="Capacidad actual.",
                        evidence=source_evidence,
                    )
                ],
                decisions=[
                    Decision(
                        description="Migrar la plataforma.",
                        evidence=source_evidence,
                    )
                ],
                action_items=[
                    ActionItem(
                        description="Preparar el plan.",
                        evidence=source_evidence,
                    )
                ],
                risks=[
                    MeetingRisk(
                        description="Interrupción del servicio.",
                        evidence=source_evidence,
                    )
                ],
                pending_items=[
                    PendingItem(
                        description="Confirmar la ventana.",
                        evidence=source_evidence,
                    )
                ],
            )
        ],
    )

    result = (
        MeetingSemanticCoverageService()
        .reconcile(
            semantic_consolidation=(
                MeetingSemanticConsolidation()
            ),
            meeting_knowledge=knowledge,
        )
    )

    assert [
        item.kind
        for item in result.items
    ] == [
        ChunkKnowledgeKind.TOPIC,
        ChunkKnowledgeKind.DECISION,
        ChunkKnowledgeKind.ACTION,
        ChunkKnowledgeKind.RISK,
        ChunkKnowledgeKind.PENDING,
    ]

    assert source_keys(result) == [
        ("topic", 0, 0),
        ("decision", 0, 0),
        ("action", 0, 0),
        ("risk", 0, 0),
        ("pending", 0, 0),
    ]

    assert [
        item.description
        for item in result.items
    ] == [
        "Arquitectura. Capacidad actual.",
        "Migrar la plataforma.",
        "Preparar el plan.",
        "Interrupción del servicio.",
        "Confirmar la ventana.",
    ]


def test_identity_consolidation_uses_canonical_catalog() -> None:
    knowledge = build_real_cat_005_topology()

    result = (
        MeetingSemanticCoverageService()
        .build_identity_consolidation(
            knowledge
        )
    )

    assert source_keys(result) == [
        ("topic", 0, 0),
        ("decision", 0, 0),
        ("risk", 0, 0),
        ("decision", 1, 0),
        ("decision", 2, 0),
        ("risk", 2, 0),
        ("risk", 3, 0),
    ]

    assert [
        item.description
        for item in result.items
    ] == [
        "Arquitectura. Se revisó la arquitectura actual.",
        "Se aprobó iniciar la migración.",
        "Existe riesgo de indisponibilidad.",
        "Se aprobó la ventana técnica.",
        "Se acordó validar la recuperación.",
        "Existe riesgo de recuperación lenta.",
        "Existe riesgo de cierre tardío.",
    ]

    assert all(
        len(item.source_refs) == 1
        for item in result.items
    )
    assert len(source_keys(result)) == len(
        set(source_keys(result))
    ) == 7


def test_identity_consolidation_is_deterministic_and_idempotent() -> None:
    knowledge = build_real_cat_005_topology()
    service = MeetingSemanticCoverageService()

    first_result = (
        service.build_identity_consolidation(
            knowledge
        )
    )
    second_result = (
        service.build_identity_consolidation(
            knowledge
        )
    )

    assert first_result is not second_result
    assert (
        first_result.as_dict()
        == second_result.as_dict()
    )

    reconciled = service.reconcile(
        semantic_consolidation=first_result,
        meeting_knowledge=knowledge,
    )

    assert reconciled is first_result


def test_uses_canonical_topic_text_when_title_equals_summary() -> None:
    knowledge = MeetingKnowledge(
        source_chunk_count=1,
        chunks=[
            ChunkKnowledge(
                chunk_index=0,
                start=0.0,
                end=10.0,
                topics=[
                    MeetingTopic(
                        title="Arquitectura",
                        summary="Arquitectura",
                        evidence=evidence(
                            "Arquitectura.",
                            1.0,
                        ),
                    )
                ],
            )
        ],
    )

    result = (
        MeetingSemanticCoverageService()
        .reconcile(
            semantic_consolidation=(
                MeetingSemanticConsolidation()
            ),
            meeting_knowledge=knowledge,
        )
    )

    assert len(result.items) == 1
    assert (
        result.items[0].description
        == "Arquitectura"
    )


def test_rejects_wrong_kind_reference_instead_of_repairing() -> None:
    consolidation = MeetingSemanticConsolidation(
        items=[
            ConsolidatedMeetingKnowledgeItem(
                kind=ChunkKnowledgeKind.ACTION,
                description=(
                    "Referencia con categoría alterada."
                ),
                source_refs=[
                    reference(
                        0,
                        0,
                    )
                ],
            )
        ]
    )

    with pytest.raises(
        ValueError,
        match="referencias fuente inválidas",
    ):
        (
            MeetingSemanticCoverageService()
            .reconcile(
                semantic_consolidation=(
                    consolidation
                ),
                meeting_knowledge=(
                    build_real_cat_005_topology()
                ),
            )
        )


@pytest.mark.parametrize(
    (
        "chunk_index",
        "item_index",
    ),
    [
        (
            99,
            0,
        ),
        (
            0,
            99,
        ),
    ],
)
def test_rejects_invented_reference_instead_of_repairing(
    chunk_index: int,
    item_index: int,
) -> None:
    consolidation = MeetingSemanticConsolidation(
        items=[
            ConsolidatedMeetingKnowledgeItem(
                kind=ChunkKnowledgeKind.TOPIC,
                description=(
                    "Referencia inventada."
                ),
                source_refs=[
                    reference(
                        chunk_index,
                        item_index,
                    )
                ],
            )
        ]
    )

    with pytest.raises(
        ValueError,
        match="referencias fuente inválidas",
    ):
        (
            MeetingSemanticCoverageService()
            .reconcile(
                semantic_consolidation=(
                    consolidation
                ),
                meeting_knowledge=(
                    build_real_cat_005_topology()
                ),
            )
        )


def test_rejects_duplicate_reference_instead_of_repairing() -> None:
    consolidation = single_topic_consolidation()

    consolidation.items[0].source_refs.append(
        reference(
            0,
            0,
        )
    )

    with pytest.raises(
        ValueError,
        match="duplicada o reutilizada",
    ):
        (
            MeetingSemanticCoverageService()
            .reconcile(
                semantic_consolidation=(
                    consolidation
                ),
                meeting_knowledge=(
                    build_real_cat_005_topology()
                ),
            )
        )


def test_rejects_reused_reference_instead_of_repairing() -> None:
    consolidation = single_topic_consolidation()

    consolidation.items.append(
        ConsolidatedMeetingKnowledgeItem(
            kind=ChunkKnowledgeKind.TOPIC,
            description=(
                "Segunda consolidación inválida."
            ),
            source_refs=[
                reference(
                    0,
                    0,
                )
            ],
        )
    )

    with pytest.raises(
        ValueError,
        match="duplicada o reutilizada",
    ):
        (
            MeetingSemanticCoverageService()
            .reconcile(
                semantic_consolidation=(
                    consolidation
                ),
                meeting_knowledge=(
                    build_real_cat_005_topology()
                ),
            )
        )


@pytest.mark.parametrize(
    (
        "semantic_consolidation",
        "meeting_knowledge",
        "message",
    ),
    [
        (
            object(),
            build_real_cat_005_topology(),
            "MeetingSemanticConsolidation",
        ),
        (
            MeetingSemanticConsolidation(),
            object(),
            "MeetingKnowledge",
        ),
    ],
)
def test_rejects_invalid_input_types(
    semantic_consolidation,
    meeting_knowledge,
    message: str,
) -> None:
    with pytest.raises(
        TypeError,
        match=message,
    ):
        (
            MeetingSemanticCoverageService()
            .reconcile(
                semantic_consolidation=(
                    semantic_consolidation
                ),
                meeting_knowledge=(
                    meeting_knowledge
                ),
            )
        )


def test_identity_consolidation_rejects_invalid_input_type() -> None:
    with pytest.raises(
        TypeError,
        match="MeetingKnowledge",
    ):
        (
            MeetingSemanticCoverageService()
            .build_identity_consolidation(
                object()
            )
        )
