from services.configuration_service import (
    ConfigurationService,
)
from services.setup.setup_engine import SetupEngine
from services.setup.tasks.initialize_output_directory_task import (
    InitializeOutputDirectoryTask,
)


configuration = ConfigurationService()

task = InitializeOutputDirectoryTask(
    configuration.output_directory
)

engine = SetupEngine(
    tasks=[task]
)

result = engine.run()

task_result = result.task_results[0]

print("=" * 60)
print("MAI OUTPUT DIRECTORY SETUP")
print("=" * 60)

print(
    f"Estado: {task_result.status.value}"
)

print(
    f"Mensaje: {task_result.message}"
)

for key, value in task_result.details.items():
    print(f"{key}: {value}")

if task_result.error:
    print(f"Error: {task_result.error}")

assert result.successful

print()
print(
    "La carpeta real de reuniones está disponible."
)