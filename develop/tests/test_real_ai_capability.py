from providers.ollama_provider import (
    OllamaProvider,
)
from services.setup.capabilities.ai_capability import (
    AICapability,
)
from services.setup.capabilities.capability_result import (
    CapabilityStatus,
)
from services.setup.capabilities.capability_runner import (
    CapabilityRunner,
)


provider = OllamaProvider()

result = CapabilityRunner().run(
    AICapability(provider)
)

print("=" * 60)
print("MAI REAL AI CAPABILITY")
print("=" * 60)

print()
print(f"Estado: {result.status.value}")
print(f"Mensaje: {result.message}")

print()

for key, value in result.details.items():

    print(f"{key}: {value}")

print()

for task_result in result.task_results:

    print(
        f"[{task_result.status.value}] "
        f"{task_result.name}"
    )

    print(
        f"  {task_result.message}"
    )

    if task_result.error:
        print(
            f"  Error: {task_result.error}"
        )

assert (
    result.status
    == CapabilityStatus.AVAILABLE
)

assert result.is_available

print()
print(
    "La capacidad real de inteligencia "
    "artificial está disponible."
)