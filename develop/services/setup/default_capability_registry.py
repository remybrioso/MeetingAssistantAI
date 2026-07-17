"""
default_capability_registry.py

Construye el registro predeterminado de
capacidades funcionales de MAI.
"""

from providers.ollama_provider import (
    OllamaProvider,
)
from services.setup.capabilities.ai_capability import (
    AICapability,
)
from services.setup.capabilities.audio_capability import (
    AudioCapability,
)
from services.setup.capabilities.capability_registry import (
    CapabilityRegistry,
)
from services.setup.capabilities.workspace_capability import (
    WorkspaceCapability,
)


def build_default_capability_registry(
    configuration,
    ai_provider=None,
) -> CapabilityRegistry:

    registry = CapabilityRegistry()

    provider = (
        ai_provider
        or OllamaProvider()
    )

    registry.register(
        WorkspaceCapability(
            configuration.output_directory
        )
    )

    registry.register(
        AICapability(
            provider
        )
    )

    registry.register(
        AudioCapability()
    )

    return registry