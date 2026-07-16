from pathlib import Path

from services.configuration_service import (
    ConfigurationService,
)
from services.setup.setup_engine import SetupEngine
from services.setup.tasks.initialize_output_directory_task import (
    InitializeOutputDirectoryTask,
)
from services.setup.tasks.verify_temporary_workspace_task import (
    VerifyTemporaryWorkspaceTask,
)


configuration = ConfigurationService()

output_directory = Path(
    configuration.output_directory
)

engine = SetupEngine(
    tasks=[
        InitializeOutputDirectoryTask(
            output_directory
        ),
        VerifyTemporaryWorkspaceTask(
            output_directory
        ),
    ]
)

result = engine.run()

print("=" * 60)
print("MAI REAL WORKSPACE VERIFICATION")
print("=" * 60)

for task_result in result.task_results:

    print()
    print(
        f"[{task_result.status.value}] "
        f"{task_result.name}"
    )

    print(task_result.message)

    for key, value in (
        task_result.details.items()
    ):

        print(f"  {key}: {value}")

    if task_result.error:
        print(
            f"  error: {task_result.error}"
        )

assert result.successful

residual_directories = list(
    output_directory.glob(
        ".mai_workspace_test_*"
    )
)

assert residual_directories == []

print()
print(
    "El Workspace real fue validado "
    "sin dejar residuos."
)