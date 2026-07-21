import os
import time

import sounddevice as sd
import soundfile as sf


OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "system.wav")

DURATION = 10
CHANNELS = 2

os.makedirs(OUTPUT_DIR, exist_ok=True)

devices = sd.query_devices()

print()
print("===== SYSTEM AUDIO CANDIDATES =====")
print()

candidates = []

for index, device in enumerate(devices):
    name = device["name"].lower()

    if (
        "stereo mix" in name
        or "what u hear" in name
        or "loopback" in name
    ):
        candidates.append((index, device))
        print(f"{len(candidates) - 1}: [{index}] {device['name']}")
        print(f"   Input Channels: {device['max_input_channels']}")
        print(f"   Sample Rate: {device['default_samplerate']}")
        print()

if not candidates:
    raise RuntimeError(
        "No se encontró Stereo Mix ni dispositivo Loopback. "
        "En este equipo habría que usar WASAPI nativo o VB-Cable."
    )

selection = int(input("Seleccione dispositivo de audio del sistema: "))

device_id, device_info = candidates[selection]

samplerate = int(device_info["default_samplerate"])
channels = min(int(device_info["max_input_channels"]), CHANNELS)

print()
print("Reproduce audio en Windows ahora.")
print(f"Grabando audio del sistema durante {DURATION} segundos...")
print()

data = sd.rec(
    int(DURATION * samplerate),
    samplerate=samplerate,
    channels=channels,
    dtype="float32",
    device=device_id
)

sd.wait()

sf.write(
    OUTPUT_FILE,
    data,
    samplerate
)

print()
print(f"Archivo generado: {OUTPUT_FILE}")
print("Prueba finalizada.")