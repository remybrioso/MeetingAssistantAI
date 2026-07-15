from mai_config.ai_config import (
    OLLAMA_MODEL,
    OLLAMA_URL,
)
from providers.ollama_provider import (
    OllamaProvider
)


provider = OllamaProvider()

result = provider.health()

print("=" * 60)
print("OLLAMA PROVIDER HEALTH")
print("=" * 60)

print(f"Proveedor: {result.provider}")
print(f"URL: {OLLAMA_URL}")
print(f"Modelo esperado: {OLLAMA_MODEL}")
print(f"Conectado: {result.connected}")
print(f"Modelo encontrado: {result.model_found}")
print(
    f"Tiempo de respuesta: "
    f"{result.response_time_ms} ms"
)
print(
    f"Modelos disponibles: "
    f"{result.available_models}"
)
print(f"Mensaje: {result.message}")

if result.error:
    print(f"Error: {result.error}")

assert result.provider == "Ollama"
assert result.model == OLLAMA_MODEL
assert result.response_time_ms is not None

print()
print(
    "Diagnóstico del proveedor ejecutado "
    "sin propagar excepciones."
)