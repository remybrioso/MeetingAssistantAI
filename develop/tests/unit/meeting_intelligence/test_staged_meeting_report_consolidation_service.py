import pytest

from models.artifacts.meeting_report import (
    MeetingReport,
)
from models.chunk_classification import (
    ChunkKnowledgeKind,
)
from models.chunk_knowledge import ChunkKnowledge
from models.meeting_knowledge import (
    MeetingKnowledge,
)
from models.meeting_report_narrative import (
    GroundedNarrativeText,
    MeetingReportNarrative,
)
from models.meeting_semantic_consolidation import (
    ConsolidatedMeetingKnowledgeItem,
    MeetingKnowledgeItemReference,
    MeetingSemanticConsolidation,
)
from models.prompt import Prompt
from services.meeting_semantic_consolidation_parser import (
    CrossItemSourceReferenceReuseError,
)
from services.staged_meeting_report_consolidation_service import (
    StagedMeetingReportConsolidationService,
)


class FakeProvider:
    def __init__(
        self,
        responses=None,
        error_on_call: int | None = None,
        model: object = "fake-model",
    ) -> None:
        self.responses = (
            list(responses)
            if responses is not None
            else [
                "semantic-response",
                "narrative-response",
            ]
        )
        self.error_on_call = (
            error_on_call
        )
        self.model = model
        self.calls = []

    def generate(
        self,
        prompt,
        output_schema,
    ):
        call_number = (
            len(self.calls)
            + 1
        )

        self.calls.append(
            (
                prompt,
                output_schema,
            )
        )

        if (
            self.error_on_call
            == call_number
        ):
            raise RuntimeError(
                f"provider failure #{call_number}"
            )

        return self.responses[
            call_number - 1
        ]


class FakeSchemaLoader:
    def __init__(
        self,
        schemas=None,
        error_on_contract: str | None = None,
    ) -> None:
        self.schemas = (
            dict(schemas)
            if schemas is not None
            else {
                "meeting_semantic_consolidation_v1": {
                    "schema": "semantic",
                },
                "meeting_report_narrative_v1": {
                    "schema": "narrative",
                },
            }
        )
        self.error_on_contract = (
            error_on_contract
        )
        self.calls = []

    def load(
        self,
        contract,
    ):
        self.calls.append(
            contract
        )

        if (
            contract
            == self.error_on_contract
        ):
            raise FileNotFoundError(
                f"schema ausente: {contract}"
            )

        return self.schemas[
            contract
        ]


class FakeSemanticFormatter:
    def __init__(
        self,
        result=None,
        error=None,
    ) -> None:
        self.result = (
            result
            if result is not None
            else Prompt(
                content="semantic-prompt",
                version=(
                    "meeting_semantic_consolidation_v1"
                ),
            )
        )
        self.error = error
        self.calls = 0
        self.received = None

    def format(
        self,
        meeting_knowledge,
    ):
        self.calls += 1
        self.received = (
            meeting_knowledge
        )

        if self.error is not None:
            raise self.error

        return self.result


class FakeNarrativeFormatter:
    def __init__(
        self,
        result=None,
        error=None,
    ) -> None:
        self.result = (
            result
            if result is not None
            else Prompt(
                content="narrative-prompt",
                version=(
                    "meeting_report_narrative_v1"
                ),
            )
        )
        self.error = error
        self.calls = 0
        self.received = None

    def format(
        self,
        semantic_consolidation,
    ):
        self.calls += 1
        self.received = (
            semantic_consolidation
        )

        if self.error is not None:
            raise self.error

        return self.result


class FakeSemanticParser:
    def __init__(
        self,
        result=None,
        error=None,
    ) -> None:
        self.result = (
            result
            if result is not None
            else build_semantic_consolidation()
        )
        self.error = error
        self.calls = 0
        self.received_response = None
        self.received_knowledge = None

    def parse(
        self,
        response,
        meeting_knowledge,
    ):
        self.calls += 1
        self.received_response = (
            response
        )
        self.received_knowledge = (
            meeting_knowledge
        )

        if self.error is not None:
            raise self.error

        return self.result


class FakeSemanticCoverageService:
    def __init__(
        self,
        result=None,
        identity_result=None,
        error=None,
    ) -> None:
        self.result = result
        self.identity_result = (
            identity_result
            if identity_result is not None
            else build_semantic_consolidation()
        )
        self.error = error
        self.calls = 0
        self.identity_calls = 0
        self.received_semantic = None
        self.received_knowledge = None
        self.identity_received_knowledge = None

    def reconcile(
        self,
        semantic_consolidation,
        meeting_knowledge,
    ):
        self.calls += 1
        self.received_semantic = (
            semantic_consolidation
        )
        self.received_knowledge = (
            meeting_knowledge
        )

        if self.error is not None:
            raise self.error

        return (
            self.result
            if self.result is not None
            else semantic_consolidation
        )

    def build_identity_consolidation(
        self,
        meeting_knowledge,
    ):
        self.identity_calls += 1
        self.identity_received_knowledge = (
            meeting_knowledge
        )

        if self.error is not None:
            raise self.error

        return self.identity_result


class FakeLogger:
    def __init__(self) -> None:
        self.warnings = []

    def warning(
        self,
        message,
    ) -> None:
        self.warnings.append(
            message
        )


class FakeNarrativeParser:
    def __init__(
        self,
        result=None,
        error=None,
    ) -> None:
        self.result = (
            result
            if result is not None
            else build_narrative()
        )
        self.error = error
        self.calls = 0
        self.received_response = None
        self.received_semantic = None

    def parse(
        self,
        response,
        semantic_consolidation,
    ):
        self.calls += 1
        self.received_response = (
            response
        )
        self.received_semantic = (
            semantic_consolidation
        )

        if self.error is not None:
            raise self.error

        return self.result


class FakeAssembler:
    def __init__(
        self,
        result=None,
        error=None,
    ) -> None:
        self.result = (
            result
            if result is not None
            else build_report()
        )
        self.error = error
        self.calls = 0
        self.received = None

    def assemble(
        self,
        **kwargs,
    ):
        self.calls += 1
        self.received = kwargs

        if self.error is not None:
            raise self.error

        return self.result


class FakeGroundingValidator:
    def __init__(
        self,
        result=(True, []),
    ) -> None:
        self.result = result
        self.calls = 0
        self.received_report = None
        self.received_knowledge = None

    def validate(
        self,
        report,
        meeting_knowledge,
    ):
        self.calls += 1
        self.received_report = report
        self.received_knowledge = (
            meeting_knowledge
        )
        return self.result


class FakeReportValidator:
    def __init__(
        self,
        result=(True, []),
    ) -> None:
        self.result = result
        self.calls = 0
        self.received_report = None

    def validate(
        self,
        report,
    ):
        self.calls += 1
        self.received_report = report
        return self.result


def ref(
    chunk_index: int = 0,
    item_index: int = 0,
) -> MeetingKnowledgeItemReference:
    return MeetingKnowledgeItemReference(
        chunk_index=chunk_index,
        item_index=item_index,
    )


def build_meeting_knowledge(
    with_content: bool = True,
) -> MeetingKnowledge:
    if with_content:
        return MeetingKnowledge(
            source_chunk_count=1,
            chunks=[
                ChunkKnowledge(
                    chunk_index=0,
                    start=0.0,
                    end=10.0,
                    key_points=[
                        "Contenido de prueba."
                    ],
                ),
            ],
        )

    return MeetingKnowledge(
        source_chunk_count=1,
        chunks=[
            ChunkKnowledge(
                chunk_index=0,
                start=0.0,
                end=10.0,
            ),
        ],
    )


def build_semantic_consolidation() -> MeetingSemanticConsolidation:
    return MeetingSemanticConsolidation(
        items=[
            ConsolidatedMeetingKnowledgeItem(
                kind=(
                    ChunkKnowledgeKind.TOPIC
                ),
                description=(
                    "Arquitectura del servicio."
                ),
                source_refs=[
                    ref()
                ],
            ),
        ]
    )


def grounded(
    text: str,
) -> GroundedNarrativeText:
    return GroundedNarrativeText(
        text=text,
        source_item_ids=[
            0
        ],
    )


def build_narrative() -> MeetingReportNarrative:
    return MeetingReportNarrative(
        title=grounded(
            "Arquitectura del servicio"
        ),
        objective=None,
        executive_summary=grounded(
            "Se revisó la arquitectura general del servicio."
        ),
        key_points=[
            grounded(
                "Se revisó la arquitectura del servicio."
            )
        ],
    )


def build_report() -> MeetingReport:
    return MeetingReport(
        artifact_type="meeting_report",
        provider="ollama",
        model="fake-model",
        prompt_version=(
            "meeting_report_global_staged_v1"
        ),
        title="Arquitectura del servicio",
        executive_summary=(
            "Se revisó la arquitectura general del servicio."
        ),
        key_points=[
            "Se revisó la arquitectura del servicio."
        ],
    )


def build_service(
    **overrides,
) -> StagedMeetingReportConsolidationService:
    dependencies = {
        "provider": FakeProvider(),
        "semantic_prompt_formatter": (
            FakeSemanticFormatter()
        ),
        "semantic_parser": (
            FakeSemanticParser()
        ),
        "semantic_coverage_service": (
            FakeSemanticCoverageService()
        ),
        "narrative_prompt_formatter": (
            FakeNarrativeFormatter()
        ),
        "narrative_parser": (
            FakeNarrativeParser()
        ),
        "report_assembler": (
            FakeAssembler()
        ),
        "schema_loader": (
            FakeSchemaLoader()
        ),
        "grounding_validator": (
            FakeGroundingValidator()
        ),
        "report_validator": (
            FakeReportValidator()
        ),
        "logger": FakeLogger(),
    }

    dependencies.update(
        overrides
    )

    return (
        StagedMeetingReportConsolidationService(
            **dependencies
        )
    )


def test_service_runs_complete_two_call_pipeline() -> None:
    provider = FakeProvider()
    semantic_formatter = (
        FakeSemanticFormatter()
    )
    semantic_parser = (
        FakeSemanticParser()
    )
    semantic_coverage_result = (
        build_semantic_consolidation()
    )
    semantic_coverage_service = (
        FakeSemanticCoverageService(
            result=(
                semantic_coverage_result
            )
        )
    )
    narrative_formatter = (
        FakeNarrativeFormatter()
    )
    narrative_parser = (
        FakeNarrativeParser()
    )
    assembler = FakeAssembler()
    schema_loader = FakeSchemaLoader()
    grounding_validator = (
        FakeGroundingValidator()
    )
    report_validator = (
        FakeReportValidator()
    )

    service = build_service(
        provider=provider,
        semantic_prompt_formatter=(
            semantic_formatter
        ),
        semantic_parser=semantic_parser,
        semantic_coverage_service=(
            semantic_coverage_service
        ),
        narrative_prompt_formatter=(
            narrative_formatter
        ),
        narrative_parser=(
            narrative_parser
        ),
        report_assembler=assembler,
        schema_loader=schema_loader,
        grounding_validator=(
            grounding_validator
        ),
        report_validator=(
            report_validator
        ),
    )

    knowledge = (
        build_meeting_knowledge()
    )

    result = service.generate(
        knowledge
    )

    assert result is assembler.result

    assert len(
        provider.calls
    ) == 2

    assert provider.calls == [
        (
            "semantic-prompt",
            {
                "schema": "semantic",
            },
        ),
        (
            "narrative-prompt",
            {
                "schema": "narrative",
            },
        ),
    ]

    assert schema_loader.calls == [
        "meeting_semantic_consolidation_v1",
        "meeting_report_narrative_v1",
    ]

    assert semantic_formatter.calls == 1
    assert (
        semantic_formatter.received
        is knowledge
    )

    assert semantic_parser.calls == 1
    assert (
        semantic_parser.received_response
        == "semantic-response"
    )
    assert (
        semantic_parser.received_knowledge
        is knowledge
    )

    assert (
        semantic_coverage_service.calls
        == 1
    )
    assert (
        semantic_coverage_service.received_semantic
        is semantic_parser.result
    )
    assert (
        semantic_coverage_service.received_knowledge
        is knowledge
    )

    assert narrative_formatter.calls == 1
    assert (
        narrative_formatter.received
        is semantic_coverage_result
    )

    assert narrative_parser.calls == 1
    assert (
        narrative_parser.received_response
        == "narrative-response"
    )
    assert (
        narrative_parser.received_semantic
        is semantic_coverage_result
    )

    assert assembler.calls == 1
    assert (
        assembler.received[
            "meeting_knowledge"
        ]
        is knowledge
    )
    assert (
        assembler.received[
            "semantic_consolidation"
        ]
        is semantic_coverage_result
    )
    assert (
        assembler.received[
            "narrative"
        ]
        is narrative_parser.result
    )
    assert (
        assembler.received[
            "provider"
        ]
        == "ollama"
    )
    assert (
        assembler.received[
            "model"
        ]
        == "fake-model"
    )
    assert (
        assembler.received[
            "prompt_version"
        ]
        == "meeting_report_global_staged_v1"
    )

    assert grounding_validator.calls == 1
    assert (
        grounding_validator.received_report
        is result
    )
    assert (
        grounding_validator.received_knowledge
        is knowledge
    )

    assert report_validator.calls == 1
    assert (
        report_validator.received_report
        is result
    )


def test_service_uses_identity_fallback_for_cross_item_reuse() -> None:
    provider = FakeProvider()
    knowledge = build_meeting_knowledge()
    identity_result = build_semantic_consolidation()
    semantic_coverage_service = (
        FakeSemanticCoverageService(
            identity_result=identity_result
        )
    )
    narrative_formatter = (
        FakeNarrativeFormatter()
    )
    narrative_parser = (
        FakeNarrativeParser()
    )
    assembler = FakeAssembler()
    logger = FakeLogger()

    service = build_service(
        provider=provider,
        semantic_parser=(
            FakeSemanticParser(
                error=(
                    CrossItemSourceReferenceReuseError(
                        [
                            (
                                "risk",
                                3,
                                0,
                            )
                        ]
                    )
                )
            )
        ),
        semantic_coverage_service=(
            semantic_coverage_service
        ),
        narrative_prompt_formatter=(
            narrative_formatter
        ),
        narrative_parser=narrative_parser,
        report_assembler=assembler,
        logger=logger,
    )

    result = service.generate(
        knowledge
    )

    assert result is assembler.result
    assert len(provider.calls) == 2
    assert semantic_coverage_service.calls == 0
    assert (
        semantic_coverage_service.identity_calls
        == 1
    )
    assert (
        semantic_coverage_service
        .identity_received_knowledge
        is knowledge
    )
    assert narrative_formatter.received is identity_result
    assert (
        narrative_parser.received_semantic
        is identity_result
    )
    assert (
        assembler.received[
            "semantic_consolidation"
        ]
        is identity_result
    )
    assert len(logger.warnings) == 1
    assert "G1 fue descartada" in logger.warnings[0]
    assert (
        "referencias fuente reutilizadas"
        in logger.warnings[0]
    )
    assert "('risk', 3, 0)" in logger.warnings[0]
    assert (
        "consolidación de identidad determinista"
        in logger.warnings[0]
    )


def test_service_rejects_invalid_meeting_knowledge_type() -> None:
    provider = FakeProvider()

    service = build_service(
        provider=provider
    )

    with pytest.raises(
        TypeError,
        match="MeetingKnowledge",
    ):
        service.generate(
            object()
        )

    assert provider.calls == []


def test_service_rejects_empty_meeting_knowledge() -> None:
    provider = FakeProvider()

    service = build_service(
        provider=provider
    )

    with pytest.raises(
        ValueError,
        match="no contiene conocimiento suficiente",
    ):
        service.generate(
            build_meeting_knowledge(
                with_content=False
            )
        )

    assert provider.calls == []


def test_service_rejects_wrong_semantic_prompt_contract() -> None:
    provider = FakeProvider()
    schema_loader = FakeSchemaLoader()

    service = build_service(
        provider=provider,
        schema_loader=schema_loader,
        semantic_prompt_formatter=(
            FakeSemanticFormatter(
                result=Prompt(
                    content="semantic-prompt",
                    version="wrong-contract",
                )
            )
        ),
    )

    with pytest.raises(
        ValueError,
        match="meeting_semantic_consolidation_v1",
    ):
        service.generate(
            build_meeting_knowledge()
        )

    assert provider.calls == []
    assert schema_loader.calls == []


def test_service_rejects_wrong_narrative_prompt_contract() -> None:
    provider = FakeProvider()
    schema_loader = FakeSchemaLoader()

    service = build_service(
        provider=provider,
        schema_loader=schema_loader,
        narrative_prompt_formatter=(
            FakeNarrativeFormatter(
                result=Prompt(
                    content="narrative-prompt",
                    version="wrong-contract",
                )
            )
        ),
    )

    with pytest.raises(
        ValueError,
        match="meeting_report_narrative_v1",
    ):
        service.generate(
            build_meeting_knowledge()
        )

    assert len(
        provider.calls
    ) == 1
    assert schema_loader.calls == [
        "meeting_semantic_consolidation_v1",
    ]


def test_service_rejects_non_prompt_semantic_formatter_result() -> None:
    provider = FakeProvider()

    service = build_service(
        provider=provider,
        semantic_prompt_formatter=(
            FakeSemanticFormatter(
                result="not-prompt"
            )
        ),
    )

    with pytest.raises(
        TypeError,
        match="instancia de Prompt",
    ):
        service.generate(
            build_meeting_knowledge()
        )

    assert provider.calls == []


def test_service_rejects_non_prompt_narrative_formatter_result() -> None:
    provider = FakeProvider()

    service = build_service(
        provider=provider,
        narrative_prompt_formatter=(
            FakeNarrativeFormatter(
                result="not-prompt"
            )
        ),
    )

    with pytest.raises(
        TypeError,
        match="instancia de Prompt",
    ):
        service.generate(
            build_meeting_knowledge()
        )

    assert len(
        provider.calls
    ) == 1


@pytest.mark.parametrize(
    "error_on_contract",
    [
        "meeting_semantic_consolidation_v1",
        "meeting_report_narrative_v1",
    ],
)
def test_service_propagates_schema_loader_errors(
    error_on_contract: str,
) -> None:
    provider = FakeProvider()

    service = build_service(
        provider=provider,
        schema_loader=FakeSchemaLoader(
            error_on_contract=(
                error_on_contract
            )
        ),
    )

    with pytest.raises(
        FileNotFoundError,
        match="schema ausente",
    ):
        service.generate(
            build_meeting_knowledge()
        )

    expected_provider_calls = (
        0
        if error_on_contract
        == "meeting_semantic_consolidation_v1"
        else 1
    )

    assert (
        len(
            provider.calls
        )
        == expected_provider_calls
    )


@pytest.mark.parametrize(
    "error_on_call",
    [
        1,
        2,
    ],
)
def test_service_propagates_provider_errors(
    error_on_call: int,
) -> None:
    provider = FakeProvider(
        error_on_call=error_on_call
    )

    service = build_service(
        provider=provider
    )

    with pytest.raises(
        RuntimeError,
        match=(
            f"provider failure #{error_on_call}"
        ),
    ):
        service.generate(
            build_meeting_knowledge()
        )

    assert (
        len(
            provider.calls
        )
        == error_on_call
    )


def test_service_propagates_semantic_parser_error() -> None:
    provider = FakeProvider()
    semantic_coverage_service = (
        FakeSemanticCoverageService()
    )
    logger = FakeLogger()

    service = build_service(
        provider=provider,
        semantic_parser=(
            FakeSemanticParser(
                error=ValueError(
                    "semantic parse failure"
                )
            )
        ),
        semantic_coverage_service=(
            semantic_coverage_service
        ),
        logger=logger,
    )

    with pytest.raises(
        ValueError,
        match="semantic parse failure",
    ):
        service.generate(
            build_meeting_knowledge()
        )

    assert len(
        provider.calls
    ) == 1
    assert semantic_coverage_service.calls == 0
    assert (
        semantic_coverage_service.identity_calls
        == 0
    )
    assert logger.warnings == []


def test_service_propagates_semantic_coverage_error() -> None:
    provider = FakeProvider()
    narrative_formatter = (
        FakeNarrativeFormatter()
    )

    service = build_service(
        provider=provider,
        semantic_coverage_service=(
            FakeSemanticCoverageService(
                error=ValueError(
                    "semantic coverage failure"
                )
            )
        ),
        narrative_prompt_formatter=(
            narrative_formatter
        ),
    )

    with pytest.raises(
        ValueError,
        match="semantic coverage failure",
    ):
        service.generate(
            build_meeting_knowledge()
        )

    assert len(
        provider.calls
    ) == 1
    assert narrative_formatter.calls == 0


def test_service_propagates_narrative_parser_error() -> None:
    provider = FakeProvider()

    service = build_service(
        provider=provider,
        narrative_parser=(
            FakeNarrativeParser(
                error=ValueError(
                    "narrative parse failure"
                )
            )
        ),
    )

    with pytest.raises(
        ValueError,
        match="narrative parse failure",
    ):
        service.generate(
            build_meeting_knowledge()
        )

    assert len(
        provider.calls
    ) == 2


def test_service_propagates_assembler_error() -> None:
    provider = FakeProvider()

    service = build_service(
        provider=provider,
        report_assembler=(
            FakeAssembler(
                error=ValueError(
                    "assembler failure"
                )
            )
        ),
    )

    with pytest.raises(
        ValueError,
        match="assembler failure",
    ):
        service.generate(
            build_meeting_knowledge()
        )

    assert len(
        provider.calls
    ) == 2


def test_service_rejects_grounding_failure_before_quality() -> None:
    report_validator = (
        FakeReportValidator()
    )

    service = build_service(
        grounding_validator=(
            FakeGroundingValidator(
                result=(
                    False,
                    [
                        (
                            "evidencia global "
                            "inválida"
                        )
                    ],
                )
            )
        ),
        report_validator=(
            report_validator
        ),
    )

    with pytest.raises(
        ValueError,
        match="grounding válido",
    ):
        service.generate(
            build_meeting_knowledge()
        )

    assert report_validator.calls == 0


def test_service_rejects_quality_failure() -> None:
    service = build_service(
        report_validator=(
            FakeReportValidator(
                result=(
                    False,
                    [
                        (
                            "resumen ejecutivo "
                            "demasiado corto"
                        )
                    ],
                )
            )
        ),
    )

    with pytest.raises(
        ValueError,
        match="consolidado es inválido",
    ):
        service.generate(
            build_meeting_knowledge()
        )


@pytest.mark.parametrize(
    "model",
    [
        None,
        3,
        "",
        "   ",
    ],
)
def test_service_rejects_invalid_provider_model(
    model,
) -> None:
    service = build_service(
        provider=FakeProvider(
            model=model
        )
    )

    expected_error = (
        TypeError
        if not isinstance(
            model,
            str,
        )
        else ValueError
    )

    with pytest.raises(
        expected_error
    ):
        service.generate(
            build_meeting_knowledge()
        )


def test_service_propagates_semantic_formatter_error() -> None:
    service = build_service(
        semantic_prompt_formatter=(
            FakeSemanticFormatter(
                error=RuntimeError(
                    "semantic formatter failure"
                )
            )
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="semantic formatter failure",
    ):
        service.generate(
            build_meeting_knowledge()
        )


def test_service_propagates_narrative_formatter_error() -> None:
    provider = FakeProvider()

    service = build_service(
        provider=provider,
        narrative_prompt_formatter=(
            FakeNarrativeFormatter(
                error=RuntimeError(
                    "narrative formatter failure"
                )
            )
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="narrative formatter failure",
    ):
        service.generate(
            build_meeting_knowledge()
        )

    assert len(
        provider.calls
    ) == 1


def test_service_does_not_mutate_meeting_knowledge() -> None:
    knowledge = (
        build_meeting_knowledge()
    )
    original = knowledge.as_dict()

    service = build_service()

    service.generate(
        knowledge
    )

    assert (
        knowledge.as_dict()
        == original
    )
