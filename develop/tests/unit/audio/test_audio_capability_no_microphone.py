from models.audio_health import AudioHealth
from services.setup.capabilities.audio_capability import AudioCapability
from services.setup.capabilities.capability_result import CapabilityStatus
from services.setup.capabilities.capability_runner import CapabilityRunner


class NoMicrophoneAudioService:

    def check(self) -> AudioHealth:
        return AudioHealth(
            microphone_available=False,
            system_audio_available=True,
            system_device_name="Speakers Realtek Audio",
            system_audio_method="soundcard-loopback",
            message="No se encontró micrófono.",
        )


def test_audio_capability_is_unavailable_without_microphone() -> None:
    result = CapabilityRunner().run(
        AudioCapability(
            NoMicrophoneAudioService()
        )
    )

    assert result.status == CapabilityStatus.UNAVAILABLE
    assert result.is_available is False
    assert result.repairable is True
    assert result.repair_action == "CONFIGURE_MICROPHONE"

    assert result.details["microphone_available"] is False
    assert result.details["system_audio_available"] is True