from pathlib import Path

from providers.whisper.whisper_provider import WhisperProvider


AUDIO_FILE = Path("output") / "test_whisper.wav"

if not AUDIO_FILE.exists():
    raise FileNotFoundError(
        "No existe output/test_whisper.wav"
    )

provider = WhisperProvider()

result = provider.transcribe(
    str(AUDIO_FILE)
)

print(result.as_dict())

assert result.language == "es"
assert len(result.segments) > 0

print()
print("Segmentos:", len(result.segments))
print("Prueba satisfactoria.")