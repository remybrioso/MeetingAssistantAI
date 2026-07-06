from providers.whisper.whisper_configuration import WhisperConfiguration


config = WhisperConfiguration()

print(config.as_dict())

assert config.model == "base"
assert config.language == "es"
assert config.device == "cpu"
assert config.compute_type == "int8"
assert config.beam_size == 5

print()
print("Prueba satisfactoria.")