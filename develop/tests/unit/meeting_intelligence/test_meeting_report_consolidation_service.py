import json

import pytest

from models.artifacts.meeting_report import MeetingReport
from models.chunk_knowledge import ChunkKnowledge
from models.meeting_knowledge import MeetingKnowledge
from models.prompt import Prompt
from services.meeting_report_consolidation_service import (
    MeetingReportConsolidationService,
)


VALID_RESPONSE = json.dumps(
    {
        "title": "Arquitectura y continuidad del proyecto",
        "objective": None,
        "executive_summary": (
            "Se revisó la arquitectura actual del proyecto "
            "y se confirmó la continuidad de las pruebas."
        ),
        "key_points": [
            "Se revisó la arquitectura actual del proyecto.",
        ],
        "topics": [],
        "decisions": [],
        "action_items": [],
        "risks": [],
        "pending_items": [],
        "participants": [],
        "conclusions": [],
    },
    ensure_ascii=False,
)


class FakeProvider:
    def __init__(
        self,
        response: str = VALID_RESPONSE,
        error: Exception | None = None,
    ) -> None:
        self.response = response
        self.error = error
        self.model = "fake-model"
        self.calls = 0
        self.received_prompt = None
        self.received_schema = None

    def generate(self, prompt, output_schema):
        self.calls += 1
        self.received_prompt = prompt
        self.received_schema = output_schema
        if self.error is not None:
            raise self.error
        return self.response


class FakeSchemaLoader:
    def __init__(
        self,
        schema=None,
        error: Exception | None = None,
    ) -> None:
        self.schema = schema if schema is not None else {"type": "object"}
        self.error = error
        self.calls = 0
        self.received_contract = None

    def load(self, contract):
        self.calls += 1
        self.received_contract = contract
        if self.error is not None:
            raise self.error
        return self.schema


class FakeParser:
    def __init__(
        self,
        result=None,
        error: Exception | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.calls = 0
        self.received_response = None
        self.received_provider = None
        self.received_model = None
        self.received_prompt_version = None

    def parse(
        self,
        response,
        provider,
        model,
        prompt_version,
    ):
        self.calls += 1
        self.received_response = response
        self.received_provider = provider
        self.received_model = model
        self.received_prompt_version = prompt_version
        if self.error is not None:
            raise self.error
        return self.result


class FakeGroundingValidator:
    def __init__(self, result=(True, [])) -> None:
        self.result = result
        self.calls = 0
        self.received_report = None
        self.received_knowledge = None

    def validate(self, report, meeting_knowledge):
        self.calls += 1
        self.received_report = report
        self.received_knowledge = meeting_knowledge
        return self.result


class FakeReportValidator:
    def __init__(self, result=(True, [])) -> None:
        self.result = result
        self.calls = 0
        self.received_report = None

    def validate(self, report):
        self.calls += 1
        self.received_report = report
        return self.result


def build_prompt() -> Prompt:
    return Prompt(
        content="Prompt global de consolidación.",
        version="meeting_report_consolidation_v1",
    )


def build_meeting_knowledge(
    with_content: bool = True,
) -> MeetingKnowledge:
    return MeetingKnowledge(
        source_chunk_count=2,
        chunks=[
            ChunkKnowledge(
                chunk_index=0,
                start=0.0,
                end=10.0,
                key_points=(
                    ["Se revisó la arquitectura actual del proyecto."]
                    if with_content
                    else []
                ),
            ),
            ChunkKnowledge(
                chunk_index=1,
                start=10.0,
                end=20.0,
                conclusions=(
                    ["Se continuará con las pruebas."]
                    if with_content
                    else []
                ),
            ),
        ],
    )


def build_report() -> MeetingReport:
    return MeetingReport(
        artifact_type="meeting_report",
        provider="ollama",
        model="fake-model",
        prompt_version="meeting_report_consolidation_v1",
        title="Arquitectura y continuidad del proyecto",
        executive_summary=(
            "Se revisó la arquitectura actual del proyecto y se "
            "confirmó la continuidad de las pruebas."
        ),
        key_points=[
            "Se revisó la arquitectura actual del proyecto.",
        ],
    )


def test_service_runs_complete_consolidation_flow() -> None:
    prompt = build_prompt()
    knowledge = build_meeting_knowledge()
    report = build_report()

    provider = FakeProvider()
    schema_loader = FakeSchemaLoader(
        schema={
            "type": "object",
            "required": [
                "title",
                "executive_summary",
                "key_points",
            ],
        }
    )
    parser = FakeParser(result=report)
    grounding_validator = FakeGroundingValidator()
    report_validator = FakeReportValidator()

    service = MeetingReportConsolidationService(
        provider=provider,
        parser=parser,
        schema_loader=schema_loader,
        grounding_validator=grounding_validator,
        report_validator=report_validator,
    )

    result = service.generate(
        prompt=prompt,
        meeting_knowledge=knowledge,
    )

    assert result is report
    assert schema_loader.calls == 1
    assert schema_loader.received_contract == "meeting_report_v1"
    assert provider.calls == 1
    assert provider.received_prompt == prompt.content
    assert provider.received_schema == schema_loader.schema
    assert parser.calls == 1
    assert parser.received_response == provider.response
    assert parser.received_provider == "ollama"
    assert parser.received_model == "fake-model"
    assert (
        parser.received_prompt_version
        == "meeting_report_consolidation_v1"
    )
    assert grounding_validator.calls == 1
    assert grounding_validator.received_report is report
    assert grounding_validator.received_knowledge is knowledge
    assert report_validator.calls == 1
    assert report_validator.received_report is report


def test_service_with_real_parser_and_validators() -> None:
    service = MeetingReportConsolidationService(
        provider=FakeProvider(),
        schema_loader=FakeSchemaLoader(),
    )

    result = service.generate(
        prompt=build_prompt(),
        meeting_knowledge=build_meeting_knowledge(),
    )

    assert isinstance(result, MeetingReport)
    assert result.prompt_version == "meeting_report_consolidation_v1"
    assert result.model == "fake-model"
    assert result.provider == "ollama"


def test_service_uses_meeting_report_schema_not_prompt_contract() -> None:
    schema_loader = FakeSchemaLoader()

    service = MeetingReportConsolidationService(
        provider=FakeProvider(),
        parser=FakeParser(result=build_report()),
        schema_loader=schema_loader,
        grounding_validator=FakeGroundingValidator(),
        report_validator=FakeReportValidator(),
    )

    service.generate(
        prompt=build_prompt(),
        meeting_knowledge=build_meeting_knowledge(),
    )

    assert schema_loader.received_contract == "meeting_report_v1"


def test_service_rejects_invalid_prompt_type() -> None:
    service = MeetingReportConsolidationService(
        provider=FakeProvider(),
        schema_loader=FakeSchemaLoader(),
    )

    with pytest.raises(TypeError, match="instancia de Prompt"):
        service.generate(
            prompt=object(),
            meeting_knowledge=build_meeting_knowledge(),
        )


def test_service_rejects_invalid_meeting_knowledge_type() -> None:
    service = MeetingReportConsolidationService(
        provider=FakeProvider(),
        schema_loader=FakeSchemaLoader(),
    )

    with pytest.raises(TypeError, match="instancia de MeetingKnowledge"):
        service.generate(
            prompt=build_prompt(),
            meeting_knowledge=object(),
        )


def test_service_rejects_wrong_prompt_contract() -> None:
    provider = FakeProvider()
    schema_loader = FakeSchemaLoader()

    service = MeetingReportConsolidationService(
        provider=provider,
        schema_loader=schema_loader,
    )

    with pytest.raises(
        ValueError,
        match="requiere el contrato meeting_report_consolidation_v1",
    ):
        service.generate(
            prompt=Prompt(
                content="Prompt.",
                version="meeting_report_v1",
            ),
            meeting_knowledge=build_meeting_knowledge(),
        )

    assert provider.calls == 0
    assert schema_loader.calls == 0


def test_service_rejects_empty_meeting_knowledge() -> None:
    provider = FakeProvider()
    schema_loader = FakeSchemaLoader()

    service = MeetingReportConsolidationService(
        provider=provider,
        schema_loader=schema_loader,
    )

    with pytest.raises(
        ValueError,
        match="no contiene conocimiento suficiente",
    ):
        service.generate(
            prompt=build_prompt(),
            meeting_knowledge=build_meeting_knowledge(
                with_content=False
            ),
        )

    assert provider.calls == 0
    assert schema_loader.calls == 0


def test_service_rejects_grounding_failure() -> None:
    report_validator = FakeReportValidator()

    service = MeetingReportConsolidationService(
        provider=FakeProvider(),
        parser=FakeParser(result=build_report()),
        schema_loader=FakeSchemaLoader(),
        grounding_validator=FakeGroundingValidator(
            result=(
                False,
                [
                    "action_items elemento #1 contiene evidencia inventada.",
                ],
            )
        ),
        report_validator=report_validator,
    )

    with pytest.raises(ValueError, match="sin grounding válido"):
        service.generate(
            prompt=build_prompt(),
            meeting_knowledge=build_meeting_knowledge(),
        )

    assert report_validator.calls == 0


def test_service_rejects_report_quality_failure() -> None:
    service = MeetingReportConsolidationService(
        provider=FakeProvider(),
        parser=FakeParser(result=build_report()),
        schema_loader=FakeSchemaLoader(),
        grounding_validator=FakeGroundingValidator(),
        report_validator=FakeReportValidator(
            result=(
                False,
                [
                    "El resumen ejecutivo es demasiado corto.",
                ],
            )
        ),
    )

    with pytest.raises(ValueError, match="consolidado inválido"):
        service.generate(
            prompt=build_prompt(),
            meeting_knowledge=build_meeting_knowledge(),
        )


def test_service_propagates_schema_loader_error() -> None:
    provider = FakeProvider()

    service = MeetingReportConsolidationService(
        provider=provider,
        schema_loader=FakeSchemaLoader(
            error=FileNotFoundError("schema ausente")
        ),
    )

    with pytest.raises(FileNotFoundError, match="schema ausente"):
        service.generate(
            prompt=build_prompt(),
            meeting_knowledge=build_meeting_knowledge(),
        )

    assert provider.calls == 0


def test_service_propagates_provider_error() -> None:
    service = MeetingReportConsolidationService(
        provider=FakeProvider(
            error=RuntimeError("provider failure")
        ),
        schema_loader=FakeSchemaLoader(),
    )

    with pytest.raises(RuntimeError, match="provider failure"):
        service.generate(
            prompt=build_prompt(),
            meeting_knowledge=build_meeting_knowledge(),
        )


def test_service_propagates_parser_error() -> None:
    grounding_validator = FakeGroundingValidator()

    service = MeetingReportConsolidationService(
        provider=FakeProvider(),
        parser=FakeParser(
            error=ValueError("invalid structured response")
        ),
        schema_loader=FakeSchemaLoader(),
        grounding_validator=grounding_validator,
        report_validator=FakeReportValidator(),
    )

    with pytest.raises(
        ValueError,
        match="invalid structured response",
    ):
        service.generate(
            prompt=build_prompt(),
            meeting_knowledge=build_meeting_knowledge(),
        )

    assert grounding_validator.calls == 0


def test_service_does_not_mutate_inputs() -> None:
    prompt = build_prompt()
    knowledge = build_meeting_knowledge()

    original_prompt = (prompt.content, prompt.version)
    original_knowledge = knowledge.as_dict()

    service = MeetingReportConsolidationService(
        provider=FakeProvider(),
        schema_loader=FakeSchemaLoader(),
    )

    service.generate(
        prompt=prompt,
        meeting_knowledge=knowledge,
    )

    assert (prompt.content, prompt.version) == original_prompt
    assert knowledge.as_dict() == original_knowledge
