from application.dependency_container import container

config = container.get("configuration")

print("Configuración inicial")

print()

print("Micrófono:", config.microphone)
print("Salida:", config.system_device)
print("Output:", config.output_directory)
print("Sample Rate:", config.sample_rate)
print("Canales:", config.channels)
print("Idioma:", config.language)
print("Modelo:", config.whisper_model)

print()

config.microphone = 17

config.system_device = 15

print("Nueva configuración")

print()

print("Micrófono:", config.microphone)
print("Salida:", config.system_device)

assert config.microphone == 17
assert config.system_device == 15

print()

print("Prueba satisfactoria.")