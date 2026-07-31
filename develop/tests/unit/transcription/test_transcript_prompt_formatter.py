import json

import pytest

from models.transcript import Segment, Transcript
from services.transcript_prompt_formatter import (
    TranscriptPromptFormatter,
)


def build_transcript() -> Transcript:
    transcript = Transcript()

    transcript.add_segment(
        Segment(
            start=0.0,
            end=3.5,
            speaker="SPEAKER_00",
            text="Buenos días, iniciaremos la reunión.",
        )
    )

    transcript.add_segment(
        Segment(
            start=3.5,
            end=8.0,
            speaker="SPEAKER_01",
            text=(
                "Revisaremos el avance de las tareas "
                "pendientes."
            ),
        )
    )

    return transcript


def test_formatter_serializes_complete_transcript() -> None:
    transcript = build_transcript()
    formatter = TranscriptPromptFormatter()

    result = formatter.format(
        transcript
    )

    parsed_result = json.loads(
        result
    )

    assert parsed_result == transcript.as_dict()


def test_formatter_preserves_unicode_characters() -> None:
    transcript = Transcript()

    transcript.add_segment(
        Segment(
            start=0.0,
            end=2.0,
            speaker="SPEAKER_00",
            text=(
                "Revisión técnica y planificación."
            ),
        )
    )

    formatter = TranscriptPromptFormatter()

    result = formatter.format(
        transcript
    )

    assert "Revisión" in result
    assert "planificación" in result
    assert "\\u00f3" not in result


def test_formatter_does_not_modify_transcript() -> None:
    transcript = build_transcript()
    original_data = transcript.as_dict()

    formatter = TranscriptPromptFormatter()

    formatter.format(
        transcript
    )

    assert transcript.as_dict() == original_data


def test_formatter_rejects_invalid_input() -> None:
    formatter = TranscriptPromptFormatter()

    with pytest.raises(
        TypeError,
        match="debe ser una instancia de Transcript",
    ):
        formatter.format(
            object()
        )