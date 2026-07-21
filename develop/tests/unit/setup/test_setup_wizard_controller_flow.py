from datetime import datetime

from services.setup.wizard.setup_wizard_result import (
    SetupWizardResult,
    SetupWizardStatus,
)


class FakeState:

    def __init__(self) -> None:
        self.values = {
            "setup_wizard_status": "pending",
            "setup_wizard_completed": False,
            "application_ready": False,
        }

    def get(self, key: str):
        return self.values[key]

    def set(self, key: str, value) -> None:
        self.values[key] = value


class ControllerStateAdapter:

    def __init__(self) -> None:
        self.state = FakeState()

    def accept_setup_wizard_result(
        self,
        result: SetupWizardResult,
    ) -> None:
        self.state.set(
            "setup_wizard_status",
            result.status.value.lower(),
        )

        self.state.set(
            "setup_wizard_completed",
            True,
        )

        self.state.set(
            "application_ready",
            result.can_continue,
        )


def test_controller_accepts_setup_wizard_result() -> None:
    controller = ControllerStateAdapter()

    result = SetupWizardResult(
        status=SetupWizardStatus.ATTENTION,
        message="MAI requiere atención.",
        started_at=datetime.now(),
        completed_at=datetime.now(),
        capability_results=[],
    )

    controller.accept_setup_wizard_result(
        result
    )

    assert (
        controller.state.get(
            "setup_wizard_status"
        )
        == "attention"
    )

    assert (
        controller.state.get(
            "setup_wizard_completed"
        )
        is True
    )

    assert (
        controller.state.get(
            "application_ready"
        )
        is True
    )