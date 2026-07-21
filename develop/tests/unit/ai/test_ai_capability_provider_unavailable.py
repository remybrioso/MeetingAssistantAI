from models.provider_health import ProviderHealth
from services.setup.capabilities.ai_capability import AICapability
from services.setup.capabilities.capability_result import CapabilityStatus
from services.setup.capabilities.capability_runner import CapabilityRunner


class UnavailableProvider:

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            provider="Ollama",
            connected=False,
            model_found=False,
            model="qwen2.5:3b",
            response_time_ms=3000,
            available_models=[],
            message="No fue posible conectar.",
            error="Connection refused.",
        )


def test_ai_capability_returns_unavailable_when_provider_is_offline() -> None:
    result = CapabilityRunner().run(
        AICapability(
            UnavailableProvider()
        )
    )

    assert result.status == CapabilityStatus.UNAVAILABLE
    assert result.is_available is False
    assert result.repairable is True
    assert result.repair_action == "INSTALL_AI_PROVIDER"
    assert result.details["connected"] is False
    assert result.details["model_found"] is False