from faster_whisper import WhisperModel
import time

print("=" * 60)
print("Meeting Assistant AI - Faster Whisper Lab")
print("=" * 60)

start = time.time()

print("\nCargando modelo 'base'...\n")

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

elapsed = time.time() - start

print(f"Modelo cargado en {elapsed:.2f} segundos")

print("\nPrueba finalizada correctamente.")