import json
from pathlib import Path

import pytest

from models.chunk_classification import (
    ChunkClassification,
    ChunkKnowledgeKind,
    ClassifiedKnowledgeItem,
)
from models.prompt import Prompt
from models.transcript import Segment
from models.transcript_chunk import TranscriptChunk
from services.chunk_action_metadata_prompt_formatter import (
    ChunkActionMetadataPromptFormatter,
)


def build_chunk() -> TranscriptChunk:
    return TranscriptChunk(
        index=3,
        segments=[
            Segment(
                start=10.0,
                end=15.0,
                speaker="LOCAL",
                text="Se revisó la arquitectura.",
            ),
            Segment(
                start=15.0,
                end=20.0,
                speaker="REMOTE",
                text=(
                    "María debe preparar el plan "
                    "antes del 30 de agosto de 2026."
                ),
            ),
            Segment(
                start=20.0,
                end=25.0,
                speaker="LOCAL",
                text=(
                    "Infraestructura debe validar el respaldo."
                ),
            ),
        ],
    )


def build_classification() -> ChunkClassification:
    chunk = build_chunk()

    return ChunkClassification(
        chunk_index=chunk.index,
        start=chunk.start,
        end=chunk.end,
        items=[
            ClassifiedKnowledgeItem(
                kind=ChunkKnowledgeKind.TOPIC,
                description="Se revisó la arquitectura.",
                segment_ids=[
                    0,
                ],
            ),
            ClassifiedKnowledgeItem(
                kind=ChunkKnowledgeKind.ACTION,
                description="María debe preparar el plan.",
                segment_ids=[
                    1,
                ],
            ),
            ClassifiedKnowledgeItem(
                kind=ChunkKnowledgeKind.ACTION,
                description=(
                    "Infraestructura debe validar el respaldo."
                ),
                segment_ids=[
                    2,
                ],
            ),
        ],
    )


def create_template(
    tmp_path: Path,
    content: str = (
        "Enriquece:\n"
        "{{ACTIONS}}"
    ),
) -> Path:
    template_file = (
        tmp_path
        / "chunk_action_metadata_v1.md"
    )
    template_file.write_text(
        content,
        encoding="utf-8",
    )
    return template_file


def test_formatter_returns_versioned_prompt(
    tmp_path: Path,
) -> None:
    formatter = ChunkActionMetadataPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    result = formatter.format(
        classification=build_classification(),
        chunk=build_chunk(),
    )

    assert isinstance(
        result,
        Prompt,
    )
    assert (
        result.version
        == "chunk_action_metadata_v1"
    )
    assert "{{ACTIONS}}" not in result.content


def test_formatter_batches_all_actions_in_one_payload(
    tmp_path: Path,
) -> None:
    formatter = ChunkActionMetadataPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    result = formatter.format(
        classification=build_classification(),
        chunk=build_chunk(),
    )

    expected_payload = [
        {
            "item_index": 1,
            "description": (
                "María debe preparar el plan."
            ),
            "segments": [
                {
                    "segment_id": 1,
                    "text": (
                        "María debe preparar el plan "
                        "antes del 30 de agosto de 2026."
                    ),
                }
            ],
        },
        {
            "item_index": 2,
            "description": (
                "Infraestructura debe validar el respaldo."
            ),
            "segments": [
                {
                    "segment_id": 2,
                    "text": (
                        "Infraestructura debe validar el respaldo."
                    ),
                }
            ],
        },
    ]

    expected_json = json.dumps(
        expected_payload,
        ensure_ascii=False,
        separators=(
            ",",
            ":",
        ),
    )

    assert expected_json in result.content


def test_formatter_excludes_non_action_items(
    tmp_path: Path,
) -> None:
    formatter = ChunkActionMetadataPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    result = formatter.format(
        classification=build_classification(),
        chunk=build_chunk(),
    )

    assert "Se revisó la arquitectura." not in result.content


def test_formatter_does_not_send_speaker_or_timestamps(
    tmp_path: Path,
) -> None:
    formatter = ChunkActionMetadataPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    result = formatter.format(
        classification=build_classification(),
        chunk=build_chunk(),
    )

    assert '"speaker":' not in result.content
    assert '"start":' not in result.content
    assert '"end":' not in result.content
    assert "REMOTE" not in result.content


def test_formatter_preserves_unicode(
    tmp_path: Path,
) -> None:
    formatter = ChunkActionMetadataPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    result = formatter.format(
        classification=build_classification(),
        chunk=build_chunk(),
    )

    assert "María" in result.content
    assert "\\u00ed" not in result.content


def test_formatter_rejects_classification_without_actions(
    tmp_path: Path,
) -> None:
    chunk = build_chunk()
    classification = ChunkClassification(
        chunk_index=chunk.index,
        start=chunk.start,
        end=chunk.end,
        items=[
            ClassifiedKnowledgeItem(
                kind=ChunkKnowledgeKind.TOPIC,
                description="Tema general.",
                segment_ids=[
                    0,
                ],
            )
        ],
    )

    formatter = ChunkActionMetadataPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    with pytest.raises(
        ValueError,
        match="no contiene acciones",
    ):
        formatter.format(
            classification=classification,
            chunk=chunk,
        )


def test_formatter_rejects_chunk_index_mismatch(
    tmp_path: Path,
) -> None:
    classification = build_classification()
    classification.chunk_index = 99

    formatter = ChunkActionMetadataPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    with pytest.raises(
        ValueError,
        match="chunk_index",
    ):
        formatter.format(
            classification=classification,
            chunk=build_chunk(),
        )


def test_formatter_rejects_out_of_range_segment_id(
    tmp_path: Path,
) -> None:
    chunk = build_chunk()
    classification = ChunkClassification(
        chunk_index=chunk.index,
        start=chunk.start,
        end=chunk.end,
        items=[
            ClassifiedKnowledgeItem(
                kind=ChunkKnowledgeKind.ACTION,
                description="Acción inválida.",
                segment_ids=[
                    99,
                ],
            )
        ],
    )

    formatter = ChunkActionMetadataPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    with pytest.raises(
        ValueError,
        match="segment_id inexistente",
    ):
        formatter.format(
            classification=classification,
            chunk=chunk,
        )


def test_formatter_does_not_modify_inputs(
    tmp_path: Path,
) -> None:
    chunk = build_chunk()
    classification = build_classification()

    original_chunk = chunk.as_dict()
    original_classification = (
        classification.as_dict()
    )

    formatter = ChunkActionMetadataPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    formatter.format(
        classification=classification,
        chunk=chunk,
    )

    assert chunk.as_dict() == original_chunk
    assert (
        classification.as_dict()
        == original_classification
    )


def test_formatter_rejects_template_without_placeholder(
    tmp_path: Path,
) -> None:
    formatter = ChunkActionMetadataPromptFormatter(
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
            classification=build_classification(),
            chunk=build_chunk(),
        )


def test_formatter_rejects_duplicate_placeholder(
    tmp_path: Path,
) -> None:
    formatter = ChunkActionMetadataPromptFormatter(
        template_file=create_template(
            tmp_path,
            content=(
                "{{ACTIONS}}\n"
                "{{ACTIONS}}"
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match="más de una ocurrencia",
    ):
        formatter.format(
            classification=build_classification(),
            chunk=build_chunk(),
        )


def test_formatter_rejects_non_classification(
    tmp_path: Path,
) -> None:
    formatter = ChunkActionMetadataPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    with pytest.raises(
        TypeError,
        match="ChunkClassification",
    ):
        formatter.format(
            classification=object(),
            chunk=build_chunk(),
        )


def test_formatter_rejects_non_chunk(
    tmp_path: Path,
) -> None:
    formatter = ChunkActionMetadataPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    with pytest.raises(
        TypeError,
        match="TranscriptChunk",
    ):
        formatter.format(
            classification=build_classification(),
            chunk=object(),
        )
