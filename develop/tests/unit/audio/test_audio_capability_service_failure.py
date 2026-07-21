from services.setup.capabilities.audio_capability import AudioCapability
from services.setup.capabilities.capability_result import CapabilityStatus
from services.setup.capabilities.capability_runner import CapabilityRunner


class BrokenAudioService:

    def check(self):
        raise RuntimeError(
            "Fallo simulado de PortAudio."
        )


def test_audio_capability_returns_unavailable_when_service_fails() -> None:
    result = CapabilityRunner().run(
        AudioCapability(
            BrokenAudioService()
        )
    )

    assert result.status == CapabilityStatus.UNAVAILABLE
    assert result.is_available is False
    assert result.repairable is True
    assert result.repair_action == "CONFIGURE_MICROPHONE"

    assert len(result.task_results) == 1
    assert "PortAudio" in result.task_results[0].error