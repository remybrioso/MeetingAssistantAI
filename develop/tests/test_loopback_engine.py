from engines.audio.loopback_engine import LoopbackEngine


engine = LoopbackEngine()

print("Estado inicial:", engine.is_recording)

engine.start()

print("Grabando:", engine.is_recording)

engine.stop()

print("Detenido:", engine.is_recording)