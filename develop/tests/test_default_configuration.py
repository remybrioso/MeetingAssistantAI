from application.dependency_container import container

config = container.get("configuration")

print()

print("===== CONFIGURACIÓN =====")

print()

print("Micrófono:", config.microphone)

print("Sistema:", config.system_device)

print("Output:", config.output_directory)

print("Sample Rate:", config.sample_rate)

print("Canales:", config.channels)

assert config.microphone is not None

print()

print("Prueba satisfactoria.")