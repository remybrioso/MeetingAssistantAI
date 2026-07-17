from application.dependency_container import (
    container,
)
from services.setup.capabilities.capability_registry import (
    CapabilityRegistry,
)
from services.setup.capabilities.capability_runner import (
    CapabilityRunner,
)
from services.setup.wizard.setup_wizard_service import (
    SetupWizardService,
)


registry = container.get(
    "capability_registry"
)

runner = container.get(
    "capability_runner"
)

wizard = container.get(
    "setup_wizard_service"
)

assert isinstance(
    registry,
    CapabilityRegistry,
)

assert isinstance(
    runner,
    CapabilityRunner,
)

assert isinstance(
    wizard,
    SetupWizardService,
)

assert len(registry) == 3

assert (
    registry.get("workspace")
    is not None
)

assert (
    registry.get(
        "artificial-intelligence"
    )
    is not None
)

assert (
    registry.get("audio")
    is not None
)

print(
    "Las dependencias del Setup Wizard "
    "están registradas correctamente."
)