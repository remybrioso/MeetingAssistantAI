import pytest

from providers.whisper.whisper_models import (
    WhisperSegment,
    WhisperWord,
)
from providers.whisper.whisper_segment_normalizer import (
    WhisperSegmentNormalizer,
)


def build_word(
    start: float,
    end: float,
    text: str,
) -> WhisperWord:
    return WhisperWord(
        start=start,
        end=end,
        text=text,
        probability=0.95,
    )


def test_normalizer_preserves_contiguous_segment_without_changes() -> None:
    segment = WhisperSegment(
        start=10.0,
        end=14.0,
        text="Texto original continuo.",
        words=[
            build_word(
                10.2,
                11.0,
                "Texto",
            ),
            build_word(
                11.2,
                12.0,
                "original",
            ),
            build_word(
                12.2,
                13.8,
                "continuo.",
            ),
        ],
    )

    normalized = (
        WhisperSegmentNormalizer()
        .normalize(
            segment
        )
    )

    assert normalized == [
        segment
    ]

    assert (
        normalized[0]
        is segment
    )


def test_normalizer_splits_segment_with_large_internal_gap() -> None:
    segment = WhisperSegment(
        start=736.3,
        end=2061.52,
        text=(
            "Primer bloque separado "
            "segundo bloque"
        ),
        words=[
            build_word(
                736.3,
                737.0,
                "Primer",
            ),
            build_word(
                737.1,
                741.94,
                "bloque",
            ),
            build_word(
                2052.42,
                2053.0,
                "segundo",
            ),
            build_word(
                2053.1,
                2061.52,
                "bloque",
            ),
        ],
    )

    normalized = (
        WhisperSegmentNormalizer()
        .normalize(
            segment
        )
    )

    assert len(
        normalized
    ) == 2

    first, second = normalized

    assert first.start == 736.3
    assert first.end == 741.94
    assert first.text == "Primer bloque"

    assert second.start == 2052.42
    assert second.end == 2061.52
    assert second.text == "segundo bloque"

    assert first.words == (
        segment.words[:2]
    )

    assert second.words == (
        segment.words[2:]
    )


def test_normalizer_can_split_multiple_discontinuities() -> None:
    segment = WhisperSegment(
        start=100.0,
        end=200.0,
        text="uno dos tres",
        words=[
            build_word(
                100.0,
                101.0,
                "uno",
            ),
            build_word(
                120.0,
                121.0,
                "dos",
            ),
            build_word(
                150.0,
                151.0,
                "tres",
            ),
        ],
    )

    normalized = (
        WhisperSegmentNormalizer(
            max_word_gap_seconds=10.0
        )
        .normalize(
            segment
        )
    )

    assert [
        item.text
        for item in normalized
    ] == [
        "uno",
        "dos",
        "tres",
    ]


def test_normalizer_does_not_split_gap_equal_to_threshold() -> None:
    segment = WhisperSegment(
        start=0.0,
        end=12.0,
        text="uno dos",
        words=[
            build_word(
                0.0,
                1.0,
                "uno",
            ),
            build_word(
                11.0,
                12.0,
                "dos",
            ),
        ],
    )

    normalized = (
        WhisperSegmentNormalizer(
            max_word_gap_seconds=10.0
        )
        .normalize(
            segment
        )
    )

    assert normalized == [
        segment
    ]


def test_normalizer_preserves_segment_without_words() -> None:
    segment = WhisperSegment(
        start=5.0,
        end=7.0,
        text="Texto sin timestamps de palabras.",
        words=[],
    )

    normalized = (
        WhisperSegmentNormalizer()
        .normalize(
            segment
        )
    )

    assert normalized == [
        segment
    ]


def test_normalizer_validates_configuration() -> None:
    with pytest.raises(
        TypeError,
        match="debe ser numérico",
    ):
        WhisperSegmentNormalizer(
            max_word_gap_seconds="10"
        )

    with pytest.raises(
        ValueError,
        match="mayor que cero",
    ):
        WhisperSegmentNormalizer(
            max_word_gap_seconds=0
        )


def test_normalizer_rejects_non_monotonic_words() -> None:
    segment = WhisperSegment(
        start=0.0,
        end=3.0,
        text="orden inválido",
        words=[
            build_word(
                2.0,
                3.0,
                "segundo",
            ),
            build_word(
                0.0,
                1.0,
                "primero",
            ),
        ],
    )

    with pytest.raises(
        ValueError,
        match="orden temporal",
    ):
        (
            WhisperSegmentNormalizer()
            .normalize(
                segment
            )
        )
