from services.health.ollama_health_service import (
    OllamaHealthService
)

service = OllamaHealthService()

status = service.check()

print(status)

assert status["available"]

assert "qwen2.5:3b" in status["models"]

print()
print("Health Service validado.")