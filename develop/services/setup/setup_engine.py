"""
setup_engine.py

Orquestador del MAI Setup & Recovery Engine.
"""

from datetime import datetime

from services.setup.setup_result import SetupResult
from services.setup.task_result import (
    TaskResult,
    TaskStatus,
)


class SetupEngine:

    def __init__(
        self,
        tasks=None,
        event_bus=None
    ):

        self.tasks = list(tasks or [])
        self.event_bus = event_bus

    def add_task(self, task) -> None:

        self.tasks.append(task)

    def run(self) -> SetupResult:

        started_at = datetime.now()
        results = []

        self._emit(
            "setup_started",
            len(self.tasks)
        )

        for index, task in enumerate(
            self.tasks,
            start=1
        ):

            self._emit(
                "setup_task_started",
                task.task_id,
                task.name,
                index,
                len(self.tasks)
            )

            result = self._execute_task(task)

            results.append(result)

            self._emit(
                "setup_task_completed",
                result
            )

            if (
                result.status == TaskStatus.FAILED
                and task.critical
            ):

                self._emit(
                    "setup_stopped",
                    result
                )

                break

        setup_result = SetupResult(
            started_at=started_at,
            completed_at=datetime.now(),
            task_results=results
        )

        self._emit(
            "setup_completed",
            setup_result
        )

        return setup_result

    def _execute_task(self, task) -> TaskResult:

        try:
            if not task.should_run():

                return TaskResult(
                    task_id=task.task_id,
                    name=task.name,
                    status=TaskStatus.SKIPPED,
                    message=(
                        "La tarea no era necesaria."
                    ),
                )

            result = task.run()

            if not isinstance(result, TaskResult):

                raise TypeError(
                    "La tarea no devolvió TaskResult."
                )

            if (
                result.status == TaskStatus.SUCCESS
                and result.verification_required
            ):

                verified = task.verify()

                if not verified:

                    return TaskResult(
                        task_id=task.task_id,
                        name=task.name,
                        status=TaskStatus.FAILED,
                        message=(
                            "La tarea terminó, pero "
                            "la verificación falló."
                        ),
                        details=result.details,
                        error=(
                            "La comprobación posterior "
                            "no confirmó el resultado."
                        ),
                    )

            return result

        except Exception as ex:

            return TaskResult(
                task_id=getattr(
                    task,
                    "task_id",
                    task.__class__.__name__
                ),
                name=getattr(
                    task,
                    "name",
                    task.__class__.__name__
                ),
                status=TaskStatus.FAILED,
                message=(
                    "La tarea no pudo ejecutarse."
                ),
                error=str(ex),
            )

    def _emit(self, event_name, *args) -> None:

        if self.event_bus:

            self.event_bus.emit(
                event_name,
                *args
            )