from services.setup.capabilities.capability import (
    Capability,
)
from services.setup.capabilities.capability_result import (
    CapabilityStatus,
)
from services.setup.capabilities.capability_runner import (
    CapabilityRunner,
)


class BrokenCapability(Capability):

    capability_id = "broken"
    name = "Capacidad defectuosa"

    def get_tasks(self) -> list:

        raise RuntimeError(
            "Fallo simulado al crear las tareas."
        )

    def evaluate(self, task_results):

        raise AssertionError(
            "No debería evaluarse."
        )


runner = CapabilityRunner()

result = runner.run(
    BrokenCapability()
)

assert (
    result.status
    == CapabilityStatus.UNAVAILABLE
)

assert "error" in result.details

print(
    "CapabilityRunner convirtió correctamente "
    "la excepción en UNAVAILABLE."
)