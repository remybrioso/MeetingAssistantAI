from providers.whisper.whisper_models import (
    WhisperResult,
    WhisperSegment,
    WhisperWord,
)


result = WhisperResult(
    language="es",
    segments=[
        WhisperSegment(
            start=0.0,
            end=2.5,
            text="Buenos días.",
            words=[
                WhisperWord(
                    start=0.0,
                    end=0.8,
                    text="Buenos",
                    probability=0.95,
                ),
                WhisperWord(
                    start=0.9,
                    end=1.4,
                    text="días",
                    probability=0.94,
                ),
            ],
        )
    ],
)

print(result.as_dict())

assert result.language == "es"
assert len(result.segments) == 1
assert len(result.segments[0].words) == 2

print()
print("Prueba satisfactoria.")