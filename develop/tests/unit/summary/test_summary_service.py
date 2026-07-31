import pytest

from models.prompt import Prompt
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


def test_summary_service_generates_from_prompt() -> None:
    provider = FakeProvider()
    response_parser = FakeResponseParser()

    service = SummaryService(
        provider=provider,
        response_parser=response_parser,
    )

    prompt = Prompt(
        content=(
            "Genera una minuta a partir de esta "
            "transcripción."
        ),
        version="summary_v1",
    )

    result = service.generate(
        prompt
    )

    assert result is response_parser.summary

    assert (
        provider.received_prompt
        == prompt.content
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


def test_summary_service_uses_prompt_version() -> None:
    provider = FakeProvider()
    response_parser = FakeResponseParser()

    service = SummaryService(
        provider=provider,
        response_parser=response_parser,
    )

    prompt = Prompt(
        content="Prompt de prueba.",
        version="executive_summary_v2",
    )

    service.generate(
        prompt
    )

    assert (
        response_parser.received_prompt_version
        == "executive_summary_v2"
    )


def test_summary_service_rejects_invalid_prompt() -> None:
    service = SummaryService(
        provider=FakeProvider(),
        response_parser=FakeResponseParser(),
    )

    with pytest.raises(
        TypeError,
        match="debe ser una instancia de Prompt",
    ):
        service.generate(
            "Esto no es un Prompt."
        )