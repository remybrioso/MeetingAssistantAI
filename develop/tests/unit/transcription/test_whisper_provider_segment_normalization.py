from types import SimpleNamespace

from providers.whisper.whisper_provider import (
    WhisperProvider,
)
from providers.whisper.whisper_segment_normalizer import (
    WhisperSegmentNormalizer,
)


class FakeWhisperModel:

    def transcribe(
        self,
        audio_file,
        **kwargs,
    ):
        segment = SimpleNamespace(
            start=10.0,
            end=100.0,
            text="primero segundo",
            words=[
                SimpleNamespace(
                    start=10.0,
                    end=11.0,
                    word="primero",
                    probability=0.9,
                ),
                SimpleNamespace(
                    start=90.0,
                    end=91.0,
                    word="segundo",
                    probability=0.8,
                ),
            ],
        )

        info = SimpleNamespace(
            language="es",
            language_probability=0.99,
        )

        return (
            [
                segment
            ],
            info,
        )


def test_provider_normalizes_discontinuous_whisper_segments() -> None:
    provider = WhisperProvider(
        segment_normalizer=(
            WhisperSegmentNormalizer(
                max_word_gap_seconds=10.0
            )
        )
    )

    provider._model = (
        FakeWhisperModel()
    )

    result = provider.transcribe(
        "meeting.wav"
    )

    assert result.language == "es"

    assert len(
        result.segments
    ) == 2

    assert (
        result.segments[0].start
        == 10.0
    )

    assert (
        result.segments[0].end
        == 11.0
    )

    assert (
        result.segments[0].text
        == "primero"
    )

    assert (
        result.segments[1].start
        == 90.0
    )

    assert (
        result.segments[1].end
        == 91.0
    )

    assert (
        result.segments[1].text
        == "segundo"
    )
