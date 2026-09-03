from pathlib import Path
from types import SimpleNamespace

import pytest

from application.controllers.import_controller import (
    ImportController,
)
from exceptions.insufficient_meeting_evidence_error import (
    InsufficientMeetingEvidenceError,
)
from exceptions.insufficient_meeting_semantic_evidence_error import (
    InsufficientMeetingSemanticEvidenceError,
)
from exceptions.insufficient_transcript_evidence_error import (
    InsufficientTranscriptEvidenceError,
)


class FakeBus:

    def __init__(self) -> None:
        self.events = []

    def emit(
        self,
        event_name,
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
        self.infos = []
        self.warnings = []
        self.errors = []

    def info(self, message) -> None:
        self.infos.append(message)

    def warning(self, message) -> None:
        self.warnings.append(message)

    def error(self, message) -> None:
        self.errors.append(message)


class FakeImportedMeetingService:

    def __init__(
        self,
        result=None,
        error: Exception | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.received_source = None

    def import_wav(
        self,
        source_file,
    ):
        self.received_source = source_file

        if self.error is not None:
            raise self.error

        return self.result


def build_controller(
    imported_meeting_service,
):
    bus = FakeBus()
    logger = FakeLogger()

    controller = ImportController(
        state=object(),
        bus=bus,
        logger=logger,
        task_runner=object(),
        imported_meeting_service=(
            imported_meeting_service
        ),
    )

    return (
        controller,
        bus,
        logger,
    )


@pytest.mark.parametrize(
    "expected_error",
    [
        InsufficientTranscriptEvidenceError(
            "Transcript demasiado corto."
        ),
        InsufficientMeetingSemanticEvidenceError(
            source_chunk_count=1,
            content_chunk_count=0,
        ),
    ],
)
def test_import_controller_emits_expected_evidence_outcome(
    expected_error: InsufficientMeetingEvidenceError,
) -> None:
    service = FakeImportedMeetingService(
        error=expected_error
    )
    controller, bus, logger = build_controller(
        service
    )
    source_file = Path(
        "C:/recordings/non_meeting.wav"
    )

    controller._process_imported_recording(
        source_file
    )

    assert service.received_source == source_file
    assert bus.events == [
        (
            "meeting_import_insufficient_evidence",
            (
                expected_error,
            ),
        )
    ]
    assert len(logger.warnings) == 1
    assert str(source_file) in logger.warnings[0]
    assert type(expected_error).__name__ in logger.warnings[0]
    assert str(expected_error) in logger.warnings[0]
    assert logger.errors == []


@pytest.mark.parametrize(
    "technical_error",
    [
        RuntimeError(
            "ollama unavailable"
        ),
        ValueError(
            "MeetingKnowledge no contiene conocimiento "
            "suficiente para generar un MeetingReport."
        ),
        ValueError(
            "malformed model output"
        ),
    ],
)
def test_import_controller_preserves_generic_failure_semantics(
    technical_error: Exception,
) -> None:
    service = FakeImportedMeetingService(
        error=technical_error
    )
    controller, bus, logger = build_controller(
        service
    )

    controller._process_imported_recording(
        Path(
            "C:/recordings/failure.wav"
        )
    )

    event_names = [
        event_name
        for event_name, _ in bus.events
    ]

    assert event_names == [
        "meeting_import_failed",
        "activity",
    ]
    assert (
        "meeting_import_insufficient_evidence"
        not in event_names
    )
    assert "meeting_import_completed" not in event_names
    assert logger.warnings == []
    assert len(logger.errors) == 1
    assert str(technical_error) in logger.errors[0]
    assert bus.events[-1][1][0].startswith(
        "❌ Error importando grabación:"
    )


def test_import_controller_preserves_success_semantics() -> None:
    session = SimpleNamespace(
        session_dir=Path(
            "C:/meetings/meeting_imported_test"
        )
    )
    service = FakeImportedMeetingService(
        result=session
    )
    controller, bus, logger = build_controller(
        service
    )

    controller._process_imported_recording(
        Path(
            "C:/recordings/meeting.wav"
        )
    )

    assert [
        event_name
        for event_name, _ in bus.events
    ] == [
        "meeting_import_completed",
        "activity",
    ]
    assert logger.warnings == []
    assert logger.errors == []
