from services.setup.capabilities.capability import (
    Capability,
)
from services.setup.capabilities.capability_registry import (
    CapabilityRegistry,
)
from services.setup.capabilities.capability_result import (
    CapabilityResult,
    CapabilityStatus,
)


class DuplicateCapability(Capability):

    capability_id = "duplicate"
    name = "Capacidad duplicada"

    def get_tasks(self) -> list:
        return []

    def evaluate(
        self,
        task_results
    ) -> CapabilityResult:

        return CapabilityResult(
            capability_id=self.capability_id,
            name=self.name,
            status=CapabilityStatus.AVAILABLE,
            message="Disponible.",
        )


registry = CapabilityRegistry()

registry.register(
    DuplicateCapability()
)

try:
    registry.register(
        DuplicateCapability()
    )

    raise AssertionError(
        "El registro permitió un ID duplicado."
    )

except ValueError as ex:

    assert "Ya existe" in str(ex)

    print(
        "El CapabilityRegistry rechazó "
        "correctamente un ID duplicado."
    )