from models.audio_health import AudioHealth
from services.setup.capabilities.audio_capability import (
    AudioCapability,
)
from services.setup.capabilities.capability_result import (
    CapabilityStatus,
)
from services.setup.capabilities.capability_runner import (
    CapabilityRunner,
)


class NoMicrophoneAudioService:

    def check(self) -> AudioHealth:

        return AudioHealth(
            microphone_available=False,
            system_audio_available=True,
            system_device_name=(
                "Speakers Realtek Audio"
            ),
            system_audio_method=(
                "soundcard-loopback"
            ),
            message=(
                "No se encontró micrófono."
            ),
        )


result = CapabilityRunner().run(
    AudioCapability(
        NoMicrophoneAudioService()
    )
)

assert (
    result.status
    == CapabilityStatus.UNAVAILABLE
)

assert not result.is_available
assert result.repairable

assert (
    result.repair_action
    == "CONFIGURE_MICROPHONE"
)

print(
    "[UNAVAILABLE] Ausencia de micrófono "
    "detectada correctamente."
)

print(
    f"Acción propuesta: "
    f"{result.repair_action}"
)