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


class FixedCapability(Capability):

    def __init__(
        self,
        capability_id,
        status,
        repair_action=None,
    ):

        self.capability_id = capability_id
        self.name = capability_id
        self.description = capability_id
        self._status = status
        self._repair_action = repair_action

    def get_tasks(self):

        return []

    def evaluate(
        self,
        task_results,
    ):

        return CapabilityResult(
            capability_id=self.capability_id,
            name=self.name,
            status=self._status,
            message="Resultado simulado.",
            task_results=task_results,
            repairable=(
                self._repair_action
                is not None
            ),
            repair_action=(
                self._repair_action
            ),
        )


registry = CapabilityRegistry()

registry.register(
    FixedCapability(
        "workspace",
        CapabilityStatus.AVAILABLE,
    )
)

registry.register(
    FixedCapability(
        "artificial-intelligence",
        CapabilityStatus.UNAVAILABLE,
        "DOWNLOAD_AI_MODEL",
    )
)

registry.register(
    FixedCapability(
        "audio",
        CapabilityStatus.AVAILABLE,
    )
)

result = SetupWizardService(
    capability_registry=registry
).run()

assert (
    result.status
    == SetupWizardStatus.BLOCKED
)

assert result.is_blocked
assert not result.can_continue

assert len(
    result.get_unavailable()
) == 1

assert len(
    result.get_repairable()
) == 1

ai_result = result.get_capability(
    "artificial-intelligence"
)

assert ai_result is not None

assert (
    ai_result.repair_action
    == "DOWNLOAD_AI_MODEL"
)

print(
    "[BLOCKED] Modelo de IA ausente "
    "detectado correctamente."
)