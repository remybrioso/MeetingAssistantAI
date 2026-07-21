from models.audio_health import AudioHealth
from services.setup.capabilities.audio_capability import AudioCapability
from services.setup.capabilities.capability_result import CapabilityStatus
from services.setup.capabilities.capability_runner import CapabilityRunner


class MicrophoneOnlyAudioService:

    def check(self) -> AudioHealth:
        return AudioHealth(
            microphone_available=True,
            system_audio_available=False,
            microphone_id=2,
            microphone_name="USB Microphone",
            system_audio_method="soundcard-loopback",
            message="Audio del sistema no disponible.",
            error="No se encontró un dispositivo loopback.",
        )


def test_audio_capability_is_degraded_without_system_audio() -> None:
    result = CapabilityRunner().run(
        AudioCapability(
            MicrophoneOnlyAudioService()
        )
    )

    assert result.status == CapabilityStatus.DEGRADED
    assert result.is_available is False
    assert result.repairable is True
    assert result.repair_action == "CONFIGURE_SYSTEM_AUDIO"

    assert result.details["microphone_available"] is True
    assert result.details["system_audio_available"] is False