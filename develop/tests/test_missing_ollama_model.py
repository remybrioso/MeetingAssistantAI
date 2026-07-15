from providers.ollama_provider import OllamaProvider


provider = OllamaProvider(
    model="modelo-inexistente:latest"
)

result = provider.health()

print("=" * 60)
print("MISSING OLLAMA MODEL TEST")
print("=" * 60)

print(f"Conectado: {result.connected}")
print(f"Modelo encontrado: {result.model_found}")
print(f"Mensaje: {result.message}")

if result.error:
    print(f"Error: {result.error}")

assert result.connected is True
assert result.model_found is False

print()
print("Modelo inexistente detectado correctamente.")