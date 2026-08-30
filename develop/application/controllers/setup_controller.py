"""
setup_controller.py

Responsable de coordinar el flujo de configuración
inicial de la aplicación.
"""

from services.setup.repair_executor import (
    SetupRepairExecutor,
)


class SetupController:
    """
    Controlador del flujo de Setup Wizard.
    """

    def __init__(
        self,
        state,
        bus,
        logger,
        task_runner,
        setup_wizard_service,
        repair_executor=None,
    ):
        self.state = state
        self.bus = bus
        self.logger = logger
        self.task_runner = task_runner
        self.setup_wizard_service = setup_wizard_service
        self.repair_executor = (
            repair_executor
            or SetupRepairExecutor()
        )
        self._repair_running = False

    def start(self) -> None:
        """
        Ejecuta el diagnóstico inicial fuera del hilo
        gráfico de CustomTkinter.
        """

        if self.setup_wizard_service is None:

            self.bus.emit(
                "setup_wizard_ui_failed",
                "SetupWizardService no está registrado.",
            )

            return

        if self.state.get(
            "setup_wizard_status"
        ) == "running":

            return

        self.state.set(
            "setup_wizard_status",
            "running",
        )

        self.state.set(
            "setup_wizard_completed",
            False,
        )

        self.state.set(
            "application_ready",
            False,
        )

        self.bus.emit(
            "setup_wizard_ui_started"
        )

        self.task_runner.run(
            self._execute
        )

    def retry(self) -> None:
        """
        Repite el diagnóstico completo.
        """

        self.start()

    def can_execute_repair(
        self,
        repair_action: str,
    ) -> bool:
        """
        Indica si existe un handler registrado para
        una acción de reparación.
        """

        return self.repair_executor.can_execute(
            repair_action
        )

    def request_repair(
        self,
        capability_id: str,
        repair_action: str,
    ) -> bool:
        """
        Solicita una reparación registrada y la ejecuta
        fuera del hilo gráfico.
        """

        if self._repair_running:
            return False

        if not self.can_execute_repair(
            repair_action
        ):

            self.bus.emit(
                "setup_repair_ui_unavailable",
                capability_id,
                repair_action,
            )

            return False

        self._repair_running = True

        self.bus.emit(
            "setup_repair_ui_started",
            capability_id,
            repair_action,
        )

        self.task_runner.run(
            self._execute_repair,
            capability_id,
            repair_action,
        )

        return True

    def accept_result(
        self,
        result,
    ) -> None:
        """
        Actualiza AppState desde el hilo gráfico cuando
        MainWindow recibe el resultado.
        """

        status = result.status.value.lower()

        self.state.set(
            "setup_wizard_status",
            status,
        )

        self.state.set(
            "setup_wizard_completed",
            True,
        )

        self.state.set(
            "application_ready",
            result.can_continue,
        )

    def continue_with_attention(self) -> bool:
        """
        Permite entrar a MAI cuando el diagnóstico terminó
        con elementos no bloqueantes.
        """

        status = self.state.get(
            "setup_wizard_status"
        )

        if status not in {
            "ready",
            "attention",
        }:

            return False

        self.state.set(
            "application_ready",
            True,
        )

        self.bus.emit(
            "setup_wizard_continue_requested"
        )

        return True

    def _execute(self) -> None:

        try:

            result = (
                self.setup_wizard_service.run()
            )

            self.bus.emit(
                "setup_wizard_ui_completed",
                result,
            )

        except Exception as ex:

            self.logger.error(
                "Error ejecutando Setup Wizard: "
                f"{ex}"
            )

            self.bus.emit(
                "setup_wizard_ui_failed",
                str(ex),
            )

    def _execute_repair(
        self,
        capability_id: str,
        repair_action: str,
    ) -> None:

        try:

            result = self.repair_executor.execute(
                repair_action,
                context={
                    "capability_id": capability_id,
                },
            )

            self.bus.emit(
                "setup_repair_ui_completed",
                capability_id,
                result,
            )

            if not result.succeeded:
                return

            self.bus.emit(
                "setup_wizard_ui_started"
            )

            wizard_result = (
                self.setup_wizard_service.run()
            )

            self.bus.emit(
                "setup_wizard_ui_completed",
                wizard_result,
            )

        except Exception as ex:

            self.logger.error(
                "Error ejecutando reparación "
                f"'{repair_action}': {ex}"
            )

            self.bus.emit(
                "setup_repair_ui_failed",
                capability_id,
                repair_action,
                str(ex),
            )

        finally:
            self._repair_running = False
