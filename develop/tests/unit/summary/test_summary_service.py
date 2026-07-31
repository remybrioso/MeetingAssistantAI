from pathlib import Path

import pytest

from services.summary_service import SummaryService


class FakeProvider:

    model = "fake-model"

    def __init__(self):
        self.received_prompt = None

    def generate(
        self,
        prompt,
    ):
        self.received_prompt = prompt

        return (
            '{"title": "Resumen de prueba"}'
        )


class FakeResponseParser:

    def __init__(self):
        self.received_response = None
        self.received_provider = None
        self.received_model = None
        self.received_prompt_version = None
        self.summary = object()

    def parse_summary(
        self,
        response,
        provider,
        model,
        prompt_version,
    ):
        self.received_response = response
        self.received_provider = provider
        self.received_model = model
        self.received_prompt_version = (
            prompt_version
        )

        return self.summary


def test_summary_service_generates_from_text(
    tmp_path: Path,
) -> None:
    prompt_file = (
        tmp_path / "summary_prompt.md"
    )

    prompt_file.write_text(
        (
            "Genera una minuta con la siguiente "
            "transcripción:\n\n"
            "{{TRANSCRIPT}}"
        ),
        encoding="utf-8",
    )

    provider = FakeProvider()
    response_parser = FakeResponseParser()

    service = SummaryService(
        provider=provider,
        response_parser=response_parser,
        prompt_file=prompt_file,
    )

    transcript_text = (
        '{"segments": [{"text": "Contenido de prueba"}]}'
    )

    result = service.generate(
        transcript_text
    )

    assert result is response_parser.summary

    assert transcript_text in (
        provider.received_prompt
    )

    assert "{{TRANSCRIPT}}" not in (
        provider.received_prompt
    )

    assert (
        response_parser.received_response
        == '{"title": "Resumen de prueba"}'
    )

    assert (
        response_parser.received_provider
        == "ollama"
    )

    assert (
        response_parser.received_model
        == "fake-model"
    )

    assert (
        response_parser.received_prompt_version
        == "summary_v1"
    )


def test_summary_service_rejects_empty_text(
    tmp_path: Path,
) -> None:
    service = SummaryService(
        provider=FakeProvider(),
        response_parser=FakeResponseParser(),
        prompt_file=(
            tmp_path / "unused.md"
        ),
    )

    with pytest.raises(
        ValueError,
        match="no puede estar vacío",
    ):
        service.generate(
            "   "
        )


def test_summary_service_rejects_non_string_input(
    tmp_path: Path,
) -> None:
    service = SummaryService(
        provider=FakeProvider(),
        response_parser=FakeResponseParser(),
        prompt_file=(
            tmp_path / "unused.md"
        ),
    )

    with pytest.raises(
        TypeError,
        match="debe ser una cadena",
    ):
        service.generate(
            None
        )