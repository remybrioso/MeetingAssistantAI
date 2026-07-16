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
from services.setup.capabilities.capability_runner import (
    CapabilityRunner,
)
from services.setup.setup_task import SetupTask
from services.setup.task_result import (
    TaskResult,
    TaskStatus,
)


class SuccessfulTask(SetupTask):

    task_id = "successful-task"
    name = "Tarea correcta"

    def should_run(self) -> bool:
        return True

    def run(self) -> TaskResult:

        return TaskResult(
            task_id=self.task_id,
            name=self.name,
            status=TaskStatus.SUCCESS,
            message="Tarea completada.",
        )


class DemoCapability(Capability):

    capability_id = "demo"
    name = "Capacidad de demostración"
    description = (
        "Valida el Capability Framework."
    )

    def get_tasks(self) -> list:

        return [
            SuccessfulTask(),
        ]

    def evaluate(
        self,
        task_results
    ) -> CapabilityResult:

        all_successful = all(
            result.is_successful
            for result in task_results
        )

        status = (
            CapabilityStatus.AVAILABLE
            if all_successful
            else CapabilityStatus.UNAVAILABLE
        )

        return CapabilityResult(
            capability_id=self.capability_id,
            name=self.name,
            status=status,
            message=(
                "La capacidad está disponible."
                if all_successful
                else "La capacidad no está disponible."
            ),
            task_results=task_results,
        )


registry = CapabilityRegistry()

capability = DemoCapability()

registry.register(capability)

assert len(registry) == 1

assert registry.get("demo") is capability

runner = CapabilityRunner()

result = runner.run(
    registry.get("demo")
)

print("=" * 60)
print("MAI CAPABILITY FRAMEWORK")
print("=" * 60)

print(f"Capacidad: {result.name}")
print(f"Estado: {result.status.value}")
print(f"Mensaje: {result.message}")

for task_result in result.task_results:

    print(
        f"[{task_result.status.value}] "
        f"{task_result.name}"
    )

assert (
    result.status
    == CapabilityStatus.AVAILABLE
)

assert result.is_available
assert len(result.task_results) == 1

print()
print(
    "Capability Framework validado."
)