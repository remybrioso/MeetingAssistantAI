import json
from pathlib import Path

import pytest

from models.prompt import Prompt
from models.transcript import Segment
from models.transcript_chunk import TranscriptChunk
from services.chunk_classification_prompt_formatter import (
    ChunkClassificationPromptFormatter,
)


def build_chunk() -> TranscriptChunk:
    return TranscriptChunk(
        index=2,
        segments=[
            Segment(
                start=15.0,
                end=20.0,
                speaker="REMOTE",
                text="Revisión técnica y planificación.",
            ),
            Segment(
                start=20.0,
                end=25.0,
                speaker="USER",
                text="Confirmaremos las pruebas mañana.",
            ),
        ],
    )


def create_template(
    tmp_path: Path,
    content: str = (
        "Clasifica:\n"
        "{{SEGMENTS}}"
    ),
) -> Path:
    template_file = (
        tmp_path
        / "chunk_classification_v1.md"
    )
    template_file.write_text(
        content,
        encoding="utf-8",
    )
    return template_file


def test_formatter_returns_versioned_prompt(
    tmp_path: Path,
) -> None:
    formatter = ChunkClassificationPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    result = formatter.format(
        build_chunk()
    )

    assert isinstance(
        result,
        Prompt,
    )
    assert (
        result.version
        == "chunk_classification_v1"
    )
    assert "{{SEGMENTS}}" not in result.content


def test_formatter_serializes_compact_local_segment_ids(
    tmp_path: Path,
) -> None:
    chunk = build_chunk()

    formatter = ChunkClassificationPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    result = formatter.format(
        chunk
    )

    expected_segments = [
        {
            "segment_id": 0,
            "text": (
                "Revisión técnica y planificación."
            ),
        },
        {
            "segment_id": 1,
            "text": (
                "Confirmaremos las pruebas mañana."
            ),
        },
    ]

    expected_json = json.dumps(
        expected_segments,
        ensure_ascii=False,
        separators=(
            ",",
            ":",
        ),
    )

    assert expected_json in result.content
    assert '"speaker":' not in result.content
    assert '"start":' not in result.content
    assert '"end":' not in result.content
    assert '"index":2' not in result.content


def test_formatter_preserves_unicode(
    tmp_path: Path,
) -> None:
    formatter = ChunkClassificationPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    result = formatter.format(
        build_chunk()
    )

    assert "Revisión" in result.content
    assert "planificación" in result.content
    assert "\\u00f3" not in result.content


def test_formatter_does_not_modify_chunk(
    tmp_path: Path,
) -> None:
    chunk = build_chunk()
    original_data = chunk.as_dict()

    formatter = ChunkClassificationPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    formatter.format(
        chunk
    )

    assert chunk.as_dict() == original_data


def test_formatter_rejects_non_chunk(
    tmp_path: Path,
) -> None:
    formatter = ChunkClassificationPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    with pytest.raises(
        TypeError,
        match="TranscriptChunk",
    ):
        formatter.format(
            object()
        )


def test_formatter_rejects_template_without_placeholder(
    tmp_path: Path,
) -> None:
    formatter = ChunkClassificationPromptFormatter(
        template_file=create_template(
            tmp_path,
            content="Plantilla sin marcador.",
        )
    )

    with pytest.raises(
        ValueError,
        match="no contiene el marcador",
    ):
        formatter.format(
            build_chunk()
        )


def test_formatter_rejects_duplicate_placeholder(
    tmp_path: Path,
) -> None:
    formatter = ChunkClassificationPromptFormatter(
        template_file=create_template(
            tmp_path,
            content=(
                "{{SEGMENTS}}\n"
                "{{SEGMENTS}}"
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match="más de una ocurrencia",
    ):
        formatter.format(
            build_chunk()
        )
