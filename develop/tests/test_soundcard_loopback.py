import os
import time

import soundcard as sc
import soundfile as sf


OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "system_soundcard.wav")

SAMPLE_RATE = 48000
DURATION = 10

os.makedirs(OUTPUT_DIR, exist_ok=True)

print()
print("===== SPEAKERS =====")
print()

speakers = sc.all_speakers()

for index, speaker in enumerate(speakers):
    print(f"{index}: {speaker.name}")

print()
selection = int(input("Seleccione speaker para loopback: "))

speaker = speakers[selection]

print()
print("Speaker seleccionado:")
print(speaker.name)

print()
print("IMPORTANTE:")
print("Reproduce audio ANTES de presionar Enter.")
print("Ejemplo: YouTube, música, video, etc.")
input("Cuando el audio esté sonando, presiona Enter para grabar...")

print()
print(f"Grabando audio del sistema durante {DURATION} segundos...")

loopback = sc.get_microphone(
    id=str(speaker.name),
    include_loopback=True
)

with loopback.recorder(samplerate=SAMPLE_RATE) as recorder:
    data = recorder.record(numframes=SAMPLE_RATE * DURATION)

sf.write(
    OUTPUT_FILE,
    data,
    SAMPLE_RATE
)

print()
print(f"Archivo generado: {OUTPUT_FILE}")
print("Prueba finalizada.")