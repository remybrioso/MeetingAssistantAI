from types import MethodType

from exceptions.insufficient_meeting_evidence_error import (
    InsufficientMeetingEvidenceError,
)
from exceptions.insufficient_meeting_semantic_evidence_error import (
    InsufficientMeetingSemanticEvidenceError,
)
from exceptions.insufficient_transcript_evidence_error import (
    InsufficientTranscriptEvidenceError,
)
from gui.components.action_panel import ActionPanel
from gui.main_window import MainWindow


STRUCTURAL_WARNING = (
    "⚠️ Audio y transcripción guardados. No se generó una "
    "minuta porque la transcripción no contiene suficiente "
    "contenido utilizable."
)

SEMANTIC_WARNING = (
    "⚠️ Audio y transcripción guardados. No se generó una "
    "minuta porque el contenido no contiene suficiente evidencia "
    "de una reunión."
)

GENERIC_WARNING = (
    "⚠️ Audio y transcripción guardados. No se generó una "
    "minuta porque no existe evidencia suficiente para producir "
    "un reporte útil."
)


class FakeDispatcher:

    def __init__(self) -> None:
        self.callbacks = {}

    def subscribe(
        self,
        event_name,
        callback,
    ) -> None:
        self.callbacks.setdefault(
            event_name,
            [],
        ).append(
            callback
        )


class FakeActivity:

    def __init__(self) -> None:
        self.messages = []

    def add(
        self,
        message,
    ) -> None:
        self.messages.append(
            message
        )


class FakeStatusPanel:

    def __init__(self) -> None:
        self.calls = []

    def set_status(
        self,
        service,
        active,
    ) -> None:
        self.calls.append(
            (
                service,
                active,
            )
        )


class FakeButton:

    def __init__(self) -> None:
        self.state = None

    def configure(
        self,
        *,
        state,
    ) -> None:
        self.state = state


def build_fake_window():
    class FakeWindow:

        def on_meeting_started(self):
            pass

        def on_meeting_finished(self):
            pass

    window = FakeWindow()
    window.ui_events = FakeDispatcher()
    window.activity = FakeActivity()
    window.status_panel = FakeStatusPanel()

    for method_name in (
        "_on_meeting_processing_insufficient_evidence",
        "_on_meeting_import_insufficient_evidence",
        "_show_insufficient_evidence_warning",
    ):
        setattr(
            window,
            method_name,
            MethodType(
                getattr(
                    MainWindow,
                    method_name,
                ),
                window,
            ),
        )

    window._insufficient_evidence_message = (
        MainWindow._insufficient_evidence_message
    )

    MainWindow.subscribe_events(
        window
    )

    return window


def build_fake_action_panel():
    panel = type(
        "FakeActionPanel",
        (),
        {},
    )()
    panel.ui_events = FakeDispatcher()
    panel.btn_start = FakeButton()
    panel.btn_pause = FakeButton()
    panel.btn_resume = FakeButton()
    panel.btn_stop = FakeButton()
    panel.btn_export = FakeButton()
    panel.btn_import = FakeButton()

    method_names = (
        "on_meeting_started",
        "on_meeting_paused",
        "on_meeting_resumed",
        "on_meeting_finished",
        "on_processing_completed",
        "on_processing_failed",
        "on_processing_insufficient_evidence",
        "on_import_started",
        "on_import_completed",
        "on_import_failed",
        "on_import_insufficient_evidence",
    )

    for method_name in method_names:
        setattr(
            panel,
            method_name,
            MethodType(
                getattr(
                    ActionPanel,
                    method_name,
                ),
                panel,
            ),
        )

    ActionPanel._bind_events(
        panel
    )

    return panel


def test_ui_maps_each_expected_evidence_subtype_without_internal_detail() -> None:
    structural = InsufficientTranscriptEvidenceError(
        "internal structural detail"
    )
    semantic = InsufficientMeetingSemanticEvidenceError(
        source_chunk_count=4,
        content_chunk_count=0,
    )
    unknown = InsufficientMeetingEvidenceError(
        "future internal detail"
    )

    assert (
        MainWindow._insufficient_evidence_message(
            structural
        )
        == STRUCTURAL_WARNING
    )
    assert (
        MainWindow._insufficient_evidence_message(
            semantic
        )
        == SEMANTIC_WARNING
    )
    assert (
        MainWindow._insufficient_evidence_message(
            unknown
        )
        == GENERIC_WARNING
    )

    messages = (
        STRUCTURAL_WARNING,
        SEMANTIC_WARNING,
        GENERIC_WARNING,
    )

    assert all(
        "MeetingKnowledge" not in message
        and "chunk" not in message
        and "internal" not in message
        for message in messages
    )


def test_normal_expected_outcome_warns_and_stops_processing_status() -> None:
    window = build_fake_window()
    error = InsufficientTranscriptEvidenceError(
        "internal detail"
    )

    callback = window.ui_events.callbacks[
        "meeting_processing_insufficient_evidence"
    ][0]
    callback(
        error
    )

    assert window.activity.messages == [
        STRUCTURAL_WARNING
    ]
    assert window.status_panel.calls == [
        (
            "processing",
            False,
        )
    ]


def test_import_expected_outcome_warns_without_processing_state_change() -> None:
    window = build_fake_window()
    error = InsufficientMeetingSemanticEvidenceError(
        source_chunk_count=2,
        content_chunk_count=0,
    )

    callback = window.ui_events.callbacks[
        "meeting_import_insufficient_evidence"
    ][0]
    callback(
        error
    )

    assert window.activity.messages == [
        SEMANTIC_WARNING
    ]
    assert window.status_panel.calls == []


def test_action_panel_subscribes_all_report_availability_events() -> None:
    panel = build_fake_action_panel()

    assert {
        "meeting_processing_completed",
        "meeting_processing_failed",
        "meeting_processing_insufficient_evidence",
        "meeting_import_completed",
        "meeting_import_failed",
        "meeting_import_insufficient_evidence",
    }.issubset(
        panel.ui_events.callbacks
    )


def test_action_panel_enables_export_only_after_report_completion() -> None:
    panel = build_fake_action_panel()

    panel.on_meeting_finished()
    assert panel.btn_export.state == "disabled"

    panel.on_processing_completed(
        object()
    )
    assert panel.btn_export.state == "normal"

    panel.on_processing_failed(
        RuntimeError()
    )
    assert panel.btn_export.state == "disabled"

    panel.on_processing_insufficient_evidence(
        InsufficientMeetingEvidenceError()
    )
    assert panel.btn_export.state == "disabled"

    panel.on_import_completed(
        object()
    )
    assert panel.btn_export.state == "normal"

    panel.on_import_failed(
        RuntimeError()
    )
    assert panel.btn_export.state == "disabled"

    panel.btn_start.state = "disabled"
    panel.btn_import.state = "disabled"
    panel.on_import_insufficient_evidence(
        InsufficientMeetingEvidenceError()
    )

    assert panel.btn_start.state == "normal"
    assert panel.btn_import.state == "normal"
    assert panel.btn_export.state == "disabled"
