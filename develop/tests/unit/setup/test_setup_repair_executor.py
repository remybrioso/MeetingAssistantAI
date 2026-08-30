from services.setup.repair_action import RepairAction
from services.setup.repair_executor import (
    SetupRepairExecutor,
)
from services.setup.repair_result import (
    RepairExecutionResult,
    RepairExecutionStatus,
)


def _success_handler(context: dict) -> RepairExecutionResult:
    return RepairExecutionResult(
        action=RepairAction.DOWNLOAD_TRANSCRIPTION_MODEL,
        status=RepairExecutionStatus.SUCCESS,
        message="Modelo preparado.",
        details={
            "capability_id": context.get(
                "capability_id"
            ),
        },
    )


def test_executor_registers_and_executes_known_action() -> None:
    executor = SetupRepairExecutor(
        handlers={
            RepairAction.DOWNLOAD_TRANSCRIPTION_MODEL: (
                _success_handler
            ),
        }
    )

    assert executor.can_execute(
        RepairAction.DOWNLOAD_TRANSCRIPTION_MODEL
    )

    result = executor.execute(
        RepairAction.DOWNLOAD_TRANSCRIPTION_MODEL,
        context={
            "capability_id": "transcription",
        },
    )

    assert result.succeeded is True
    assert (
        result.details["capability_id"]
        == "transcription"
    )


def test_executor_rejects_unknown_registration() -> None:
    executor = SetupRepairExecutor()

    try:
        executor.register(
            "UNKNOWN_ACTION",
            _success_handler,
        )
    except ValueError as ex:
        assert "contrato de MAI" in str(ex)
    else:
        raise AssertionError(
            "Se esperaba ValueError."
        )


def test_executor_reports_unregistered_handler() -> None:
    executor = SetupRepairExecutor()

    result = executor.execute(
        RepairAction.DOWNLOAD_AI_MODEL
    )

    assert result.unsupported is True
    assert (
        result.details["reason"]
        == "handler-not-registered"
    )


def test_executor_reports_unknown_action() -> None:
    executor = SetupRepairExecutor()

    result = executor.execute(
        "UNKNOWN_ACTION"
    )

    assert result.unsupported is True
    assert (
        result.details["reason"]
        == "unknown-action"
    )


def test_executor_converts_handler_exception_to_failure() -> None:
    def failing_handler(context: dict):
        raise RuntimeError("boom")

    executor = SetupRepairExecutor(
        handlers={
            RepairAction.DOWNLOAD_AI_MODEL: (
                failing_handler
            ),
        }
    )

    result = executor.execute(
        RepairAction.DOWNLOAD_AI_MODEL
    )

    assert result.failed is True
    assert (
        result.details["reason"]
        == "handler-exception"
    )
    assert result.details["error"] == "boom"


def test_executor_rejects_invalid_handler_result() -> None:
    def invalid_handler(context: dict):
        return True

    executor = SetupRepairExecutor(
        handlers={
            RepairAction.DOWNLOAD_AI_MODEL: (
                invalid_handler
            ),
        }
    )

    result = executor.execute(
        RepairAction.DOWNLOAD_AI_MODEL
    )

    assert result.failed is True
    assert (
        result.details["reason"]
        == "invalid-handler-result"
    )


def test_executor_rejects_action_mismatch() -> None:
    def mismatched_handler(context: dict):
        return RepairExecutionResult(
            action=RepairAction.REPAIR_WORKSPACE,
            status=RepairExecutionStatus.SUCCESS,
            message="Incorrecto.",
        )

    executor = SetupRepairExecutor(
        handlers={
            RepairAction.DOWNLOAD_AI_MODEL: (
                mismatched_handler
            ),
        }
    )

    result = executor.execute(
        RepairAction.DOWNLOAD_AI_MODEL
    )

    assert result.failed is True
    assert (
        result.details["reason"]
        == "action-mismatch"
    )
