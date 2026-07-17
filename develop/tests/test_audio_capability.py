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


class HealthyAudioService:

    def check(self) -> AudioHealth:

        return AudioHealth(
            microphone_available=True,
            system_audio_available=True,
            microphone_id=3,
            microphone_name="Jabra Evolve 20",
            system_device_name=(
                "Speakers Realtek Audio"
            ),
            system_audio_method=(
                "soundcard-loopback"
            ),
            message="Audio disponible.",
        )


result = CapabilityRunner().run(
    AudioCapability(
        HealthyAudioService()
    )
)

print("=" * 60)
print("MAI AUDIO CAPABILITY")
print("=" * 60)

print(f"Estado: {result.status.value}")
print(f"Mensaje: {result.message}")

assert (
    result.status
    == CapabilityStatus.AVAILABLE
)

assert result.is_available
assert not result.repairable
assert result.repair_action is None

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
    is True
)

print()
print(
    "AudioCapability validada correctamente."
)