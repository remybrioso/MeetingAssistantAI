from application.controllers.setup_controller import (
    SetupController,
)
from services.setup.repair_action import RepairAction
from services.setup.repair_result import (
    RepairExecutionResult,
    RepairExecutionStatus,
)


class FakeState:

    def __init__(self) -> None:
        self.values = {
            "setup_wizard_status": "blocked",
            "setup_wizard_completed": True,
            "application_ready": False,
        }

    def get(self, key: str):
        return self.values[key]

    def set(
        self,
        key: str,
        value,
    ) -> None:
        self.values[key] = value


class FakeBus:

    def __init__(self) -> None:
        self.events = []

    def emit(
        self,
        event_name: str,
        *args,
    ) -> None:
        self.events.append(
            (
                event_name,
                args,
            )
        )


class FakeLogger:

    def __init__(self) -> None:
        self.errors = []

    def error(self, message: str) -> None:
        self.errors.append(message)


class ImmediateTaskRunner:

    def run(
        self,
        target,
        *args,
        **kwargs,
    ):
        target(
            *args,
            **kwargs,
        )
        return object()


class FakeWizardResult:
    pass


class FakeWizardService:

    def __init__(self) -> None:
        self.run_count = 0
        self.result = FakeWizardResult()

    def run(self):
        self.run_count += 1
        return self.result


class FakeRepairExecutor:

    def __init__(
        self,
        *,
        executable: bool,
        result: RepairExecutionResult,
    ) -> None:
        self.executable = executable
        self.result = result
        self.calls = []

    def can_execute(
        self,
        action: str,
    ) -> bool:
        return self.executable

    def execute(
        self,
        action: str,
        context=None,
    ) -> RepairExecutionResult:
        self.calls.append(
            (
                action,
                context,
            )
        )
        return self.result


def _build_controller(
    repair_executor,
):
    state = FakeState()
    bus = FakeBus()
    logger = FakeLogger()
    wizard = FakeWizardService()

    controller = SetupController(
        state=state,
        bus=bus,
        logger=logger,
        task_runner=ImmediateTaskRunner(),
        setup_wizard_service=wizard,
        repair_executor=repair_executor,
    )

    return (
        controller,
        bus,
        logger,
        wizard,
    )


def test_controller_reports_repair_support() -> None:
    repair_executor = FakeRepairExecutor(
        executable=True,
        result=RepairExecutionResult(
            action=(
                RepairAction
                .DOWNLOAD_TRANSCRIPTION_MODEL
            ),
            status=RepairExecutionStatus.SUCCESS,
            message="Disponible.",
        ),
    )

    (
        controller,
        _,
        _,
        _,
    ) = _build_controller(
        repair_executor
    )

    assert controller.can_execute_repair(
        RepairAction.DOWNLOAD_TRANSCRIPTION_MODEL
    )


def test_controller_rejects_unavailable_repair() -> None:
    repair_executor = FakeRepairExecutor(
        executable=False,
        result=RepairExecutionResult(
            action=RepairAction.DOWNLOAD_AI_MODEL,
            status=RepairExecutionStatus.UNSUPPORTED,
            message="No disponible.",
        ),
    )

    (
        controller,
        bus,
        _,
        wizard,
    ) = _build_controller(
        repair_executor
    )

    accepted = controller.request_repair(
        "artificial-intelligence",
        RepairAction.DOWNLOAD_AI_MODEL,
    )

    assert accepted is False
    assert wizard.run_count == 0

    assert bus.events == [
        (
            "setup_repair_ui_unavailable",
            (
                "artificial-intelligence",
                RepairAction.DOWNLOAD_AI_MODEL,
            ),
        )
    ]


def test_successful_repair_rechecks_setup_wizard() -> None:
    repair_executor = FakeRepairExecutor(
        executable=True,
        result=RepairExecutionResult(
            action=(
                RepairAction
                .DOWNLOAD_TRANSCRIPTION_MODEL
            ),
            status=RepairExecutionStatus.SUCCESS,
            message="Modelo preparado.",
        ),
    )

    (
        controller,
        bus,
        _,
        wizard,
    ) = _build_controller(
        repair_executor
    )

    accepted = controller.request_repair(
        "transcription",
        (
            RepairAction
            .DOWNLOAD_TRANSCRIPTION_MODEL
        ),
    )

    assert accepted is True
    assert wizard.run_count == 1

    assert repair_executor.calls == [
        (
            RepairAction.DOWNLOAD_TRANSCRIPTION_MODEL,
            {
                "capability_id": "transcription",
            },
        )
    ]

    event_names = [
        name
        for name, _
        in bus.events
    ]

    assert event_names == [
        "setup_repair_ui_started",
        "setup_repair_ui_completed",
        "setup_wizard_ui_started",
        "setup_wizard_ui_completed",
    ]

    assert (
        bus.events[-1][1][0]
        is wizard.result
    )


def test_failed_repair_does_not_recheck_wizard() -> None:
    repair_executor = FakeRepairExecutor(
        executable=True,
        result=RepairExecutionResult(
            action=RepairAction.DOWNLOAD_AI_MODEL,
            status=RepairExecutionStatus.FAILED,
            message="Falló.",
        ),
    )

    (
        controller,
        bus,
        _,
        wizard,
    ) = _build_controller(
        repair_executor
    )

    accepted = controller.request_repair(
        "artificial-intelligence",
        RepairAction.DOWNLOAD_AI_MODEL,
    )

    assert accepted is True
    assert wizard.run_count == 0

    event_names = [
        name
        for name, _
        in bus.events
    ]

    assert event_names == [
        "setup_repair_ui_started",
        "setup_repair_ui_completed",
    ]


def test_external_repair_waits_for_user_action() -> None:
    repair_executor = FakeRepairExecutor(
        executable=True,
        result=RepairExecutionResult(
            action=RepairAction.INSTALL_AI_PROVIDER,
            status=(
                RepairExecutionStatus
                .USER_ACTION_REQUIRED
            ),
            message="Instala Ollama.",
        ),
    )

    (
        controller,
        bus,
        _,
        wizard,
    ) = _build_controller(
        repair_executor
    )

    accepted = controller.request_repair(
        "artificial-intelligence",
        RepairAction.INSTALL_AI_PROVIDER,
    )

    assert accepted is True
    assert wizard.run_count == 0

    event_names = [
        name
        for name, _
        in bus.events
    ]

    assert event_names == [
        "setup_repair_ui_started",
        "setup_repair_ui_completed",
    ]
