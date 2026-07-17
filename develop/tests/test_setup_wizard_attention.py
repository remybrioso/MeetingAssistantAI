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
    ):

        self.capability_id = capability_id
        self.name = capability_id
        self.description = capability_id
        self._status = status

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
                self._status
                != CapabilityStatus.AVAILABLE
            ),
            repair_action=(
                "CONFIGURE_SYSTEM_AUDIO"
                if (
                    self._status
                    == CapabilityStatus.DEGRADED
                )
                else None
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
        CapabilityStatus.AVAILABLE,
    )
)

registry.register(
    FixedCapability(
        "audio",
        CapabilityStatus.DEGRADED,
    )
)

result = SetupWizardService(
    capability_registry=registry
).run()

assert (
    result.status
    == SetupWizardStatus.ATTENTION
)

assert result.can_continue
assert result.has_attention_items
assert not result.is_ready
assert not result.is_blocked

assert (
    result.details[
        "degraded_count"
    ]
    == 1
)

assert len(
    result.get_degraded()
) == 1

assert len(
    result.get_repairable()
) == 1

print(
    "[ATTENTION] Setup Wizard permite "
    "continuar con audio degradado."
)