from providers.ollama_provider import (
    OllamaProvider
)
from services.health.checks.ai_provider_check import (
    AIProviderCheck
)
from services.health.checks.dependency_check import (
    DependencyCheck
)
from services.health.checks.python_check import (
    PythonCheck
)
from services.health.health_service import (
    HealthService
)


provider = OllamaProvider()

service = HealthService(
    checks=[
        PythonCheck(),
        DependencyCheck(),
        AIProviderCheck(provider),
    ]
)

results = service.run_all()

print("=" * 60)
print("MAI HEALTH REPORT")
print("=" * 60)

for result in results:

    print()
    print(
        f"[{result.status.value}] "
        f"{result.name}"
    )

    print(result.message)

    if result.details:

        for key, value in result.details.items():

            print(
                f"  {key}: {value}"
            )

print()

if service.is_ready(results):

    print("READY FOR USE")

else:

    print("SYSTEM REQUIRES ATTENTION")