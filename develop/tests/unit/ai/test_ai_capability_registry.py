from models.provider_health import ProviderHealth
from services.setup.capabilities.ai_capability import AICapability
from services.setup.capabilities.capability_registry import CapabilityRegistry
from services.setup.capabilities.capability_result import CapabilityStatus
from services.setup.capabilities.capability_runner import CapabilityRunner


class HealthyProvider:

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            provider="Proveedor simulado",
            connected=True,
            model_found=True,
            model="modelo-prueba",
            response_time_ms=10.0,
            available_models=["modelo-prueba"],
            message="Proveedor disponible.",
        )


def test_ai_capability_can_be_registered_and_executed() -> None:

    registry = CapabilityRegistry()

    registry.register(
        AICapability(
            HealthyProvider()
        )
    )

    assert len(registry) == 1

    capability = registry.get(
        "artificial-intelligence"
    )

    assert capability is not None

    result = CapabilityRunner().run(
        capability
    )

    assert result.status == CapabilityStatus.AVAILABLE