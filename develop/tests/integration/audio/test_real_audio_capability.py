import pytest

from services.setup.capabilities.audio_capability import AudioCapability
from services.setup.capabilities.capability_result import CapabilityStatus
from services.setup.capabilities.capability_runner import CapabilityRunner


@pytest.mark.integration
def test_real_audio_capability_is_available() -> None:

    result = CapabilityRunner().run(
        AudioCapability()
    )

    if result.status == CapabilityStatus.UNAVAILABLE:
        pytest.skip(
            "No hay hardware de audio disponible para esta prueba."
        )

    assert result.status in {
        CapabilityStatus.AVAILABLE,
        CapabilityStatus.DEGRADED,
    }

    assert result.details["microphone_available"] is True