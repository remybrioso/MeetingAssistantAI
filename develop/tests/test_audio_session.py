import time

from engines.audio.audio_session import AudioSession
from models.recording_state import RecordingState


session = AudioSession()

print("Estado inicial:", session.state)

session.start()

print("Después de iniciar:", session.state)

time.sleep(2)

session.pause()

print("Después de pausar:", session.state)

time.sleep(1)

session.resume()

print("Después de reanudar:", session.state)

time.sleep(2)

session.stop()

print("Después de finalizar:", session.state)

print("Duración:", session.duration)

assert session.state == RecordingState.FINISHED

print("\nPrueba satisfactoria.")