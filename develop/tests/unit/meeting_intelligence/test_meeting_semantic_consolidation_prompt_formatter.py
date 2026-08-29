import json
from datetime import date
from pathlib import Path

import pytest

from application.runtime_paths import RuntimePaths
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
from models.prompt import Prompt
from services.meeting_semantic_consolidation_prompt_formatter import (
    MeetingSemanticConsolidationPromptFormatter,
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
        "Quedó pendiente confirmar la ventana."
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
                        evidence=evidence(
                            topic_text,
                            0.0,
                            4.0,
                        ),
                    ),
                ],
                decisions=[
                    Decision(
                        description=(
                            decision_text
                        ),
                        evidence=evidence(
                            decision_text,
                            4.0,
                            8.0,
                        ),
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
                        evidence=evidence(
                            action_text,
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
                        description=risk_text,
                        evidence=evidence(
                            risk_text,
                            20.0,
                            24.0,
                        ),
                    ),
                ],
                pending_items=[
                    PendingItem(
                        description=(
                            pending_text
                        ),
                        evidence=evidence(
                            pending_text,
                            24.0,
                            28.0,
                        ),
                    ),
                ],
            ),
        ],
    )


def create_template(
    tmp_path: Path,
    content: str = (
        "Consolida:\n"
        "{{SOURCE_CATALOG}}"
    ),
) -> Path:
    template_file = (
        tmp_path
        / "meeting_semantic_consolidation_v1.md"
    )

    template_file.write_text(
        content,
        encoding="utf-8",
    )

    return template_file


def extract_catalog(
    prompt: Prompt,
) -> list[dict]:
    marker = "Consolida:\n"

    assert prompt.content.startswith(
        marker
    )

    return json.loads(
        prompt.content[
            len(marker):
        ]
    )


def test_formatter_returns_versioned_prompt(
    tmp_path: Path,
) -> None:
    formatter = (
        MeetingSemanticConsolidationPromptFormatter(
            template_file=create_template(
                tmp_path
            )
        )
    )

    result = formatter.format(
        build_meeting_knowledge()
    )

    assert isinstance(
        result,
        Prompt,
    )
    assert (
        result.version
        == "meeting_semantic_consolidation_v1"
    )
    assert (
        "{{SOURCE_CATALOG}}"
        not in result.content
    )


def test_formatter_builds_compact_complete_catalog(
    tmp_path: Path,
) -> None:
    formatter = (
        MeetingSemanticConsolidationPromptFormatter(
            template_file=create_template(
                tmp_path
            )
        )
    )

    result = formatter.format(
        build_meeting_knowledge()
    )

    catalog = extract_catalog(
        result
    )

    assert [
        item["kind"]
        for item in catalog
    ] == [
        "topic",
        "decision",
        "action",
        "risk",
        "pending",
    ]

    assert [
        (
            item["chunk_index"],
            item["item_index"],
        )
        for item in catalog
    ] == [
        (0, 0),
        (0, 0),
        (0, 0),
        (1, 0),
        (1, 0),
    ]


def test_formatter_sends_action_metadata_as_context(
    tmp_path: Path,
) -> None:
    formatter = (
        MeetingSemanticConsolidationPromptFormatter(
            template_file=create_template(
                tmp_path
            )
        )
    )

    catalog = extract_catalog(
        formatter.format(
            build_meeting_knowledge()
        )
    )

    action = next(
        item
        for item in catalog
        if item["kind"] == "action"
    )

    assert action["owner"] == "María"
    assert (
        action["due_date"]
        == "2026-08-30"
    )
    assert action["status"] == "pending"


def test_formatter_does_not_serialize_full_evidence(
    tmp_path: Path,
) -> None:
    formatter = (
        MeetingSemanticConsolidationPromptFormatter(
            template_file=create_template(
                tmp_path
            )
        )
    )

    catalog = extract_catalog(
        formatter.format(
            build_meeting_knowledge()
        )
    )

    forbidden_fields = {
        "evidence",
        "speaker",
        "start",
        "end",
        "excerpt",
    }

    for entry in catalog:
        assert not (
            forbidden_fields
            & set(
                entry.keys()
            )
        )


def test_formatter_preserves_unicode(
    tmp_path: Path,
) -> None:
    formatter = (
        MeetingSemanticConsolidationPromptFormatter(
            template_file=create_template(
                tmp_path
            )
        )
    )

    result = formatter.format(
        build_meeting_knowledge()
    )

    assert "María" in result.content
    assert "\\u00ed" not in result.content


def test_formatter_does_not_mutate_meeting_knowledge(
    tmp_path: Path,
) -> None:
    knowledge = (
        build_meeting_knowledge()
    )
    original = knowledge.as_dict()

    formatter = (
        MeetingSemanticConsolidationPromptFormatter(
            template_file=create_template(
                tmp_path
            )
        )
    )

    formatter.format(
        knowledge
    )

    assert (
        knowledge.as_dict()
        == original
    )


def test_formatter_rejects_invalid_input(
    tmp_path: Path,
) -> None:
    formatter = (
        MeetingSemanticConsolidationPromptFormatter(
            template_file=create_template(
                tmp_path
            )
        )
    )

    with pytest.raises(
        TypeError,
        match="instancia de MeetingKnowledge",
    ):
        formatter.format(
            object()
        )


def test_formatter_rejects_missing_placeholder(
    tmp_path: Path,
) -> None:
    formatter = (
        MeetingSemanticConsolidationPromptFormatter(
            template_file=create_template(
                tmp_path,
                content="Sin marcador.",
            )
        )
    )

    with pytest.raises(
        ValueError,
        match="no contiene el marcador",
    ):
        formatter.format(
            build_meeting_knowledge()
        )


def test_formatter_rejects_duplicate_placeholder(
    tmp_path: Path,
) -> None:
    formatter = (
        MeetingSemanticConsolidationPromptFormatter(
            template_file=create_template(
                tmp_path,
                content=(
                    "{{SOURCE_CATALOG}}\n"
                    "{{SOURCE_CATALOG}}"
                ),
            )
        )
    )

    with pytest.raises(
        ValueError,
        match="más de una ocurrencia",
    ):
        formatter.format(
            build_meeting_knowledge()
        )


def test_formatter_resolves_default_contract_template() -> None:
    formatter = (
        MeetingSemanticConsolidationPromptFormatter()
    )

    expected_template = (
        RuntimePaths.resolve()
        .prompts_directory
        / "meeting_semantic_consolidation_v1.md"
    )

    assert (
        formatter.template_file
        == expected_template
    )

    result = formatter.format(
        build_meeting_knowledge()
    )

    assert (
        result.version
        == "meeting_semantic_consolidation_v1"
    )
    assert (
        "Regla de cobertura exacta"
        in result.content
    )
    assert (
        "No devuelvas esos campos."
        in result.content
    )
