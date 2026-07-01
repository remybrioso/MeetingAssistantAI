import time

from engines.audio.audio_session import AudioSession


session = AudioSession()

print("Iniciando...")

session.start()

time.sleep(3)

print(session.duration)

session.pause()

print(session.is_paused)

session.resume()

print(session.is_paused)

session.stop()

print(session.is_recording)

print(session.duration)