import json
from dataclasses import FrozenInstanceError

import pytest

from models.prompt import Prompt
from models.transcript import Segment
from models.transcript_chunk import TranscriptChunk
from services.chunk_ignored_segment_audit_prompt_formatter import (
    ChunkIgnoredSegmentAuditPromptFormatter,
)


def build_chunk() -> TranscriptChunk:
    return TranscriptChunk(index=1, segments=[
        Segment(start=0.0, end=1.0, speaker="LOCAL", text="No debe incluirse."),
        Segment(start=1.0, end=2.0, speaker="REMOTE", text="Auditar este tema."),
        Segment(start=2.0, end=3.0, speaker="LOCAL", text="Tampoco incluirse."),
        Segment(start=3.0, end=4.0, speaker="REMOTE", text="Auditar esta acción."),
        Segment(start=4.0, end=5.0, speaker="LOCAL", text="Confirmar ignorado."),
    ])


def test_formatter_supplies_only_candidate_segments(tmp_path) -> None:
    template = tmp_path / "audit.md"
    template.write_text("Audita:\n{{CANDIDATE_SEGMENTS}}", encoding="utf-8")
    result = ChunkIgnoredSegmentAuditPromptFormatter(template).format(build_chunk(), [1, 3])
    assert isinstance(result, Prompt)
    assert result.version == "chunk_ignored_segment_audit_v1"
    payload = json.loads(result.content.split("\n", 1)[1])
    assert payload["candidate_segment_ids"] == [1, 3]
    assert payload["segments"] == [
        {"segment_id": 1, "text": "Auditar este tema."},
        {"segment_id": 3, "text": "Auditar esta acción."},
    ]
    assert "No debe incluirse" not in result.content
    assert "Confirmar ignorado" not in result.content
    with pytest.raises(FrozenInstanceError):
        result.version = "other"


def test_default_prompt_challenges_ignored_decision() -> None:
    result = ChunkIgnoredSegmentAuditPromptFormatter().format(build_chunk(), [4])
    for text in (
        "debes desafiarla",
        "conocimiento sustantivo",
        "Nunca marques como ignorado",
        "nunca en ambos",
        "exactamente `items`",
    ):
        assert text in result.content


@pytest.mark.parametrize("candidate_ids, error_type", [
    ([1, 1], ValueError),
    ([9], ValueError),
    ([True], TypeError),
    ("1", TypeError),
])
def test_formatter_rejects_invalid_candidate_ids(candidate_ids, error_type) -> None:
    with pytest.raises(error_type):
        ChunkIgnoredSegmentAuditPromptFormatter().format(build_chunk(), candidate_ids)


def test_formatter_rejects_bad_template(tmp_path) -> None:
    template = tmp_path / "audit.md"
    template.write_text("without marker", encoding="utf-8")
    with pytest.raises(ValueError, match="exactamente un marcador"):
        ChunkIgnoredSegmentAuditPromptFormatter(template).format(build_chunk(), [1])


def test_formatter_rejects_non_chunk() -> None:
    with pytest.raises(TypeError, match="TranscriptChunk"):
        ChunkIgnoredSegmentAuditPromptFormatter().format(object(), [1])
