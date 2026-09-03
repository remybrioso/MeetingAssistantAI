import pytest

from exceptions.insufficient_meeting_evidence_error import (
    InsufficientMeetingEvidenceError,
)
from exceptions.insufficient_meeting_semantic_evidence_error import (
    InsufficientMeetingSemanticEvidenceError,
)
from exceptions.insufficient_transcript_evidence_error import (
    InsufficientTranscriptEvidenceError,
)


def test_transcript_evidence_error_inherits_domain_outcome() -> None:
    error = InsufficientTranscriptEvidenceError(
        "Transcript demasiado corto."
    )

    assert isinstance(
        error,
        InsufficientMeetingEvidenceError,
    )
    assert str(error) == "Transcript demasiado corto."


def test_semantic_evidence_error_preserves_diagnostic_counts() -> None:
    error = InsufficientMeetingSemanticEvidenceError(
        source_chunk_count=3,
        content_chunk_count=0,
    )

    assert isinstance(
        error,
        InsufficientMeetingEvidenceError,
    )
    assert error.source_chunk_count == 3
    assert error.content_chunk_count == 0
    assert "source_chunk_count=3" in str(error)
    assert "content_chunk_count=0" in str(error)


def test_default_composition_reuses_existing_logger() -> None:
    from application.dependency_container import container

    finalization_service = container.get(
        "meeting_finalization_service"
    )

    assert finalization_service.logger is container.get(
        "logger"
    )


@pytest.mark.parametrize(
    (
        "kwargs",
        "expected_error",
        "message",
    ),
    [
        (
            {
                "source_chunk_count": True,
                "content_chunk_count": 0,
            },
            TypeError,
            "source_chunk_count debe ser entero",
        ),
        (
            {
                "source_chunk_count": 0,
                "content_chunk_count": 0,
            },
            ValueError,
            "source_chunk_count debe ser mayor",
        ),
        (
            {
                "source_chunk_count": 1,
                "content_chunk_count": -1,
            },
            ValueError,
            "content_chunk_count debe ser mayor",
        ),
        (
            {
                "source_chunk_count": 1,
                "content_chunk_count": 1,
            },
            ValueError,
            "content_chunk_count debe ser cero",
        ),
    ],
)
def test_semantic_evidence_error_validates_counts(
    kwargs: dict,
    expected_error: type[Exception],
    message: str,
) -> None:
    with pytest.raises(
        expected_error,
        match=message,
    ):
        InsufficientMeetingSemanticEvidenceError(
            **kwargs
        )
