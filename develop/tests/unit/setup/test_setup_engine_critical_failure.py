from services.setup.setup_engine import SetupEngine
from services.setup.setup_task import SetupTask
from services.setup.task_result import TaskResult, TaskStatus


class CriticalFailedTask(SetupTask):

    task_id = "critical-failure"
    name = "Fallo crítico"
    critical = True

    def should_run(self) -> bool:
        return True

    def run(self) -> TaskResult:
        return TaskResult(
            task_id=self.task_id,
            name=self.name,
            status=TaskStatus.FAILED,
            message="Fallo crítico simulado.",
        )


class TaskThatMustNotRun(SetupTask):

    task_id = "must-not-run"
    name = "No debe ejecutarse"

    def should_run(self) -> bool:
        return True

    def run(self) -> TaskResult:
        raise AssertionError(
            "El motor no detuvo el flujo."
        )


def test_setup_engine_stops_after_critical_failure() -> None:
    engine = SetupEngine(
        tasks=[
            CriticalFailedTask(),
            TaskThatMustNotRun(),
        ]
    )

    result = engine.run()

    assert len(result.task_results) == 1
    assert result.task_results[0].status == TaskStatus.FAILED
    assert result.successful is False