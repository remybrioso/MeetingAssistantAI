"""
setup_controller.py

Responsable de coordinar el flujo de configuración
inicial de la aplicación.
"""


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
    ):
        self.state = state
        self.bus = bus
        self.logger = logger
        self.task_runner = task_runner
        self.setup_wizard_service = setup_wizard_service

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