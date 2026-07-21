from services.setup.setup_engine import SetupEngine
from services.setup.setup_task import SetupTask
from services.setup.task_result import TaskResult, TaskStatus


class SuccessfulTask(SetupTask):

    task_id = "successful"
    name = "Tarea correcta"

    def should_run(self) -> bool:
        return True

    def run(self) -> TaskResult:
        return TaskResult(
            task_id=self.task_id,
            name=self.name,
            status=TaskStatus.SUCCESS,
            message="Tarea ejecutada correctamente.",
            verification_required=True,
        )

    def verify(self) -> bool:
        return True


class SkippedTask(SetupTask):

    task_id = "skipped"
    name = "Tarea omitida"

    def should_run(self) -> bool:
        return False

    def run(self) -> TaskResult:
        raise RuntimeError(
            "Esta tarea no debe ejecutarse."
        )


class NonCriticalFailedTask(SetupTask):

    task_id = "non-critical-failed"
    name = "Fallo no crítico"
    critical = False

    def should_run(self) -> bool:
        return True

    def run(self) -> TaskResult:
        return TaskResult(
            task_id=self.task_id,
            name=self.name,
            status=TaskStatus.FAILED,
            message="Fallo simulado no crítico.",
        )


class FinalTask(SetupTask):

    task_id = "final"
    name = "Tarea final"

    def should_run(self) -> bool:
        return True

    def run(self) -> TaskResult:
        return TaskResult(
            task_id=self.task_id,
            name=self.name,
            status=TaskStatus.SUCCESS,
            message="La ejecución continuó.",
        )


def test_setup_engine_continues_after_non_critical_failure() -> None:
    engine = SetupEngine(
        tasks=[
            SuccessfulTask(),
            SkippedTask(),
            NonCriticalFailedTask(),
            FinalTask(),
        ]
    )

    result = engine.run()

    assert len(result.task_results) == 4

    assert result.task_results[0].status == TaskStatus.SUCCESS
    assert result.task_results[1].status == TaskStatus.SKIPPED
    assert result.task_results[2].status == TaskStatus.FAILED

    # Debe continuar porque el fallo no es crítico.
    assert result.task_results[3].status == TaskStatus.SUCCESS

    assert result.successful is False