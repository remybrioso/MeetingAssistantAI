import os
import time

from application.dependency_container import container
from engines.audio.microphone_engine import MicrophoneEngine

config = container.get("configuration")

engine = MicrophoneEngine()

filename = os.path.join(
    config.output_directory,
    "microphone_engine.wav"
)

print("Grabando durante 5 segundos...")

engine.start(
    device_id=config.microphone,
    filename=filename,
    samplerate=config.sample_rate,
    channels=config.channels
)

time.sleep(5)

engine.stop()

print("Prueba satisfactoria.")