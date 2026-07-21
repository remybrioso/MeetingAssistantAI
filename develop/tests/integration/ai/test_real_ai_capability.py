import pytest

from providers.ollama_provider import OllamaProvider
from services.setup.capabilities.ai_capability import AICapability
from services.setup.capabilities.capability_result import CapabilityStatus
from services.setup.capabilities.capability_runner import CapabilityRunner


@pytest.mark.integration
def test_real_ai_capability_is_available() -> None:
    provider = OllamaProvider()

    result = CapabilityRunner().run(
        AICapability(provider)
    )

    if result.status != CapabilityStatus.AVAILABLE:
        pytest.skip(
            f"Ollama o el modelo no están disponibles: {result.message}"
        )

    assert result.is_available is True
    assert result.status == CapabilityStatus.AVAILABLE