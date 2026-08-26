import json
from pathlib import Path

import pytest

from models.prompt import Prompt
from models.transcript import Segment
from models.transcript_chunk import TranscriptChunk
from services.chunk_prompt_formatter import (
    ChunkPromptFormatter,
)


def build_chunk() -> TranscriptChunk:
    return TranscriptChunk(
        index=2,
        segments=[
            Segment(
                start=15.0,
                end=20.0,
                speaker="REMOTE",
                text=(
                    "Revisión técnica y planificación."
                ),
            ),
            Segment(
                start=20.0,
                end=25.0,
                speaker="USER",
                text=(
                    "Confirmaremos las pruebas mañana."
                ),
            ),
        ],
    )


def create_template(
    tmp_path: Path,
    content: str = (
        "Analiza este bloque:\n\n"
        "{{CHUNK}}"
    ),
) -> Path:
    template_file = (
        tmp_path / "chunk_knowledge_v1.md"
    )
    template_file.write_text(
        content,
        encoding="utf-8",
    )
    return template_file


def test_formatter_returns_versioned_prompt(
    tmp_path: Path,
) -> None:
    formatter = ChunkPromptFormatter(
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
        == "chunk_knowledge_v1"
    )
    assert "{{CHUNK}}" not in result.content


def test_formatter_serializes_complete_chunk(
    tmp_path: Path,
) -> None:
    chunk = build_chunk()

    formatter = ChunkPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    result = formatter.format(
        chunk
    )

    chunk_json = json.dumps(
        chunk.as_dict(),
        ensure_ascii=False,
        indent=4,
    )

    assert chunk_json in result.content
    assert '"index": 2' in result.content
    assert '"start": 15.0' in result.content
    assert '"end": 25.0' in result.content
    assert '"speaker": "REMOTE"' in result.content


def test_formatter_preserves_unicode(
    tmp_path: Path,
) -> None:
    formatter = ChunkPromptFormatter(
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

    formatter = ChunkPromptFormatter(
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
    formatter = ChunkPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    with pytest.raises(
        TypeError,
        match="debe ser una instancia de TranscriptChunk",
    ):
        formatter.format(
            object()
        )


def test_formatter_rejects_template_without_placeholder(
    tmp_path: Path,
) -> None:
    formatter = ChunkPromptFormatter(
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
    formatter = ChunkPromptFormatter(
        template_file=create_template(
            tmp_path,
            content=(
                "{{CHUNK}}\n"
                "{{CHUNK}}"
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


def test_formatter_resolves_default_contract_template() -> None:
    formatter = ChunkPromptFormatter()

    assert formatter.template_file == Path(
        "prompts/chunk_knowledge_v1.md"
    )

    result = formatter.format(
        build_chunk()
    )

    assert (
        result.version
        == "chunk_knowledge_v1"
    )
    assert "Reglas de fidelidad" in result.content
