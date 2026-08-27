import pytest

from models.chunk_knowledge import ChunkKnowledge
from models.meeting_knowledge import MeetingKnowledge
from services.meeting_knowledge_assembler import (
    MeetingKnowledgeAssembler,
)


def build_chunks() -> list[ChunkKnowledge]:
    return [
        ChunkKnowledge(
            chunk_index=0,
            start=0.0,
            end=10.0,
        ),
        ChunkKnowledge(
            chunk_index=1,
            start=10.0,
            end=20.0,
        ),
    ]


def test_assembler_builds_meeting_knowledge() -> None:
    chunks = build_chunks()

    result = MeetingKnowledgeAssembler().assemble(
        chunks=chunks,
        source_chunk_count=2,
    )

    assert isinstance(
        result,
        MeetingKnowledge,
    )
    assert result.source_chunk_count == 2
    assert result.analyzed_chunk_count == 2
    assert result.chunks[0] is chunks[0]
    assert result.chunks[1] is chunks[1]


def test_assembler_does_not_reorder_chunks() -> None:
    chunks = build_chunks()

    with pytest.raises(
        ValueError,
        match="índices contiguos desde 0",
    ):
        MeetingKnowledgeAssembler().assemble(
            chunks=[
                chunks[1],
                chunks[0],
            ],
            source_chunk_count=2,
        )


def test_assembler_propagates_incomplete_coverage() -> None:
    with pytest.raises(
        ValueError,
        match="cobertura completa",
    ):
        MeetingKnowledgeAssembler().assemble(
            chunks=[
                build_chunks()[0],
            ],
            source_chunk_count=2,
        )


def test_assembler_rejects_non_list_input() -> None:
    with pytest.raises(
        TypeError,
        match="chunks debe ser una lista",
    ):
        MeetingKnowledgeAssembler().assemble(
            chunks=tuple(
                build_chunks()
            ),
            source_chunk_count=2,
        )
