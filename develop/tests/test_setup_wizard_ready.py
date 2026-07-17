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
from services.setup.wizard.setup_wizard_result import (
    SetupWizardStatus,
)
from services.setup.wizard.setup_wizard_service import (
    SetupWizardService,
)


class AvailableCapability(Capability):

    def __init__(
        self,
        capability_id,
        name,
    ):

        self.capability_id = capability_id
        self.name = name
        self.description = name

    def get_tasks(self):

        return []

    def evaluate(
        self,
        task_results,
    ):

        return CapabilityResult(
            capability_id=self.capability_id,
            name=self.name,
            status=CapabilityStatus.AVAILABLE,
            message="Capacidad disponible.",
            task_results=task_results,
        )


registry = CapabilityRegistry()

registry.register(
    AvailableCapability(
        "workspace",
        "Almacenamiento",
    )
)

registry.register(
    AvailableCapability(
        "artificial-intelligence",
        "Inteligencia artificial",
    )
)

registry.register(
    AvailableCapability(
        "audio",
        "Audio",
    )
)

service = SetupWizardService(
    capability_registry=registry
)

result = service.run()

assert (
    result.status
    == SetupWizardStatus.READY
)

assert result.is_ready
assert result.can_continue
assert not result.is_blocked

assert (
    result.details[
        "available_count"
    ]
    == 3
)

assert (
    result.details[
        "degraded_count"
    ]
    == 0
)

assert (
    result.details[
        "unavailable_count"
    ]
    == 0
)

print("=" * 60)
print("MAI SETUP WIZARD")
print("=" * 60)

print(f"Estado: {result.status.value}")
print(f"Mensaje: {result.message}")

print()
print(
    "Setup Wizard READY validado."
)