import time
import os

from engines.audio.recorder import AudioRecorder
from engines.audio.device_manager import DeviceManager


OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

manager = DeviceManager()

microphones = manager.get_microphones()

print("\n===== MICRÓFONOS =====\n")

for index, mic in enumerate(microphones):
    print(f"{index}: {mic.name}")

selection = int(input("\nSeleccione el micrófono: "))

device = microphones[selection]

recorder = AudioRecorder()

print("\nGrabando durante 10 segundos...")

recorder.start(
    device_id=device.id,
    filename=os.path.join(OUTPUT_DIR, "mic_test.wav")
)

time.sleep(10)

recorder.stop()

print("\nArchivo generado correctamente.")