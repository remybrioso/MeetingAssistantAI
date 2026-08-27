import json
from pathlib import Path

import pytest

from models.chunk_knowledge import ChunkKnowledge
from models.meeting_knowledge import MeetingKnowledge
from models.prompt import Prompt
from services.meeting_knowledge_prompt_formatter import (
    MeetingKnowledgePromptFormatter,
)


def build_meeting_knowledge() -> MeetingKnowledge:
    return MeetingKnowledge(
        source_chunk_count=3,
        chunks=[
            ChunkKnowledge(
                chunk_index=0,
                start=0.0,
                end=10.0,
                key_points=[
                    "Se revisó el alcance inicial.",
                ],
            ),
            ChunkKnowledge(
                chunk_index=1,
                start=10.0,
                end=20.0,
            ),
            ChunkKnowledge(
                chunk_index=2,
                start=20.0,
                end=30.0,
                conclusions=[
                    "Se continuará con las pruebas.",
                ],
            ),
        ],
    )


def create_template(
    tmp_path: Path,
    content: str = (
        "Consolida el conocimiento:\n\n"
        "{{MEETING_KNOWLEDGE}}"
    ),
) -> Path:
    template_file = (
        tmp_path
        / "meeting_report_consolidation_v1.md"
    )

    template_file.write_text(
        content,
        encoding="utf-8",
    )

    return template_file


def test_formatter_returns_versioned_prompt(
    tmp_path: Path,
) -> None:
    formatter = MeetingKnowledgePromptFormatter(
        template_file=create_template(
            tmp_path
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
        == "meeting_report_consolidation_v1"
    )

    assert (
        "{{MEETING_KNOWLEDGE}}"
        not in result.content
    )


def test_formatter_serializes_complete_meeting_knowledge(
    tmp_path: Path,
) -> None:
    meeting_knowledge = (
        build_meeting_knowledge()
    )

    formatter = MeetingKnowledgePromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    result = formatter.format(
        meeting_knowledge
    )

    serialized = json.dumps(
        meeting_knowledge.as_dict(),
        ensure_ascii=False,
        indent=4,
    )

    assert serialized in result.content

    assert (
        '"source_chunk_count": 3'
        in result.content
    )

    assert (
        '"analyzed_chunk_count": 3'
        in result.content
    )

    assert (
        '"chunk_index": 0'
        in result.content
    )

    assert (
        '"chunk_index": 1'
        in result.content
    )

    assert (
        '"chunk_index": 2'
        in result.content
    )


def test_formatter_preserves_early_and_late_knowledge(
    tmp_path: Path,
) -> None:
    formatter = MeetingKnowledgePromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    result = formatter.format(
        build_meeting_knowledge()
    )

    assert (
        "Se revisó el alcance inicial."
        in result.content
    )

    assert (
        "Se continuará con las pruebas."
        in result.content
    )


def test_formatter_preserves_unicode(
    tmp_path: Path,
) -> None:
    formatter = MeetingKnowledgePromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    result = formatter.format(
        build_meeting_knowledge()
    )

    assert "revisó" in result.content
    assert "\\u00f3" not in result.content


def test_formatter_does_not_modify_meeting_knowledge(
    tmp_path: Path,
) -> None:
    meeting_knowledge = (
        build_meeting_knowledge()
    )

    original_data = (
        meeting_knowledge.as_dict()
    )

    formatter = MeetingKnowledgePromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    formatter.format(
        meeting_knowledge
    )

    assert (
        meeting_knowledge.as_dict()
        == original_data
    )


def test_formatter_rejects_invalid_input(
    tmp_path: Path,
) -> None:
    formatter = MeetingKnowledgePromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    with pytest.raises(
        TypeError,
        match="instancia de MeetingKnowledge",
    ):
        formatter.format(
            object()
        )


def test_formatter_rejects_template_without_placeholder(
    tmp_path: Path,
) -> None:
    formatter = MeetingKnowledgePromptFormatter(
        template_file=create_template(
            tmp_path,
            content=(
                "Plantilla sin marcador."
            ),
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
    formatter = MeetingKnowledgePromptFormatter(
        template_file=create_template(
            tmp_path,
            content=(
                "{{MEETING_KNOWLEDGE}}\n"
                "{{MEETING_KNOWLEDGE}}"
            ),
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
    formatter = MeetingKnowledgePromptFormatter()

    assert formatter.template_file == Path(
        "prompts/"
        "meeting_report_consolidation_v1.md"
    )

    result = formatter.format(
        build_meeting_knowledge()
    )

    assert (
        result.version
        == "meeting_report_consolidation_v1"
    )

    assert (
        "Principio de cobertura total"
        in result.content
    )

    assert (
        "No favorezcas los últimos chunks"
        in result.content
    )

    assert (
        "no parafrasees `excerpt`"
        in result.content
    )
