from datetime import date

import pytest

from models.artifacts.meeting_report import (
    MeetingReport,
)
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
from models.meeting_report_narrative import (
    GroundedNarrativeText,
    MeetingReportNarrative,
)
from models.meeting_semantic_consolidation import (
    ConsolidatedMeetingKnowledgeItem,
    MeetingKnowledgeItemReference,
    MeetingSemanticConsolidation,
)
from services.meeting_report_staged_assembler import (
    MeetingReportStagedAssembler,
)


def evidence(
    speaker: str,
    start: float,
    end: float,
    excerpt: str,
) -> EvidenceReference:
    return EvidenceReference(
        speaker=speaker,
        start=start,
        end=end,
        excerpt=excerpt,
    )


def ref(
    chunk_index: int,
    item_index: int,
) -> MeetingKnowledgeItemReference:
    return MeetingKnowledgeItemReference(
        chunk_index=chunk_index,
        item_index=item_index,
    )


def grounded(
    text: str,
    source_item_ids: list[int],
) -> GroundedNarrativeText:
    return GroundedNarrativeText(
        text=text,
        source_item_ids=source_item_ids,
    )


def build_meeting_knowledge() -> MeetingKnowledge:
    topic_text = (
        "Se revisó la arquitectura actual."
    )
    decision_text = (
        "Se aprobó migrar la plataforma."
    )
    action_text = (
        "María preparará el plan."
    )
    risk_text = (
        "Existe riesgo de interrupción."
    )
    pending_text = (
        "Confirmar la ventana de mantenimiento."
    )

    return MeetingKnowledge(
        source_chunk_count=2,
        chunks=[
            ChunkKnowledge(
                chunk_index=0,
                start=0.0,
                end=20.0,
                topics=[
                    MeetingTopic(
                        title=topic_text,
                        summary=topic_text,
                        evidence=[
                            evidence(
                                "LOCAL",
                                0.0,
                                4.0,
                                topic_text,
                            )
                        ],
                    ),
                ],
                decisions=[
                    Decision(
                        description=decision_text,
                        evidence=[
                            evidence(
                                "LOCAL",
                                4.0,
                                8.0,
                                decision_text,
                            )
                        ],
                    ),
                ],
                action_items=[
                    ActionItem(
                        description=action_text,
                        owner="María",
                        due_date=date(
                            2026,
                            8,
                            30,
                        ),
                        status=(
                            ActionStatus.PENDING
                        ),
                        evidence=[
                            evidence(
                                "REMOTE",
                                8.0,
                                12.0,
                                action_text,
                            )
                        ],
                    ),
                ],
            ),
            ChunkKnowledge(
                chunk_index=1,
                start=20.0,
                end=40.0,
                risks=[
                    MeetingRisk(
                        description=risk_text,
                        evidence=[
                            evidence(
                                "LOCAL",
                                20.0,
                                24.0,
                                risk_text,
                            )
                        ],
                    ),
                ],
                pending_items=[
                    PendingItem(
                        description=pending_text,
                        evidence=[
                            evidence(
                                "REMOTE",
                                24.0,
                                28.0,
                                pending_text,
                            )
                        ],
                    ),
                ],
            ),
        ],
    )


def build_semantic_consolidation() -> MeetingSemanticConsolidation:
    return MeetingSemanticConsolidation(
        items=[
            ConsolidatedMeetingKnowledgeItem(
                kind=ChunkKnowledgeKind.TOPIC,
                description=(
                    "Arquitectura actual."
                ),
                source_refs=[
                    ref(
                        0,
                        0,
                    )
                ],
            ),
            ConsolidatedMeetingKnowledgeItem(
                kind=ChunkKnowledgeKind.DECISION,
                description=(
                    "Se aprobó migrar la plataforma."
                ),
                source_refs=[
                    ref(
                        0,
                        0,
                    )
                ],
            ),
            ConsolidatedMeetingKnowledgeItem(
                kind=ChunkKnowledgeKind.ACTION,
                description=(
                    "María preparará el plan."
                ),
                source_refs=[
                    ref(
                        0,
                        0,
                    )
                ],
            ),
            ConsolidatedMeetingKnowledgeItem(
                kind=ChunkKnowledgeKind.RISK,
                description=(
                    "Existe riesgo de interrupción."
                ),
                source_refs=[
                    ref(
                        1,
                        0,
                    )
                ],
            ),
            ConsolidatedMeetingKnowledgeItem(
                kind=ChunkKnowledgeKind.PENDING,
                description=(
                    "Confirmar la ventana de mantenimiento."
                ),
                source_refs=[
                    ref(
                        1,
                        0,
                    )
                ],
            ),
        ]
    )


def build_narrative(
    item_count: int = 5,
) -> MeetingReportNarrative:
    return MeetingReportNarrative(
        title=grounded(
            "Migración y arquitectura de plataforma",
            [
                0,
                1,
            ],
        ),
        objective=None,
        executive_summary=grounded(
            (
                "Se revisó la arquitectura, se aprobó la "
                "migración y se definieron acciones, riesgos "
                "y asuntos pendientes."
            ),
            list(
                range(
                    item_count
                )
            ),
        ),
        key_points=[
            grounded(
                "Se aprobó migrar la plataforma.",
                [
                    1
                ],
            ),
            grounded(
                "María preparará el plan.",
                [
                    2
                ],
            ),
        ],
    )


def build_assembler() -> MeetingReportStagedAssembler:
    return MeetingReportStagedAssembler()


def assemble_default() -> MeetingReport:
    return build_assembler().assemble(
        meeting_knowledge=(
            build_meeting_knowledge()
        ),
        semantic_consolidation=(
            build_semantic_consolidation()
        ),
        narrative=(
            build_narrative()
        ),
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version=(
            "meeting_report_global_staged_v1"
        ),
    )


def test_assembler_returns_meeting_report() -> None:
    result = assemble_default()

    assert isinstance(
        result,
        MeetingReport,
    )


def test_assembler_uses_artifact_metadata() -> None:
    result = build_assembler().assemble(
        meeting_knowledge=(
            build_meeting_knowledge()
        ),
        semantic_consolidation=(
            build_semantic_consolidation()
        ),
        narrative=(
            build_narrative()
        ),
        provider="  ollama  ",
        model="  qwen2.5:3b  ",
        prompt_version=(
            "  meeting_report_global_staged_v1  "
        ),
    )

    assert result.provider == "ollama"
    assert result.model == "qwen2.5:3b"
    assert (
        result.prompt_version
        == "meeting_report_global_staged_v1"
    )


def test_assembler_uses_narrative_text_only() -> None:
    narrative = build_narrative()
    narrative.objective = grounded(
        "Revisar la arquitectura actual.",
        [
            0
        ],
    )

    result = build_assembler().assemble(
        meeting_knowledge=(
            build_meeting_knowledge()
        ),
        semantic_consolidation=(
            build_semantic_consolidation()
        ),
        narrative=narrative,
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="v1",
    )

    assert (
        result.title
        == "Migración y arquitectura de plataforma"
    )
    assert (
        result.objective
        == "Revisar la arquitectura actual."
    )
    assert (
        result.executive_summary
        == narrative.executive_summary.text
    )
    assert result.key_points == [
        "Se aprobó migrar la plataforma.",
        "María preparará el plan.",
    ]


def test_assembler_preserves_null_objective() -> None:
    result = assemble_default()

    assert result.objective is None


def test_assembler_maps_all_semantic_kinds() -> None:
    result = assemble_default()

    assert len(result.topics) == 1
    assert len(result.decisions) == 1
    assert len(result.action_items) == 1
    assert len(result.risks) == 1
    assert len(result.pending_items) == 1

    assert (
        result.topics[0].title
        == "Arquitectura actual."
    )
    assert (
        result.topics[0].summary
        == "Arquitectura actual."
    )
    assert (
        result.decisions[0].description
        == "Se aprobó migrar la plataforma."
    )
    assert (
        result.risks[0].description
        == "Existe riesgo de interrupción."
    )


def test_assembler_reconstructs_exact_evidence() -> None:
    knowledge = (
        build_meeting_knowledge()
    )

    result = build_assembler().assemble(
        meeting_knowledge=knowledge,
        semantic_consolidation=(
            build_semantic_consolidation()
        ),
        narrative=(
            build_narrative()
        ),
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="v1",
    )

    source = (
        knowledge.chunks[
            0
        ].decisions[
            0
        ].evidence[
            0
        ]
    )

    final = (
        result.decisions[
            0
        ].evidence[
            0
        ]
    )

    assert final is source
    assert (
        final.as_dict()
        == source.as_dict()
    )


def test_assembler_reconstructs_action_metadata() -> None:
    result = assemble_default()

    action = (
        result.action_items[
            0
        ]
    )

    assert action.owner is not None
    assert (
        action.owner.display_name
        == "María"
    )
    assert (
        action.due_date
        == date(
            2026,
            8,
            30,
        )
    )
    assert (
        action.status
        is ActionStatus.PENDING
    )


def test_assembler_leaves_unsupported_legacy_sections_empty() -> None:
    result = assemble_default()

    assert result.participants == []
    assert result.conclusions == []


def test_assembler_merges_same_kind_evidence_in_source_order() -> None:
    knowledge = (
        build_meeting_knowledge()
    )

    first_text = (
        knowledge.chunks[
            0
        ].decisions[
            0
        ].description
    )

    second_text = (
        "Se confirmó el calendario de migración."
    )

    knowledge.chunks[
        1
    ].decisions.append(
        Decision(
            description=second_text,
            evidence=[
                evidence(
                    "REMOTE",
                    28.0,
                    32.0,
                    second_text,
                )
            ],
        )
    )

    consolidation = (
        build_semantic_consolidation()
    )

    decision = (
        consolidation.items[
            1
        ]
    )

    consolidation.items[
        1
    ] = (
        ConsolidatedMeetingKnowledgeItem(
            kind=ChunkKnowledgeKind.DECISION,
            description=(
                "Se aprobó y confirmó la migración."
            ),
            source_refs=[
                ref(
                    0,
                    0,
                ),
                ref(
                    1,
                    0,
                ),
            ],
        )
    )

    narrative = build_narrative()

    result = build_assembler().assemble(
        meeting_knowledge=knowledge,
        semantic_consolidation=consolidation,
        narrative=narrative,
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="v1",
    )

    final_evidence = (
        result.decisions[
            0
        ].evidence
    )

    assert [
        item.excerpt
        for item in final_evidence
    ] == [
        first_text,
        second_text,
    ]


def test_assembler_deduplicates_repeated_evidence() -> None:
    knowledge = (
        build_meeting_knowledge()
    )

    shared = (
        knowledge.chunks[
            0
        ].decisions[
            0
        ].evidence[
            0
        ]
    )

    knowledge.chunks[
        1
    ].decisions.append(
        Decision(
            description=(
                "Se confirmó la migración."
            ),
            evidence=[
                shared
            ],
        )
    )

    consolidation = (
        build_semantic_consolidation()
    )

    consolidation.items[
        1
    ] = (
        ConsolidatedMeetingKnowledgeItem(
            kind=ChunkKnowledgeKind.DECISION,
            description=(
                "Se aprobó y confirmó la migración."
            ),
            source_refs=[
                ref(
                    0,
                    0,
                ),
                ref(
                    1,
                    0,
                ),
            ],
        )
    )

    result = build_assembler().assemble(
        meeting_knowledge=knowledge,
        semantic_consolidation=consolidation,
        narrative=(
            build_narrative()
        ),
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="v1",
    )

    assert len(
        result.decisions[
            0
        ].evidence
    ) == 1


def build_two_action_sources(
    *,
    second_owner=None,
    second_due_date=None,
    second_status=ActionStatus.UNKNOWN,
):
    knowledge = (
        build_meeting_knowledge()
    )

    second_text = (
        "Preparar el plan detallado de migración."
    )

    knowledge.chunks[
        1
    ].action_items.append(
        ActionItem(
            description=second_text,
            owner=second_owner,
            due_date=second_due_date,
            status=second_status,
            evidence=[
                evidence(
                    "REMOTE",
                    32.0,
                    36.0,
                    second_text,
                )
            ],
        )
    )

    consolidation = (
        build_semantic_consolidation()
    )

    consolidation.items[
        2
    ] = (
        ConsolidatedMeetingKnowledgeItem(
            kind=ChunkKnowledgeKind.ACTION,
            description=(
                "María preparará el plan de migración."
            ),
            source_refs=[
                ref(
                    0,
                    0,
                ),
                ref(
                    1,
                    0,
                ),
            ],
        )
    )

    return (
        knowledge,
        consolidation,
    )


def test_assembler_accepts_unknown_action_metadata_when_compatible() -> None:
    (
        knowledge,
        consolidation,
    ) = build_two_action_sources()

    result = build_assembler().assemble(
        meeting_knowledge=knowledge,
        semantic_consolidation=consolidation,
        narrative=(
            build_narrative()
        ),
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="v1",
    )

    action = result.action_items[
        0
    ]

    assert action.owner is not None
    assert (
        action.owner.display_name
        == "María"
    )
    assert (
        action.due_date
        == date(
            2026,
            8,
            30,
        )
    )
    assert (
        action.status
        is ActionStatus.PENDING
    )


def test_assembler_rejects_conflicting_action_owners() -> None:
    (
        knowledge,
        consolidation,
    ) = build_two_action_sources(
        second_owner="Pedro",
    )

    with pytest.raises(
        ValueError,
        match="owners incompatibles",
    ):
        build_assembler().assemble(
            meeting_knowledge=knowledge,
            semantic_consolidation=consolidation,
            narrative=(
                build_narrative()
            ),
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="v1",
        )


def test_assembler_rejects_conflicting_action_due_dates() -> None:
    (
        knowledge,
        consolidation,
    ) = build_two_action_sources(
        second_due_date=date(
            2026,
            9,
            5,
        ),
    )

    with pytest.raises(
        ValueError,
        match="due_dates incompatibles",
    ):
        build_assembler().assemble(
            meeting_knowledge=knowledge,
            semantic_consolidation=consolidation,
            narrative=(
                build_narrative()
            ),
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="v1",
        )


def test_assembler_rejects_conflicting_action_statuses() -> None:
    (
        knowledge,
        consolidation,
    ) = build_two_action_sources(
        second_status=(
            ActionStatus.COMPLETED
        ),
    )

    with pytest.raises(
        ValueError,
        match="status incompatibles",
    ):
        build_assembler().assemble(
            meeting_knowledge=knowledge,
            semantic_consolidation=consolidation,
            narrative=(
                build_narrative()
            ),
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="v1",
        )


def test_assembler_rejects_missing_semantic_coverage() -> None:
    consolidation = (
        build_semantic_consolidation()
    )

    consolidation.items.pop()

    with pytest.raises(
        ValueError,
        match="cobertura semántica completa",
    ):
        build_assembler().assemble(
            meeting_knowledge=(
                build_meeting_knowledge()
            ),
            semantic_consolidation=consolidation,
            narrative=(
                build_narrative(
                    item_count=4
                )
            ),
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="v1",
        )


def test_assembler_rejects_out_of_range_source_chunk() -> None:
    consolidation = (
        build_semantic_consolidation()
    )

    consolidation.items[
        0
    ] = (
        ConsolidatedMeetingKnowledgeItem(
            kind=ChunkKnowledgeKind.TOPIC,
            description=(
                "Arquitectura actual."
            ),
            source_refs=[
                ref(
                    8,
                    0,
                )
            ],
        )
    )

    with pytest.raises(
        ValueError,
        match="chunk inexistente",
    ):
        build_assembler().assemble(
            meeting_knowledge=(
                build_meeting_knowledge()
            ),
            semantic_consolidation=consolidation,
            narrative=(
                build_narrative()
            ),
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="v1",
        )


def test_assembler_rejects_out_of_range_source_item() -> None:
    consolidation = (
        build_semantic_consolidation()
    )

    consolidation.items[
        0
    ] = (
        ConsolidatedMeetingKnowledgeItem(
            kind=ChunkKnowledgeKind.TOPIC,
            description=(
                "Arquitectura actual."
            ),
            source_refs=[
                ref(
                    0,
                    9,
                )
            ],
        )
    )

    with pytest.raises(
        ValueError,
        match="item fuente inexistente",
    ):
        build_assembler().assemble(
            meeting_knowledge=(
                build_meeting_knowledge()
            ),
            semantic_consolidation=consolidation,
            narrative=(
                build_narrative()
            ),
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="v1",
        )


def test_assembler_rejects_source_item_without_evidence() -> None:
    knowledge = (
        build_meeting_knowledge()
    )

    knowledge.chunks[
        0
    ].topics[
        0
    ] = MeetingTopic(
        title="Arquitectura",
        summary="Arquitectura",
        evidence=[],
    )

    with pytest.raises(
        ValueError,
        match="requiere evidencia fuente",
    ):
        build_assembler().assemble(
            meeting_knowledge=knowledge,
            semantic_consolidation=(
                build_semantic_consolidation()
            ),
            narrative=(
                build_narrative()
            ),
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="v1",
        )


def test_assembler_rejects_narrative_unknown_source_id() -> None:
    narrative = build_narrative()

    narrative.key_points[
        0
    ] = grounded(
        "Se aprobó migrar la plataforma.",
        [
            99
        ],
    )

    with pytest.raises(
        ValueError,
        match="item semántico inexistente",
    ):
        build_assembler().assemble(
            meeting_knowledge=(
                build_meeting_knowledge()
            ),
            semantic_consolidation=(
                build_semantic_consolidation()
            ),
            narrative=narrative,
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="v1",
        )


def test_assembler_accepts_summary_with_valid_subset() -> None:
    narrative = build_narrative()

    narrative.executive_summary = grounded(
        (
            "Se revisó la arquitectura y se "
            "aprobó la migración."
        ),
        [
            0,
            1,
        ],
    )

    result = build_assembler().assemble(
        meeting_knowledge=(
            build_meeting_knowledge()
        ),
        semantic_consolidation=(
            build_semantic_consolidation()
        ),
        narrative=narrative,
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="v1",
    )

    assert (
        result.executive_summary
        == narrative.executive_summary.text
    )


@pytest.mark.parametrize(
    (
        "field_name",
        "value",
        "error_type",
    ),
    [
        (
            "provider",
            1,
            TypeError,
        ),
        (
            "provider",
            "   ",
            ValueError,
        ),
        (
            "model",
            None,
            TypeError,
        ),
        (
            "model",
            "",
            ValueError,
        ),
        (
            "prompt_version",
            1.5,
            TypeError,
        ),
        (
            "prompt_version",
            "  ",
            ValueError,
        ),
    ],
)
def test_assembler_rejects_invalid_artifact_metadata(
    field_name,
    value,
    error_type,
) -> None:
    metadata = {
        "provider": "ollama",
        "model": "qwen2.5:3b",
        "prompt_version": "v1",
    }

    metadata[
        field_name
    ] = value

    with pytest.raises(
        error_type
    ):
        build_assembler().assemble(
            meeting_knowledge=(
                build_meeting_knowledge()
            ),
            semantic_consolidation=(
                build_semantic_consolidation()
            ),
            narrative=(
                build_narrative()
            ),
            **metadata,
        )


def test_assembler_rejects_invalid_meeting_knowledge_type() -> None:
    with pytest.raises(
        TypeError,
        match="MeetingKnowledge",
    ):
        build_assembler().assemble(
            meeting_knowledge=object(),
            semantic_consolidation=(
                build_semantic_consolidation()
            ),
            narrative=(
                build_narrative()
            ),
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="v1",
        )


def test_assembler_rejects_invalid_semantic_type() -> None:
    with pytest.raises(
        TypeError,
        match="MeetingSemanticConsolidation",
    ):
        build_assembler().assemble(
            meeting_knowledge=(
                build_meeting_knowledge()
            ),
            semantic_consolidation=object(),
            narrative=(
                build_narrative()
            ),
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="v1",
        )


def test_assembler_rejects_invalid_narrative_type() -> None:
    with pytest.raises(
        TypeError,
        match="MeetingReportNarrative",
    ):
        build_assembler().assemble(
            meeting_knowledge=(
                build_meeting_knowledge()
            ),
            semantic_consolidation=(
                build_semantic_consolidation()
            ),
            narrative=object(),
            provider="ollama",
            model="qwen2.5:3b",
            prompt_version="v1",
        )


def test_assembler_does_not_mutate_inputs() -> None:
    knowledge = (
        build_meeting_knowledge()
    )
    consolidation = (
        build_semantic_consolidation()
    )
    narrative = (
        build_narrative()
    )

    original_knowledge = (
        knowledge.as_dict()
    )
    original_consolidation = (
        consolidation.as_dict()
    )
    original_narrative = (
        narrative.as_dict()
    )

    build_assembler().assemble(
        meeting_knowledge=knowledge,
        semantic_consolidation=consolidation,
        narrative=narrative,
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="v1",
    )

    assert (
        knowledge.as_dict()
        == original_knowledge
    )
    assert (
        consolidation.as_dict()
        == original_consolidation
    )
    assert (
        narrative.as_dict()
        == original_narrative
    )
