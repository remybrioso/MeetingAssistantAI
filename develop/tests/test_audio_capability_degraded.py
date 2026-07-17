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


class MicrophoneOnlyAudioService:

    def check(self) -> AudioHealth:

        return AudioHealth(
            microphone_available=True,
            system_audio_available=False,
            microphone_id=2,
            microphone_name="USB Microphone",
            system_audio_method=(
                "soundcard-loopback"
            ),
            message=(
                "Audio del sistema no disponible."
            ),
            error=(
                "No se encontró un dispositivo "
                "loopback."
            ),
        )


result = CapabilityRunner().run(
    AudioCapability(
        MicrophoneOnlyAudioService()
    )
)

assert (
    result.status
    == CapabilityStatus.DEGRADED
)

assert not result.is_available
assert result.repairable

assert (
    result.repair_action
    == "CONFIGURE_SYSTEM_AUDIO"
)

assert (
    result.details[
        "microphone_available"
    ]
    is True
)

assert (
    result.details[
        "system_audio_available"
    ]
    is False
)

print(
    "[DEGRADED] Micrófono disponible, "
    "pero sin audio del sistema."
)

print(
    f"Acción propuesta: "
    f"{result.repair_action}"
)