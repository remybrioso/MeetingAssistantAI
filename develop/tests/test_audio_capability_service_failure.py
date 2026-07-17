from services.setup.capabilities.audio_capability import (
    AudioCapability,
)
from services.setup.capabilities.capability_result import (
    CapabilityStatus,
)
from services.setup.capabilities.capability_runner import (
    CapabilityRunner,
)


class BrokenAudioService:

    def check(self):

        raise RuntimeError(
            "Fallo simulado de PortAudio."
        )


result = CapabilityRunner().run(
    AudioCapability(
        BrokenAudioService()
    )
)

assert (
    result.status
    == CapabilityStatus.UNAVAILABLE
)

assert result.repairable

assert (
    result.repair_action
    == "CONFIGURE_MICROPHONE"
)

assert len(result.task_results) == 1

assert (
    "PortAudio"
    in result.task_results[0].error
)

print(
    "El fallo del servicio de audio fue "
    "convertido en UNAVAILABLE."
)