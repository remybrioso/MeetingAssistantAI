"""
ai_provider_health_task.py

Comprueba la disponibilidad del proveedor de IA
y del modelo configurado.
"""

from services.setup.setup_task import SetupTask
from services.setup.task_result import (
    TaskResult,
    TaskStatus,
)


class AIProviderHealthTask(SetupTask):

    task_id = "verify-ai-provider"
    name = "Verificar motor de inteligencia artificial"
    critical = True

    def __init__(self, provider):

        self.provider = provider

    def should_run(self) -> bool:

        return True

    def run(self) -> TaskResult:

        try:
            health = self.provider.health()

            details = {
                "provider": health.provider,
                "connected": health.connected,
                "model": health.model,
                "model_found": health.model_found,
                "response_time_ms": (
                    health.response_time_ms
                ),
                "available_models": (
                    health.available_models
                ),
            }

            if health.error:
                details["error"] = health.error

            if not health.connected:

                return TaskResult(
                    task_id=self.task_id,
                    name=self.name,
                    status=TaskStatus.FAILED,
                    message=(
                        "El motor de inteligencia "
                        "artificial no está disponible."
                    ),
                    details=details,
                    error=health.error,
                )

            if not health.model_found:

                return TaskResult(
                    task_id=self.task_id,
                    name=self.name,
                    status=TaskStatus.FAILED,
                    message=(
                        "El motor de inteligencia artificial "
                        "está disponible, pero falta el "
                        "modelo requerido."
                    ),
                    details=details,
                    error=(
                        f"Modelo no encontrado: "
                        f"{health.model}"
                    ),
                )

            return TaskResult(
                task_id=self.task_id,
                name=self.name,
                status=TaskStatus.SUCCESS,
                message=(
                    "El motor de inteligencia artificial "
                    "y el modelo están disponibles."
                ),
                details=details,
            )

        except Exception as ex:

            return TaskResult(
                task_id=self.task_id,
                name=self.name,
                status=TaskStatus.FAILED,
                message=(
                    "No fue posible comprobar el motor "
                    "de inteligencia artificial."
                ),
                details={
                    "provider_class": (
                        self.provider
                        .__class__
                        .__name__
                    ),
                },
                error=str(ex),
            )

    def verify(self) -> bool:

        try:
            return bool(
                self.provider.health().is_healthy
            )

        except Exception:
            return False