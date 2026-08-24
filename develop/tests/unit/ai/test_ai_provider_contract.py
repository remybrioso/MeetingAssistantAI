from models.provider_health import ProviderHealth
from providers.ai_provider import AIProvider


class FakeAIProvider(AIProvider):

    def __init__(self) -> None:
        self.received_prompt = None
        self.received_output_schema = None

    def generate(
        self,
        prompt: str,
        output_schema: dict | None = None,
    ) -> str:
        self.received_prompt = prompt
        self.received_output_schema = (
            output_schema
        )

        return (
            f"Respuesta simulada para: {prompt}"
        )

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            provider="fake",
            connected=True,
            model_found=True,
            model="fake-model",
            response_time_ms=1.0,
            available_models=[
                "fake-model",
            ],
            message="Proveedor disponible.",
            error=None,
        )


def test_generate_returns_simulated_response() -> None:
    provider = FakeAIProvider()

    response = provider.generate(
        "Procesa esta reunión."
    )

    assert response == (
        "Respuesta simulada para: "
        "Procesa esta reunión."
    )

    assert (
        provider.received_prompt
        == "Procesa esta reunión."
    )

    assert (
        provider.received_output_schema
        is None
    )


def test_generate_accepts_output_schema() -> None:
    provider = FakeAIProvider()

    schema = {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
            },
        },
        "required": [
            "title",
        ],
    }

    provider.generate(
        prompt="Procesa esta reunión.",
        output_schema=schema,
    )

    assert (
        provider.received_output_schema
        is schema
    )


def test_health_returns_healthy_provider() -> None:
    provider = FakeAIProvider()

    health = provider.health()

    assert isinstance(
        health,
        ProviderHealth,
    )

    assert health.provider == "fake"
    assert health.connected is True
    assert health.model_found is True
    assert health.model == "fake-model"
    assert health.is_healthy is True
    assert health.error is None