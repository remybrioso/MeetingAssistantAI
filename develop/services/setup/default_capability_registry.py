"""
default_capability_registry.py

Construye el registro predeterminado de
capacidades funcionales de MAI.
"""

from application.runtime_paths import RuntimePaths
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
from services.setup.capabilities.runtime_resources_capability import (
    RuntimeResourcesCapability,
)
from services.setup.capabilities.transcription_capability import (
    TranscriptionCapability,
)
from services.setup.capabilities.workspace_capability import (
    WorkspaceCapability,
)


def build_default_capability_registry(
    configuration,
    ai_provider=None,
    transcription_model_resolver=None,
) -> CapabilityRegistry:

    registry = CapabilityRegistry()

    provider = (
        ai_provider
        or OllamaProvider()
    )

    runtime_paths = getattr(
        configuration,
        "runtime_paths",
        None,
    )

    if not isinstance(
        runtime_paths,
        RuntimePaths,
    ):
        runtime_paths = (
            RuntimePaths.resolve()
        )

    registry.register(
        RuntimeResourcesCapability(
            runtime_paths=runtime_paths
        )
    )

    registry.register(
        WorkspaceCapability(
            configuration.output_directory
        )
    )

    registry.register(
        TranscriptionCapability(
            model_name=(
                configuration.whisper_model
            ),
            model_resolver=(
                transcription_model_resolver
            ),
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
