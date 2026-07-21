from models.audio_health import AudioHealth
from services.setup.capabilities.audio_capability import AudioCapability
from services.setup.capabilities.capability_result import CapabilityStatus
from services.setup.capabilities.capability_runner import CapabilityRunner


class HealthyAudioService:

    def check(self) -> AudioHealth:
        return AudioHealth(
            microphone_available=True,
            system_audio_available=True,
            microphone_id=3,
            microphone_name="Jabra Evolve 20",
            system_device_name="Speakers Realtek Audio",
            system_audio_method="soundcard-loopback",
            message="Audio disponible.",
        )


def test_audio_capability_is_available_with_healthy_audio_service() -> None:
    result = CapabilityRunner().run(
        AudioCapability(
            HealthyAudioService()
        )
    )

    assert result.status == CapabilityStatus.AVAILABLE
    assert result.is_available is True
    assert result.repairable is False
    assert result.repair_action is None

    assert result.details["microphone_available"] is True
    assert result.details["system_audio_available"] is True