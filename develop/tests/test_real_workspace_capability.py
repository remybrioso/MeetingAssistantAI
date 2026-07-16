from services.configuration_service import (
    ConfigurationService,
)
from services.setup.capabilities.capability_result import (
    CapabilityStatus,
)
from services.setup.capabilities.capability_runner import (
    CapabilityRunner,
)
from services.setup.capabilities.workspace_capability import (
    WorkspaceCapability,
)


configuration = ConfigurationService()

capability = WorkspaceCapability(
    configuration.output_directory
)

result = CapabilityRunner().run(
    capability
)

print("=" * 60)
print("MAI REAL WORKSPACE CAPABILITY")
print("=" * 60)

print()
print(f"Estado: {result.status.value}")
print(f"Mensaje: {result.message}")

print()

for task_result in result.task_results:

    print(
        f"[{task_result.status.value}] "
        f"{task_result.name}"
    )

    print(
        f"  {task_result.message}"
    )

    if task_result.error:
        print(
            f"  Error: {task_result.error}"
        )

assert (
    result.status
    == CapabilityStatus.AVAILABLE
)

assert result.is_available

print()
print(
    "El almacenamiento real de reuniones "
    "está disponible."
)