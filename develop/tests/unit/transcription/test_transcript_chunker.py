import pytest

from models.transcript import Segment, Transcript
from models.transcript_chunk import TranscriptChunk
from services.transcript_chunker import TranscriptChunker


def build_segment(
    start: float,
    end: float,
    speaker: str,
    text: str,
) -> Segment:
    return Segment(
        start=start,
        end=end,
        speaker=speaker,
        text=text,
    )


def test_chunk_exposes_traceable_metadata() -> None:
    first = build_segment(
        10.0,
        12.0,
        "USER",
        "uno dos",
    )

    second = build_segment(
        12.5,
        15.0,
        "REMOTE",
        "tres cuatro cinco",
    )

    chunk = TranscriptChunk(
        index=0,
        segments=[
            first,
            second,
        ],
    )

    assert chunk.start == 10.0
    assert chunk.end == 15.0
    assert chunk.duration == 5.0
    assert chunk.word_count == 5

    assert chunk.segments == [
        first,
        second,
    ]


def test_chunk_uses_real_temporal_envelope_for_overlapping_segments() -> None:
    local = build_segment(
        10.0,
        20.0,
        "LOCAL",
        "intervencion local",
    )

    remote = build_segment(
        15.0,
        16.0,
        "REMOTE",
        "respuesta remota",
    )

    chunk = TranscriptChunk(
        index=0,
        segments=[
            local,
            remote,
        ],
    )

    assert chunk.start == 10.0
    assert chunk.end == 20.0
    assert chunk.duration == 10.0


def test_chunk_uses_minimum_start_even_if_input_is_not_sorted() -> None:
    later = build_segment(
        20.0,
        22.0,
        "REMOTE",
        "segmento posterior",
    )

    earlier = build_segment(
        10.0,
        12.0,
        "LOCAL",
        "segmento anterior",
    )

    chunk = TranscriptChunk(
        index=0,
        segments=[
            later,
            earlier,
        ],
    )

    assert chunk.start == 10.0
    assert chunk.end == 22.0


def test_chunk_rejects_empty_segments() -> None:
    with pytest.raises(
        ValueError,
        match="al menos un segmento",
    ):
        TranscriptChunk(
            index=0,
            segments=[],
        )


def test_chunker_returns_empty_list_for_empty_transcript() -> None:
    chunks = TranscriptChunker().chunk(
        Transcript()
    )

    assert chunks == []


def test_chunker_keeps_short_transcript_in_single_chunk() -> None:
    segments = [
        build_segment(
            0.0,
            2.0,
            "USER",
            "uno dos tres",
        ),
        build_segment(
            2.0,
            4.0,
            "REMOTE",
            "cuatro cinco",
        ),
    ]

    chunks = TranscriptChunker(
        max_words=10
    ).chunk(
        Transcript(
            segments=segments
        )
    )

    assert len(chunks) == 1

    assert chunks[0].index == 0

    assert (
        chunks[0].segments
        == segments
    )


def test_chunker_splits_before_segment_that_exceeds_limit() -> None:
    first = build_segment(
        0.0,
        1.0,
        "USER",
        "uno dos tres",
    )

    second = build_segment(
        1.0,
        2.0,
        "REMOTE",
        "cuatro cinco tres",
    )

    third = build_segment(
        2.0,
        3.0,
        "USER",
        "seis siete",
    )

    chunks = TranscriptChunker(
        max_words=5
    ).chunk(
        Transcript(
            segments=[
                first,
                second,
                third,
            ]
        )
    )

    assert len(chunks) == 2

    assert chunks[0].segments == [
        first,
    ]

    assert chunks[1].segments == [
        second,
        third,
    ]

    assert chunks[0].word_count == 3
    assert chunks[1].word_count == 5


def test_chunker_never_splits_large_segment() -> None:
    large = build_segment(
        5.0,
        20.0,
        "USER",
        (
            "uno dos tres cuatro "
            "cinco seis"
        ),
    )

    chunks = TranscriptChunker(
        max_words=3
    ).chunk(
        Transcript(
            segments=[
                large,
            ]
        )
    )

    assert len(chunks) == 1

    assert chunks[0].segments == [
        large,
    ]

    assert chunks[0].word_count == 6


def test_chunker_preserves_all_segments_exactly_once() -> None:
    segments = [
        build_segment(
            float(index),
            float(index + 1),
            "USER",
            f"segmento numero {index}",
        )
        for index in range(10)
    ]

    chunks = TranscriptChunker(
        max_words=7
    ).chunk(
        Transcript(
            segments=segments
        )
    )

    flattened = [
        segment
        for chunk in chunks
        for segment in chunk.segments
    ]

    assert (
        flattened
        == segments
    )

    assert (
        len(
            {
                id(segment)
                for segment in flattened
            }
        )
        == len(segments)
    )


def test_chunker_preserves_timestamps_and_speakers() -> None:
    segments = [
        build_segment(
            1.25,
            2.75,
            "USER",
            "primer segmento",
        ),
        build_segment(
            3.0,
            4.5,
            "REMOTE",
            "segundo segmento",
        ),
    ]

    chunks = TranscriptChunker(
        max_words=2
    ).chunk(
        Transcript(
            segments=segments
        )
    )

    assert len(chunks) == 2

    assert chunks[0].start == 1.25
    assert chunks[0].end == 2.75

    assert (
        chunks[0].segments[0].speaker
        == "USER"
    )

    assert chunks[1].start == 3.0
    assert chunks[1].end == 4.5

    assert (
        chunks[1].segments[0].speaker
        == "REMOTE"
    )


def test_chunker_validates_configuration() -> None:
    with pytest.raises(
        TypeError,
        match="max_words debe ser entero",
    ):
        TranscriptChunker(
            max_words=10.5
        )

    with pytest.raises(
        ValueError,
        match="mayor que cero",
    ):
        TranscriptChunker(
            max_words=0
        )


def test_chunker_rejects_non_transcript() -> None:
    with pytest.raises(
        TypeError,
        match="transcript debe ser una instancia",
    ):
        TranscriptChunker().chunk(
            object()
        )
