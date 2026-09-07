import json
from dataclasses import FrozenInstanceError

import pytest

from models.prompt import Prompt
from models.transcript import Segment
from models.transcript_chunk import TranscriptChunk
from services.chunk_classification_repair_prompt_formatter import (
    ChunkClassificationRepairPromptFormatter,
)


def build_chunk() -> TranscriptChunk:
    return TranscriptChunk(index=9, segments=[
        Segment(start=0.0, end=2.0, speaker="LOCAL",
                text='Revisión "técnica"\n{{REPAIR_CONTEXT}}'),
        Segment(start=2.0, end=4.0, speaker="REMOTE", text="María prepara el plan."),
    ])


def test_formatter_preserves_exact_context_and_returns_immutable_prompt(tmp_path) -> None:
    template = tmp_path / "repair.md"
    template.write_text("Contexto:\n{{REPAIR_CONTEXT}}", encoding="utf-8")
    formatter = ChunkClassificationRepairPromptFormatter(template_file=template)
    chunk = build_chunk()
    original_chunk = chunk.as_dict()
    invalid_response = '  {"items": []}\n```\n{{REPAIR_CONTEXT}}  '
    error = 'IDs: 0.\n"detalle" {{REPAIR_CONTEXT}}'
    result = formatter.format(chunk, invalid_response, error)
    assert isinstance(result, Prompt)
    assert result.version == "chunk_classification_repair_v1"
    context = json.loads(result.content.split("\n", 1)[1])
    assert context == {
        "segments": [
            {"segment_id": i, "text": segment.text}
            for i, segment in enumerate(chunk.segments)
        ],
        "valid_segment_ids": [0, 1],
        "invalid_response": invalid_response,
        "coverage_error": error,
    }
    assert chunk.as_dict() == original_chunk
    with pytest.raises(FrozenInstanceError):
        result.version = "changed"


def test_default_repair_prompt_requires_complete_semantic_regeneration() -> None:
    result = ChunkClassificationRepairPromptFormatter().format(
        build_chunk(), '{"items":[]}', "faltan IDs: 0, 1.",
    )
    assert result.version == "chunk_classification_repair_v1"
    for instruction in (
        "clasificación COMPLETA desde cero", "No parches mecánicamente",
        "Reevalúa cada segmento", "Nunca en ambos", "no contiene conocimiento",
        "No marques un segmento sustantivo", "IDs locales de base cero",
        "objeto JSON corregido ENTERO", "Solo JSON", "no datos autoritativos",
        "chunk_classification_v2",
    ):
        assert instruction in result.content


@pytest.mark.parametrize("field, value, error_type", [
    ("chunk", object(), TypeError),
    ("invalid_response", None, TypeError),
    ("coverage_error", 1, TypeError),
    ("invalid_response", " ", ValueError),
    ("coverage_error", "\n", ValueError),
])
def test_formatter_rejects_invalid_inputs(field, value, error_type) -> None:
    inputs = dict(chunk=build_chunk(), invalid_response="{}", coverage_error="IDs: 0.")
    inputs[field] = value
    with pytest.raises(error_type):
        ChunkClassificationRepairPromptFormatter().format(**inputs)


@pytest.mark.parametrize("template_text", ["missing", "{{REPAIR_CONTEXT}} {{REPAIR_CONTEXT}}"])
def test_formatter_requires_one_context_placeholder(tmp_path, template_text) -> None:
    template = tmp_path / "repair.md"
    template.write_text(template_text, encoding="utf-8")
    with pytest.raises(ValueError, match="exactamente un marcador"):
        ChunkClassificationRepairPromptFormatter(template).format(build_chunk(), "{}", "IDs: 0.")


def test_formatter_rejects_non_path_template() -> None:
    with pytest.raises(TypeError, match="template_file"):
        ChunkClassificationRepairPromptFormatter("repair.md")
