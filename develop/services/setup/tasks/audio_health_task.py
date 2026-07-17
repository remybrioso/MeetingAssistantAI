"""
audio_health_task.py

Comprueba la disponibilidad de las fuentes
de audio necesarias para una reunión.
"""

from services.audio_health_service import (
    AudioHealthService,
)
from services.setup.setup_task import SetupTask
from services.setup.task_result import (
    TaskResult,
    TaskStatus,
)


class AudioHealthTask(SetupTask):

    task_id = "verify-audio-capability"
    name = "Verificar dispositivos de audio"
    critical = False

    def __init__(
        self,
        audio_health_service=None
    ):

        self.audio_health_service = (
            audio_health_service
            or AudioHealthService()
        )

    def should_run(self) -> bool:

        return True

    def run(self) -> TaskResult:

        try:
            health = (
                self.audio_health_service.check()
            )

            details = health.as_dict()

            if not health.microphone_available:

                return TaskResult(
                    task_id=self.task_id,
                    name=self.name,
                    status=TaskStatus.FAILED,
                    message=(
                        "No existe un micrófono "
                        "utilizable."
                    ),
                    details=details,
                    error=health.error,
                )

            if not health.system_audio_available:

                return TaskResult(
                    task_id=self.task_id,
                    name=self.name,
                    status=TaskStatus.SUCCESS,
                    message=(
                        "El micrófono está disponible, "
                        "pero el audio del sistema no."
                    ),
                    details={
                        **details,
                        "degraded": True,
                    },
                )

            return TaskResult(
                task_id=self.task_id,
                name=self.name,
                status=TaskStatus.SUCCESS,
                message=(
                    "El micrófono y el audio del "
                    "sistema están disponibles."
                ),
                details={
                    **details,
                    "degraded": False,
                },
            )

        except Exception as ex:

            return TaskResult(
                task_id=self.task_id,
                name=self.name,
                status=TaskStatus.FAILED,
                message=(
                    "No fue posible comprobar los "
                    "dispositivos de audio."
                ),
                details={},
                error=str(ex),
            )

    def verify(self) -> bool:

        try:
            return bool(
                self.audio_health_service
                .check()
                .is_usable
            )

        except Exception:
            return False