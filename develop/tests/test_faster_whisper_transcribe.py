import time
from pathlib import Path

from faster_whisper import WhisperModel


AUDIO_FILE = Path("output") / "test_whisper.wav"

MODEL_NAME = "base"
DEVICE = "cpu"
COMPUTE_TYPE = "int8"
LANGUAGE = "es"


if not AUDIO_FILE.exists():
    raise FileNotFoundError(
        f"No existe {AUDIO_FILE}. "
        "Copia un mic.wav reciente y renómbralo como output/test_whisper.wav"
    )


print("=" * 60)
print("Meeting Assistant AI - Faster Whisper Transcription Lab")
print("=" * 60)

print()
print(f"Audio: {AUDIO_FILE}")
print(f"Modelo: {MODEL_NAME}")
print(f"Device: {DEVICE}")
print(f"Compute Type: {COMPUTE_TYPE}")
print(f"Idioma: {LANGUAGE}")

print()
print("Cargando modelo...")

load_start = time.time()

model = WhisperModel(
    MODEL_NAME,
    device=DEVICE,
    compute_type=COMPUTE_TYPE
)

load_time = time.time() - load_start

print(f"Modelo cargado en {load_time:.2f} segundos")

print()
print("Transcribiendo...")

transcribe_start = time.time()

segments, info = model.transcribe(
    str(AUDIO_FILE),
    language=LANGUAGE,
    beam_size=5,
    word_timestamps=True
)

segments = list(segments)

transcribe_time = time.time() - transcribe_start

print()
print("=" * 60)
print("RESULTADO")
print("=" * 60)

print()
print(f"Idioma detectado: {info.language}")
print(f"Probabilidad idioma: {info.language_probability:.2f}")
print(f"Tiempo carga modelo: {load_time:.2f} s")
print(f"Tiempo transcripción: {transcribe_time:.2f} s")
print(f"Segmentos: {len(segments)}")

print()
print("=" * 60)
print("SEGMENTOS")
print("=" * 60)

for segment in segments:
    print()
    print(f"[{segment.start:.2f} - {segment.end:.2f}]")
    print(segment.text.strip())

    if segment.words:
        print("Palabras:")
        for word in segment.words:
            print(
                f"  {word.start:.2f}-{word.end:.2f} "
                f"{word.word.strip()}"
            )

print()
print("Prueba finalizada.")