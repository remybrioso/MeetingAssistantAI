import pytest

from models.chunk_knowledge import ChunkKnowledge
from models.meeting_knowledge import MeetingKnowledge


def build_chunk(
    index: int,
    start: float,
    end: float,
    with_content: bool = True,
) -> ChunkKnowledge:
    return ChunkKnowledge(
        chunk_index=index,
        start=start,
        end=end,
        key_points=(
            [
                f"Punto confirmado del chunk {index}."
            ]
            if with_content
            else []
        ),
    )


def build_complete_chunks() -> list[ChunkKnowledge]:
    return [
        build_chunk(
            index=0,
            start=0.0,
            end=10.0,
        ),
        build_chunk(
            index=1,
            start=10.0,
            end=20.0,
            with_content=False,
        ),
        build_chunk(
            index=2,
            start=20.0,
            end=30.0,
        ),
    ]


def test_meeting_knowledge_accepts_complete_coverage() -> None:
    knowledge = MeetingKnowledge(
        source_chunk_count=3,
        chunks=build_complete_chunks(),
    )

    assert knowledge.analyzed_chunk_count == 3
    assert knowledge.content_chunk_count == 2
    assert knowledge.has_content is True
    assert knowledge.start == 0.0
    assert knowledge.end == 30.0


def test_meeting_knowledge_serializes_all_chunks_in_order() -> None:
    knowledge = MeetingKnowledge(
        source_chunk_count=3,
        chunks=build_complete_chunks(),
    )

    data = knowledge.as_dict()

    assert data["source_chunk_count"] == 3
    assert data["analyzed_chunk_count"] == 3
    assert data["content_chunk_count"] == 2
    assert data["start"] == 0.0
    assert data["end"] == 30.0

    assert [
        chunk["chunk_index"]
        for chunk in data["chunks"]
    ] == [
        0,
        1,
        2,
    ]


def test_meeting_knowledge_allows_empty_content_chunks() -> None:
    knowledge = MeetingKnowledge(
        source_chunk_count=2,
        chunks=[
            build_chunk(
                index=0,
                start=0.0,
                end=10.0,
                with_content=False,
            ),
            build_chunk(
                index=1,
                start=10.0,
                end=20.0,
                with_content=False,
            ),
        ],
    )

    assert knowledge.has_content is False
    assert knowledge.content_chunk_count == 0


@pytest.mark.parametrize(
    "value",
    [
        0,
        -1,
    ],
)
def test_meeting_knowledge_rejects_non_positive_source_count(
    value: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="debe ser mayor que cero",
    ):
        MeetingKnowledge(
            source_chunk_count=value,
            chunks=[],
        )


@pytest.mark.parametrize(
    "value",
    [
        True,
        1.5,
        "3",
    ],
)
def test_meeting_knowledge_rejects_invalid_source_count_type(
    value,
) -> None:
    with pytest.raises(
        TypeError,
        match="debe ser entero",
    ):
        MeetingKnowledge(
            source_chunk_count=value,
            chunks=[],
        )


def test_meeting_knowledge_rejects_non_list_chunks() -> None:
    with pytest.raises(
        TypeError,
        match="chunks debe ser una lista",
    ):
        MeetingKnowledge(
            source_chunk_count=1,
            chunks=(
                build_chunk(
                    index=0,
                    start=0.0,
                    end=10.0,
                ),
            ),
        )


def test_meeting_knowledge_rejects_wrong_chunk_type() -> None:
    with pytest.raises(
        TypeError,
        match="instancia de ChunkKnowledge",
    ):
        MeetingKnowledge(
            source_chunk_count=1,
            chunks=[
                object(),
            ],
        )


def test_meeting_knowledge_rejects_missing_chunk() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "se esperaban 3 chunks "
            "y se recibieron 2"
        ),
    ):
        MeetingKnowledge(
            source_chunk_count=3,
            chunks=[
                build_chunk(
                    index=0,
                    start=0.0,
                    end=10.0,
                ),
                build_chunk(
                    index=1,
                    start=10.0,
                    end=20.0,
                ),
            ],
        )


def test_meeting_knowledge_rejects_extra_chunk() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "se esperaban 2 chunks "
            "y se recibieron 3"
        ),
    ):
        MeetingKnowledge(
            source_chunk_count=2,
            chunks=build_complete_chunks(),
        )


def test_meeting_knowledge_rejects_gap_in_indices() -> None:
    with pytest.raises(
        ValueError,
        match="índices contiguos desde 0",
    ):
        MeetingKnowledge(
            source_chunk_count=3,
            chunks=[
                build_chunk(
                    index=0,
                    start=0.0,
                    end=10.0,
                ),
                build_chunk(
                    index=2,
                    start=20.0,
                    end=30.0,
                ),
                build_chunk(
                    index=3,
                    start=30.0,
                    end=40.0,
                ),
            ],
        )


def test_meeting_knowledge_rejects_out_of_order_chunks() -> None:
    chunks = build_complete_chunks()

    with pytest.raises(
        ValueError,
        match="índices contiguos desde 0",
    ):
        MeetingKnowledge(
            source_chunk_count=3,
            chunks=[
                chunks[1],
                chunks[0],
                chunks[2],
            ],
        )


def test_meeting_knowledge_copies_chunk_collection() -> None:
    chunks = build_complete_chunks()

    knowledge = MeetingKnowledge(
        source_chunk_count=3,
        chunks=chunks,
    )

    chunks.clear()

    assert knowledge.analyzed_chunk_count == 3
    assert [
        chunk.chunk_index
        for chunk in knowledge.chunks
    ] == [
        0,
        1,
        2,
    ]
