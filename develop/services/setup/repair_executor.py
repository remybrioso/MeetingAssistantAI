"""
repair_executor.py

Orquesta la ejecución controlada de acciones de reparación
del Setup Wizard sin acoplarlas a la interfaz gráfica.
"""

from collections.abc import Callable

from services.setup.repair_action import RepairAction
from services.setup.repair_result import (
    RepairExecutionResult,
    RepairExecutionStatus,
)


RepairHandler = Callable[
    [dict],
    RepairExecutionResult,
]


class SetupRepairExecutor:

    def __init__(
        self,
        handlers: dict[str, RepairHandler] | None = None,
    ) -> None:

        self._handlers: dict[
            str,
            RepairHandler,
        ] = {}

        for action, handler in (
            handlers or {}
        ).items():
            self.register(
                action,
                handler,
            )

    def register(
        self,
        action: str,
        handler: RepairHandler,
    ) -> None:

        self._validate_action(action)

        if not callable(handler):
            raise TypeError(
                "handler debe ser invocable."
            )

        self._handlers[action] = handler

    def can_execute(
        self,
        action: str,
    ) -> bool:

        return (
            action in RepairAction.ALL
            and action in self._handlers
        )

    def execute(
        self,
        action: str,
        context: dict | None = None,
    ) -> RepairExecutionResult:

        if action not in RepairAction.ALL:
            return RepairExecutionResult(
                action=action,
                status=(
                    RepairExecutionStatus.UNSUPPORTED
                ),
                message=(
                    "La acción de reparación solicitada "
                    "no pertenece al contrato de MAI."
                ),
                details={
                    "reason": "unknown-action",
                },
            )

        handler = self._handlers.get(
            action
        )

        if handler is None:
            return RepairExecutionResult(
                action=action,
                status=(
                    RepairExecutionStatus.UNSUPPORTED
                ),
                message=(
                    "MAI todavía no tiene un ejecutor "
                    "registrado para esta reparación."
                ),
                details={
                    "reason": "handler-not-registered",
                },
            )

        repair_context = dict(
            context or {}
        )

        try:
            result = handler(
                repair_context
            )
        except Exception as ex:
            return RepairExecutionResult(
                action=action,
                status=RepairExecutionStatus.FAILED,
                message=(
                    "La reparación no pudo completarse."
                ),
                details={
                    "reason": "handler-exception",
                    "error": str(ex),
                },
            )

        if not isinstance(
            result,
            RepairExecutionResult,
        ):
            return RepairExecutionResult(
                action=action,
                status=RepairExecutionStatus.FAILED,
                message=(
                    "El ejecutor de reparación devolvió "
                    "un resultado inválido."
                ),
                details={
                    "reason": "invalid-handler-result",
                    "result_type": type(
                        result
                    ).__name__,
                },
            )

        if result.action != action:
            return RepairExecutionResult(
                action=action,
                status=RepairExecutionStatus.FAILED,
                message=(
                    "El ejecutor de reparación devolvió "
                    "una acción diferente a la solicitada."
                ),
                details={
                    "reason": "action-mismatch",
                    "returned_action": result.action,
                },
            )

        return result

    @staticmethod
    def _validate_action(
        action: str,
    ) -> None:

        if action not in RepairAction.ALL:
            raise ValueError(
                "La acción de reparación no pertenece "
                "al contrato de MAI: "
                f"{action!r}."
            )
