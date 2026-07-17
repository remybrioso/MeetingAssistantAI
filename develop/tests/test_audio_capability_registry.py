from models.audio_health import AudioHealth
from services.setup.capabilities.audio_capability import (
    AudioCapability,
)
from services.setup.capabilities.capability_registry import (
    CapabilityRegistry,
)
from services.setup.capabilities.capability_result import (
    CapabilityStatus,
)
from services.setup.capabilities.capability_runner import (
    CapabilityRunner,
)


class HealthyAudioService:

    def check(self) -> AudioHealth:

        return AudioHealth(
            microphone_available=True,
            system_audio_available=True,
        )


registry = CapabilityRegistry()

registry.register(
    AudioCapability(
        HealthyAudioService()
    )
)

assert len(registry) == 1

capability = registry.get(
    "audio"
)

assert capability is not None

result = CapabilityRunner().run(
    capability
)

assert (
    result.status
    == CapabilityStatus.AVAILABLE
)

print(
    "AudioCapability registrada y "
    "ejecutada correctamente."
)