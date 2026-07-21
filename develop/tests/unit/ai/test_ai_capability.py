from models.provider_health import ProviderHealth
from services.setup.capabilities.ai_capability import AICapability
from services.setup.capabilities.capability_result import CapabilityStatus
from services.setup.capabilities.capability_runner import CapabilityRunner
from services.setup.task_result import TaskStatus


class HealthyProvider:

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            provider="Proveedor simulado",
            connected=True,
            model_found=True,
            model="modelo-prueba",
            response_time_ms=12.5,
            available_models=["modelo-prueba"],
            message="Proveedor disponible.",
        )


def test_ai_capability_is_available_with_healthy_provider() -> None:
    result = CapabilityRunner().run(
        AICapability(HealthyProvider())
    )

    assert result.status == CapabilityStatus.AVAILABLE
    assert result.is_available is True
    assert result.repairable is False
    assert result.repair_action is None
    assert len(result.task_results) == 1
    assert result.task_results[0].status == TaskStatus.SUCCESS
    assert result.details["connected"] is True
    assert result.details["model_found"] is True
