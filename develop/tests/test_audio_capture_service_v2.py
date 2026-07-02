import time
import os

from application.dependency_container import container

service = container.get("audio_capture_service")

print()

print("Grabando durante 5 segundos...")

service.start()

time.sleep(5)

service.stop()

print()

print("Estado:", service.session.state)

archivo = os.path.join(
    "output",
    "meeting.wav"
)

print("Archivo existe:", os.path.exists(archivo))

assert os.path.exists(archivo)

print()

print("Prueba satisfactoria.")