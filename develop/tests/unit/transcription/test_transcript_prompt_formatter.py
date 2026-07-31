import json
from pathlib import Path

import pytest

from models.prompt import Prompt
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
            text=(
                "Buenos días, iniciaremos la reunión."
            ),
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


def create_template(
    tmp_path: Path,
) -> Path:
    template_file = (
        tmp_path / "summary_v1.md"
    )

    template_file.write_text(
        (
            "Analiza la siguiente transcripción.\n\n"
            "{{TRANSCRIPT}}"
        ),
        encoding="utf-8",
    )

    return template_file


def test_formatter_returns_prompt(
    tmp_path: Path,
) -> None:
    transcript = build_transcript()

    formatter = TranscriptPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    result = formatter.format(
        transcript
    )

    assert isinstance(
        result,
        Prompt,
    )

    assert result.version == "summary_v1"

    assert "{{TRANSCRIPT}}" not in (
        result.content
    )


def test_formatter_serializes_complete_transcript(
    tmp_path: Path,
) -> None:
    transcript = build_transcript()

    formatter = TranscriptPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    result = formatter.format(
        transcript
    )

    transcript_json = json.dumps(
        transcript.as_dict(),
        ensure_ascii=False,
        indent=4,
    )

    assert transcript_json in result.content


def test_formatter_preserves_unicode_characters(
    tmp_path: Path,
) -> None:
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

    formatter = TranscriptPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    result = formatter.format(
        transcript
    )

    assert "Revisión" in result.content
    assert "planificación" in result.content
    assert "\\u00f3" not in result.content


def test_formatter_does_not_modify_transcript(
    tmp_path: Path,
) -> None:
    transcript = build_transcript()
    original_data = transcript.as_dict()

    formatter = TranscriptPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    formatter.format(
        transcript
    )

    assert transcript.as_dict() == original_data


def test_formatter_rejects_invalid_input(
    tmp_path: Path,
) -> None:
    formatter = TranscriptPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    with pytest.raises(
        TypeError,
        match="debe ser una instancia de Transcript",
    ):
        formatter.format(
            object()
        )


def test_formatter_rejects_template_without_placeholder(
    tmp_path: Path,
) -> None:
    template_file = (
        tmp_path / "invalid_template.md"
    )

    template_file.write_text(
        "Esta plantilla no tiene marcador.",
        encoding="utf-8",
    )

    formatter = TranscriptPromptFormatter(
        template_file=template_file
    )

    with pytest.raises(
        ValueError,
        match="no contiene el marcador",
    ):
        formatter.format(
            build_transcript()
        )