import pytest

from models.meeting_report import ActionStatus


def test_action_status_contains_expected_values() -> None:
    assert ActionStatus.UNKNOWN.value == "unknown"
    assert ActionStatus.PENDING.value == "pending"
    assert ActionStatus.COMPLETED.value == "completed"
    assert ActionStatus.CANCELLED.value == "cancelled"


def test_action_status_behaves_as_string() -> None:
    status = ActionStatus.PENDING

    assert status == "pending"
    assert str(status) == "pending"


def test_action_status_can_be_created_from_exact_value() -> None:
    status = ActionStatus(
        "completed"
    )

    assert status is ActionStatus.COMPLETED


def test_action_status_from_value_normalizes_text() -> None:
    status = ActionStatus.from_value(
        " PENDING "
    )

    assert status is ActionStatus.PENDING


def test_action_status_from_value_accepts_existing_status() -> None:
    status = ActionStatus.from_value(
        ActionStatus.CANCELLED
    )

    assert status is ActionStatus.CANCELLED


def test_action_status_rejects_unknown_value() -> None:
    with pytest.raises(
        ValueError,
        match="Estado de acción no válido",
    ):
        ActionStatus.from_value(
            "done"
        )


def test_action_status_error_lists_valid_values() -> None:
    with pytest.raises(
        ValueError,
        match="unknown, pending, completed, cancelled",
    ):
        ActionStatus.from_value(
            "waiting"
        )


def test_action_status_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="requiere una cadena",
    ):
        ActionStatus.from_value(
            123
        )


def test_action_status_serializes_as_text() -> None:
    data = {
        "status": ActionStatus.PENDING,
    }

    assert data == {
        "status": "pending",
    }