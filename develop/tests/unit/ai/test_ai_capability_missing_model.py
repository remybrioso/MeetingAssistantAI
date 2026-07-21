from models.provider_health import ProviderHealth
from services.setup.capabilities.ai_capability import AICapability
from services.setup.capabilities.capability_result import CapabilityStatus
from services.setup.capabilities.capability_runner import CapabilityRunner


class ProviderWithoutModel:

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            provider="Ollama",
            connected=True,
            model_found=False,
            model="qwen2.5:3b",
            response_time_ms=20.0,
            available_models=["otro-modelo:latest"],
            message="Modelo no instalado.",
        )


def test_ai_capability_returns_unavailable_when_model_is_missing() -> None:
    result = CapabilityRunner().run(
        AICapability(
            ProviderWithoutModel()
        )
    )

    assert result.status == CapabilityStatus.UNAVAILABLE
    assert result.repairable is True
    assert result.repair_action == "DOWNLOAD_AI_MODEL"
    assert result.details["connected"] is True
    assert result.details["model_found"] is False