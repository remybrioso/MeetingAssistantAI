from services.setup.capabilities.ai_capability import (
    AICapability,
)
from services.setup.capabilities.capability_result import (
    CapabilityStatus,
)
from services.setup.capabilities.capability_runner import (
    CapabilityRunner,
)


class BrokenProvider:

    def health(self):

        raise RuntimeError(
            "Fallo simulado del proveedor."
        )


result = CapabilityRunner().run(
    AICapability(
        BrokenProvider()
    )
)

assert (
    result.status
    == CapabilityStatus.UNAVAILABLE
)

assert result.repairable

assert (
    result.repair_action
    == "INSTALL_AI_PROVIDER"
)

assert len(result.task_results) == 1

assert (
    "Fallo simulado"
    in result.task_results[0].error
)

print(
    "El fallo del proveedor fue convertido "
    "correctamente en UNAVAILABLE."
)