import pytest

from models.artifacts.meeting_report import MeetingReport
from models.prompt import Prompt
from services.meeting_report_service import (
    MeetingReportService,
)


class FakeProvider:

    model = "fake-model"

    def __init__(self) -> None:
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
            '{"title": "Reporte de prueba"}'
        )


class FakeMeetingReportParser:

    def __init__(self) -> None:
        self.received_response = None
        self.received_provider = None
        self.received_model = None
        self.received_prompt_version = None

        self.report = object()

    def parse(
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

        return self.report


class FakeSchemaLoader:

    def __init__(self) -> None:
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
    response_parser = FakeMeetingReportParser()
    schema_loader = FakeSchemaLoader()

    service = MeetingReportService(
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


def test_meeting_report_service_generates_from_prompt() -> None:
    (
        service,
        provider,
        response_parser,
        schema_loader,
    ) = build_service()

    prompt = Prompt(
        content=(
            "Genera el documento formal de la reunión."
        ),
        version="meeting_report_v1",
    )

    result = service.generate(
        prompt
    )

    assert result is response_parser.report

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
        == "meeting_report_v1"
    )

    assert (
        response_parser.received_response
        == '{"title": "Reporte de prueba"}'
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
        == "meeting_report_v1"
    )


def test_meeting_report_service_uses_prompt_version() -> None:
    (
        service,
        provider,
        response_parser,
        schema_loader,
    ) = build_service()

    prompt = Prompt(
        content="Prompt de prueba.",
        version="meeting_report_v2",
    )

    service.generate(
        prompt
    )

    assert (
        schema_loader.received_contract
        == "meeting_report_v2"
    )

    assert (
        response_parser.received_prompt_version
        == "meeting_report_v2"
    )

    assert (
        provider.received_output_schema
        is schema_loader.schema
    )


def test_meeting_report_service_passes_schema_to_provider() -> None:
    (
        service,
        provider,
        _,
        schema_loader,
    ) = build_service()

    prompt = Prompt(
        content="Procesa esta reunión.",
        version="meeting_report_v1",
    )

    service.generate(
        prompt
    )

    assert (
        provider.received_output_schema
        is schema_loader.schema
    )


def test_meeting_report_service_passes_provider_model_to_parser() -> None:
    (
        service,
        _,
        response_parser,
        _,
    ) = build_service()

    prompt = Prompt(
        content="Procesa esta reunión.",
        version="meeting_report_v1",
    )

    service.generate(
        prompt
    )

    assert (
        response_parser.received_provider
        == "ollama"
    )

    assert (
        response_parser.received_model
        == "fake-model"
    )


def test_meeting_report_service_returns_parser_result() -> None:
    (
        service,
        _,
        response_parser,
        _,
    ) = build_service()

    prompt = Prompt(
        content="Procesa esta reunión.",
        version="meeting_report_v1",
    )

    result = service.generate(
        prompt
    )

    assert result is response_parser.report


def test_meeting_report_service_rejects_invalid_prompt() -> None:
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


def test_meeting_report_service_uses_real_dependencies_by_default() -> None:
    service = MeetingReportService()

    assert (
        service.provider
        is not None
    )

    assert (
        service.response_parser
        is not None
    )

    assert (
        service.schema_loader
        is not None
    )


def test_meeting_report_service_declares_meeting_report_return_contract() -> None:
    annotation = (
        MeetingReportService
        .generate
        .__annotations__
        .get(
            "return"
        )
    )

    assert annotation is MeetingReport