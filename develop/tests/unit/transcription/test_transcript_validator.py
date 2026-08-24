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
    filename: str = "summary_v1.md",
    content: str | None = None,
) -> Path:
    template_file = (
        tmp_path / filename
    )

    template_file.write_text(
        (
            content
            if content is not None
            else (
                "Analiza la siguiente transcripción."
                "\n\n"
                "{{TRANSCRIPT}}"
            )
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


def test_formatter_uses_summary_contract_by_default(
    tmp_path: Path,
) -> None:
    formatter = TranscriptPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    result = formatter.format(
        build_transcript()
    )

    assert formatter.contract == "summary_v1"
    assert result.version == "summary_v1"


def test_formatter_supports_meeting_report_contract(
    tmp_path: Path,
) -> None:
    formatter = TranscriptPromptFormatter(
        contract="meeting_report_v1",
        template_file=create_template(
            tmp_path,
            filename="meeting_report_v1.md",
        ),
    )

    result = formatter.format(
        build_transcript()
    )

    assert (
        formatter.contract
        == "meeting_report_v1"
    )

    assert (
        result.version
        == "meeting_report_v1"
    )


def test_formatter_resolves_default_summary_template() -> None:
    formatter = TranscriptPromptFormatter()

    assert formatter.template_file == Path(
        "prompts/summary_v1.md"
    )


def test_formatter_resolves_meeting_report_template() -> None:
    formatter = TranscriptPromptFormatter(
        contract="meeting_report_v1"
    )

    assert formatter.template_file == Path(
        "prompts/meeting_report_v1.md"
    )


def test_formatter_loads_real_summary_contract() -> None:
    formatter = TranscriptPromptFormatter(
        contract="summary_v1"
    )

    result = formatter.format(
        build_transcript()
    )

    assert result.version == "summary_v1"

    assert (
        "key_points"
        in result.content
    )

    assert "{{TRANSCRIPT}}" not in (
        result.content
    )


def test_formatter_loads_real_meeting_report_contract() -> None:
    formatter = TranscriptPromptFormatter(
        contract="meeting_report_v1"
    )

    result = formatter.format(
        build_transcript()
    )

    assert (
        result.version
        == "meeting_report_v1"
    )

    assert '"action_items"' in result.content
    assert '"pending_items"' in result.content
    assert '"participants"' in result.content

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


def test_formatter_rejects_invalid_transcript(
    tmp_path: Path,
) -> None:
    formatter = TranscriptPromptFormatter(
        template_file=create_template(
            tmp_path
        )
    )

    with pytest.raises(
        TypeError,
        match=(
            "debe ser una instancia de Transcript"
        ),
    ):
        formatter.format(
            object()
        )


def test_formatter_rejects_template_without_placeholder(
    tmp_path: Path,
) -> None:
    template_file = create_template(
        tmp_path,
        filename="invalid_template.md",
        content=(
            "Esta plantilla no tiene marcador."
        ),
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


def test_formatter_rejects_multiple_placeholders(
    tmp_path: Path,
) -> None:
    template_file = create_template(
        tmp_path,
        filename="duplicated_placeholder.md",
        content=(
            "{{TRANSCRIPT}}\n"
            "{{TRANSCRIPT}}"
        ),
    )

    formatter = TranscriptPromptFormatter(
        template_file=template_file
    )

    with pytest.raises(
        ValueError,
        match="más de una ocurrencia",
    ):
        formatter.format(
            build_transcript()
        )


def test_formatter_rejects_non_string_contract() -> None:
    with pytest.raises(
        TypeError,
        match="contract debe ser una cadena",
    ):
        TranscriptPromptFormatter(
            contract=123
        )


def test_formatter_rejects_empty_contract() -> None:
    with pytest.raises(
        ValueError,
        match="contract no puede estar vacío",
    ):
        TranscriptPromptFormatter(
            contract="   "
        )


@pytest.mark.parametrize(
    "invalid_contract",
    [
        "../summary_v1",
        "contracts/summary_v1",
        "summary_v1.md",
        "summary v1",
    ],
)
def test_formatter_rejects_invalid_contract_name(
    invalid_contract: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="caracteres no permitidos",
    ):
        TranscriptPromptFormatter(
            contract=invalid_contract
        )


def test_formatter_rejects_invalid_template_file_type() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "template_file debe ser una instancia "
            "de Path"
        ),
    ):
        TranscriptPromptFormatter(
            template_file="prompts/summary_v1.md"
        )


def test_formatter_reports_missing_contract_file(
    tmp_path: Path,
) -> None:
    formatter = TranscriptPromptFormatter(
        contract="missing_contract_v1",
        template_file=(
            tmp_path / "missing_contract_v1.md"
        ),
    )

    with pytest.raises(
        FileNotFoundError,
    ):
        formatter.format(
            build_transcript()
        )