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
from services.setup.wizard.setup_wizard_service import (
    SetupWizardService,
)


class FakeEventBus:

    def __init__(self):

        self.events = []

    def emit(
        self,
        event_name,
        *args,
    ):

        self.events.append(
            (
                event_name,
                args,
            )
        )


class AvailableCapability(Capability):

    capability_id = "workspace"
    name = "Almacenamiento"
    description = "Almacenamiento"

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
            message="Disponible.",
            task_results=task_results,
        )


event_bus = FakeEventBus()

registry = CapabilityRegistry()

registry.register(
    AvailableCapability()
)

service = SetupWizardService(
    capability_registry=registry,
    event_bus=event_bus,
)

result = service.run()

event_names = [
    event_name
    for event_name, _
    in event_bus.events
]

assert (
    "setup_wizard_started"
    in event_names
)

assert (
    "setup_wizard_capability_started"
    in event_names
)

assert (
    "setup_wizard_capability_completed"
    in event_names
)

assert (
    "setup_wizard_completed"
    in event_names
)

assert result.is_ready

print(
    "Los eventos del Setup Wizard "
    "fueron emitidos correctamente."
)