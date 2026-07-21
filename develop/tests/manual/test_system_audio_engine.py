from engines.audio.system_audio_engine import SystemAudioEngine


engine = SystemAudioEngine()

print()
print("Reproduce audio en Windows antes de continuar.")
input("Presiona Enter para grabar 10 segundos...")

engine.record(
    filename="output/system_engine.wav",
    duration=10
)

print()
print("Archivo generado: output/system_engine.wav")
print("Prueba finalizada.")