import pytest

from models.prompt import Prompt
from services.summary_service import SummaryService


class FakeProvider:

    model = "fake-model"

    def __init__(self):
        self.received_prompt = None
        self.received_output_schema = None

    def generate(
        self,
        prompt,
        output_schema=None,
    ):
        self.received_prompt = prompt
        self.received_output_schema = (
            output_schema
        )

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


class FakeSchemaLoader:

    def __init__(self):
        self.received_contract = None

        self.schema = {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                },
            },
            "required": [
                "title",
            ],
        }

    def load(
        self,
        contract,
    ):
        self.received_contract = contract

        return self.schema


def build_service():
    provider = FakeProvider()
    response_parser = FakeResponseParser()
    schema_loader = FakeSchemaLoader()

    service = SummaryService(
        provider=provider,
        response_parser=response_parser,
        schema_loader=schema_loader,
    )

    return (
        service,
        provider,
        response_parser,
        schema_loader,
    )


def test_summary_service_generates_from_prompt() -> None:
    (
        service,
        provider,
        response_parser,
        schema_loader,
    ) = build_service()

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
        provider.received_output_schema
        is schema_loader.schema
    )

    assert (
        schema_loader.received_contract
        == "summary_v1"
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
    (
        service,
        provider,
        response_parser,
        schema_loader,
    ) = build_service()

    prompt = Prompt(
        content="Prompt de prueba.",
        version="executive_summary_v2",
    )

    service.generate(
        prompt
    )

    assert (
        schema_loader.received_contract
        == "executive_summary_v2"
    )

    assert (
        response_parser.received_prompt_version
        == "executive_summary_v2"
    )

    assert (
        provider.received_output_schema
        is schema_loader.schema
    )


def test_summary_service_rejects_invalid_prompt() -> None:
    (
        service,
        _,
        _,
        _,
    ) = build_service()

    with pytest.raises(
        TypeError,
        match="debe ser una instancia de Prompt",
    ):
        service.generate(
            "Esto no es un Prompt."
        )