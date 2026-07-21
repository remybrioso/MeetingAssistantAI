import os
import time

from services.audio_capture_service import AudioCaptureService
from engines.audio.device_manager import DeviceManager

OUTPUT = "output"

os.makedirs(OUTPUT, exist_ok=True)

manager = DeviceManager()

microphones = manager.get_microphones()

print("\n===== MICRÓFONOS =====\n")

for i, mic in enumerate(microphones):
    print(f"{i}: {mic.name}")

index = int(input("\nSeleccione un micrófono: "))

device = microphones[index]

service = AudioCaptureService()

print("\nGrabando durante 5 segundos...")

service.start(
    device_id=device.id,
    filename=os.path.join(
        OUTPUT,
        "meeting_test.wav"
    )
)

time.sleep(5)

service.stop()

print()

print("Estado final:", service.session.state)

print("Duración:", service.session.duration)

print()

print("Prueba finalizada correctamente.")