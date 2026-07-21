from models.provider_health import ProviderHealth
from providers.ai_provider import AIProvider


class FakeAIProvider(AIProvider):

    def generate(self, prompt: str) -> str:
        return f"Respuesta simulada para: {prompt}"

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            provider="fake",
            connected=True,
            model_found=True,
            model="fake-model",
            response_time_ms=1.0,
            available_models=["fake-model"],
            message="Proveedor disponible.",
            error=None,
        )


def test_generate_returns_simulated_response() -> None:
    provider = FakeAIProvider()

    response = provider.generate(
        "Resume esta reunión."
    )

    assert response == "Respuesta simulada para: Resume esta reunión."


def test_health_returns_healthy_provider() -> None:
    provider = FakeAIProvider()

    health = provider.health()

    assert isinstance(health, ProviderHealth)
    assert health.provider == "fake"
    assert health.connected is True
    assert health.model_found is True
    assert health.model == "fake-model"
    assert health.is_healthy is True
    assert health.error is None