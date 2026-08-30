"""
ollama_model_repair.py

Descarga de forma explícita el modelo configurado de Ollama
y verifica que quede disponible para MAI.
"""

from services.setup.repair_action import RepairAction
from services.setup.repair_result import (
    RepairExecutionResult,
    RepairExecutionStatus,
)


class OllamaModelRepair:

    def __init__(
        self,
        provider,
    ) -> None:

        if provider is None:
            raise ValueError(
                "provider no puede ser None."
            )

        self.provider = provider

    def __call__(
        self,
        context: dict,
    ) -> RepairExecutionResult:

        repair_context = dict(
            context or {}
        )

        try:
            initial_health = (
                self.provider.health()
            )

            if not initial_health.connected:
                return RepairExecutionResult(
                    action=RepairAction.DOWNLOAD_AI_MODEL,
                    status=RepairExecutionStatus.FAILED,
                    message=(
                        "Ollama no está disponible. "
                        "Inícialo antes de descargar "
                        "el modelo de inteligencia artificial."
                    ),
                    details={
                        "reason": "provider-unavailable",
                        "model": initial_health.model,
                        "capability_id": (
                            repair_context.get(
                                "capability_id"
                            )
                        ),
                    },
                )

            if initial_health.model_found:
                return RepairExecutionResult(
                    action=RepairAction.DOWNLOAD_AI_MODEL,
                    status=RepairExecutionStatus.SUCCESS,
                    message=(
                        "El modelo de inteligencia artificial "
                        "ya está disponible."
                    ),
                    details={
                        "model": initial_health.model,
                        "already_available": True,
                        "capability_id": (
                            repair_context.get(
                                "capability_id"
                            )
                        ),
                    },
                )

            pull_result = (
                self.provider.pull_model()
            )

            final_health = (
                self.provider.health()
            )

            if not final_health.connected:
                return RepairExecutionResult(
                    action=RepairAction.DOWNLOAD_AI_MODEL,
                    status=RepairExecutionStatus.FAILED,
                    message=(
                        "El modelo se descargó, pero MAI "
                        "perdió la conexión con Ollama "
                        "durante la verificación."
                    ),
                    details={
                        "reason": (
                            "provider-unavailable-after-pull"
                        ),
                        "model": final_health.model,
                        "pull_status": pull_result.get(
                            "status"
                        ),
                        "capability_id": (
                            repair_context.get(
                                "capability_id"
                            )
                        ),
                    },
                )

            if not final_health.model_found:
                return RepairExecutionResult(
                    action=RepairAction.DOWNLOAD_AI_MODEL,
                    status=RepairExecutionStatus.FAILED,
                    message=(
                        "Ollama terminó la descarga, pero "
                        "el modelo requerido no aparece "
                        "entre los modelos disponibles."
                    ),
                    details={
                        "reason": "model-not-found-after-pull",
                        "model": final_health.model,
                        "pull_status": pull_result.get(
                            "status"
                        ),
                        "available_models": (
                            final_health.available_models
                        ),
                        "capability_id": (
                            repair_context.get(
                                "capability_id"
                            )
                        ),
                    },
                )

            return RepairExecutionResult(
                action=RepairAction.DOWNLOAD_AI_MODEL,
                status=RepairExecutionStatus.SUCCESS,
                message=(
                    "El modelo de inteligencia artificial "
                    "se descargó correctamente."
                ),
                details={
                    "model": final_health.model,
                    "pull_status": pull_result.get(
                        "status"
                    ),
                    "already_available": False,
                    "capability_id": (
                        repair_context.get(
                            "capability_id"
                        )
                    ),
                },
            )

        except Exception as ex:
            return RepairExecutionResult(
                action=RepairAction.DOWNLOAD_AI_MODEL,
                status=RepairExecutionStatus.FAILED,
                message=(
                    "No fue posible descargar el modelo "
                    "de inteligencia artificial."
                ),
                details={
                    "reason": "model-pull-failed",
                    "error_type": (
                        ex.__class__.__name__
                    ),
                    "error": str(ex),
                    "capability_id": (
                        repair_context.get(
                            "capability_id"
                        )
                    ),
                },
            )
