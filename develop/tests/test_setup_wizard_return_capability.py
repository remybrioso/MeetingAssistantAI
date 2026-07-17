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


class CountingCapability(Capability):

    capability_id = "workspace"
    name = "Almacenamiento"
    description = "Almacenamiento"

    def __init__(self):

        self.execution_count = 0

    def get_tasks(self):

        return []

    def evaluate(
        self,
        task_results,
    ):

        self.execution_count += 1

        return CapabilityResult(
            capability_id=self.capability_id,
            name=self.name,
            status=CapabilityStatus.AVAILABLE,
            message="Disponible.",
            task_results=task_results,
            details={
                "execution_count": (
                    self.execution_count
                )
            },
        )


registry = CapabilityRegistry()

capability = CountingCapability()

registry.register(capability)

service = SetupWizardService(
    capability_registry=registry
)

first_result = (
    service.rerun_capability(
        "workspace"
    )
)

second_result = (
    service.rerun_capability(
        "workspace"
    )
)

assert (
    first_result.details[
        "execution_count"
    ]
    == 1
)

assert (
    second_result.details[
        "execution_count"
    ]
    == 2
)

try:
    service.rerun_capability(
        "does-not-exist"
    )

except KeyError as ex:

    assert (
        "does-not-exist"
        in str(ex)
    )

else:
    raise AssertionError(
        "Se esperaba KeyError."
    )

print(
    "La repetición individual de capacidades "
    "fue validada."
)