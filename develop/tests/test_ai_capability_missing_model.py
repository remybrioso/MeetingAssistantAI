from models.provider_health import (
    ProviderHealth,
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


class ProviderWithoutModel:

    def health(self) -> ProviderHealth:

        return ProviderHealth(
            provider="Ollama",
            connected=True,
            model_found=False,
            model="qwen2.5:3b",
            response_time_ms=20.0,
            available_models=[
                "otro-modelo:latest"
            ],
            message=(
                "Modelo no instalado."
            ),
        )


result = CapabilityRunner().run(
    AICapability(
        ProviderWithoutModel()
    )
)

assert (
    result.status
    == CapabilityStatus.UNAVAILABLE
)

assert result.repairable

assert (
    result.repair_action
    == "DOWNLOAD_AI_MODEL"
)

assert (
    result.details["connected"]
    is True
)

assert (
    result.details["model_found"]
    is False
)

print(
    "[UNAVAILABLE] Modelo ausente "
    "detectado correctamente."
)

print(
    f"Acción propuesta: "
    f"{result.repair_action}"
)