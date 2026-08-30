from services.setup.repair_action import (
    REPAIR_ACTION_BUTTON_LABELS,
    RepairAction,
)


def test_every_repair_action_has_button_label() -> None:
    assert (
        set(REPAIR_ACTION_BUTTON_LABELS)
        == RepairAction.ALL
    )


def test_transcription_repair_has_explicit_download_label() -> None:
    assert (
        REPAIR_ACTION_BUTTON_LABELS[
            RepairAction.DOWNLOAD_TRANSCRIPTION_MODEL
        ]
        == "Descargar modelo"
    )


def test_default_container_registers_onboarding_repairs() -> None:
    from application.dependency_container import (
        container,
    )

    executor = container.get(
        "setup_repair_executor"
    )

    assert executor.can_execute(
        RepairAction.DOWNLOAD_TRANSCRIPTION_MODEL
    )

    assert executor.can_execute(
        RepairAction.DOWNLOAD_AI_MODEL
    )

    assert executor.can_execute(
        RepairAction.INSTALL_AI_PROVIDER
    )

    assert not executor.can_execute(
        RepairAction.REPAIR_AUDIO_DEVICES
    )


def test_main_window_subscribes_repair_events() -> None:
    from gui.main_window import MainWindow

    class FakeDispatcher:

        def __init__(self) -> None:
            self.events = []

        def subscribe(
            self,
            event_name,
            callback,
        ) -> None:
            self.events.append(
                event_name
            )

    class FakeWizard:

        def begin(self):
            pass

        def capability_started(self):
            pass

        def capability_completed(self):
            pass

        def repair_started(self):
            pass

        def repair_completed(self):
            pass

        def repair_unavailable(self):
            pass

        def repair_failed(self):
            pass

    class FakeWindow:

        def __init__(self) -> None:
            self.ui_events = FakeDispatcher()
            self.setup_wizard = FakeWizard()

        def _on_setup_wizard_completed(self):
            pass

        def _on_setup_wizard_failed(self):
            pass

        def hide_setup_wizard(self):
            pass

    fake = FakeWindow()

    MainWindow.subscribe_setup_wizard_events(
        fake
    )

    assert {
        "setup_repair_ui_started",
        "setup_repair_ui_completed",
        "setup_repair_ui_unavailable",
        "setup_repair_ui_failed",
    }.issubset(
        set(fake.ui_events.events)
    )


def test_ai_onboarding_button_labels_are_explicit() -> None:
    assert (
        REPAIR_ACTION_BUTTON_LABELS[
            RepairAction.INSTALL_AI_PROVIDER
        ]
        == "Abrir descarga de Ollama"
    )

    assert (
        REPAIR_ACTION_BUTTON_LABELS[
            RepairAction.DOWNLOAD_AI_MODEL
        ]
        == "Descargar modelo de IA"
    )
