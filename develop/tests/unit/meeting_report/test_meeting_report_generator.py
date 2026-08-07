import pytest

from models.artifacts.meeting_report import MeetingReport
from models.prompt import Prompt
from models.transcript import Transcript
from services.artifact_generator import (
    ArtifactGenerator,
)
from services.meeting_report_generator import (
    MeetingReportGenerator,
)


class FakePromptFormatter:

    def __init__(self) -> None:
        self.received_transcript = None

        self.prompt = Prompt(
            content="Prompt de MeetingReport.",
            version="meeting_report_v1",
        )

    def format(
        self,
        transcript,
    ):
        self.received_transcript = transcript

        return self.prompt


class FakeMeetingReportService:

    def __init__(self) -> None:
        self.received_prompt = None
        self.report = object()

    def generate(
        self,
        prompt,
    ):
        self.received_prompt = prompt

        return self.report


class FakeValidator:

    def __init__(
        self,
        valid: bool = True,
        errors: list[str] | None = None,
    ) -> None:
        self.valid = valid
        self.errors = (
            errors
            if errors is not None
            else []
        )

        self.received_report = None

    def validate(
        self,
        report,
    ):
        self.received_report = report

        return (
            self.valid,
            self.errors,
        )


def build_generator(
    *,
    validator_valid: bool = True,
    validator_errors: list[str] | None = None,
):
    prompt_formatter = FakePromptFormatter()
    meeting_report_service = (
        FakeMeetingReportService()
    )

    validator = FakeValidator(
        valid=validator_valid,
        errors=validator_errors,
    )

    generator = MeetingReportGenerator(
        prompt_formatter=prompt_formatter,
        meeting_report_service=(
            meeting_report_service
        ),
        validator=validator,
    )

    return (
        generator,
        prompt_formatter,
        meeting_report_service,
        validator,
    )


def test_meeting_report_generator_implements_artifact_generator() -> None:
    generator = MeetingReportGenerator()

    assert isinstance(
        generator,
        ArtifactGenerator,
    )


def test_generator_formats_transcript_before_generation() -> None:
    (
        generator,
        prompt_formatter,
        meeting_report_service,
        _,
    ) = build_generator()

    transcript = Transcript()

    generator.generate(
        transcript
    )

    assert (
        prompt_formatter.received_transcript
        is transcript
    )

    assert (
        meeting_report_service.received_prompt
        is prompt_formatter.prompt
    )


def test_generator_validates_generated_report() -> None:
    (
        generator,
        _,
        meeting_report_service,
        validator,
    ) = build_generator()

    generator.generate(
        Transcript()
    )

    assert (
        validator.received_report
        is meeting_report_service.report
    )


def test_generator_returns_valid_report() -> None:
    (
        generator,
        _,
        meeting_report_service,
        _,
    ) = build_generator()

    result = generator.generate(
        Transcript()
    )

    assert (
        result
        is meeting_report_service.report
    )


def test_generator_rejects_invalid_report() -> None:
    (
        generator,
        _,
        _,
        _,
    ) = build_generator(
        validator_valid=False,
        validator_errors=[
            "El resumen ejecutivo es demasiado corto.",
            "La sección contiene duplicados.",
        ],
    )

    with pytest.raises(
        ValueError,
        match="MeetingReport inválido",
    ) as error:
        generator.generate(
            Transcript()
        )

    message = str(
        error.value
    )

    assert (
        "El resumen ejecutivo es demasiado corto."
        in message
    )

    assert (
        "La sección contiene duplicados."
        in message
    )


def test_generator_rejects_invalid_transcript() -> None:
    (
        generator,
        _,
        _,
        _,
    ) = build_generator()

    with pytest.raises(
        TypeError,
        match=(
            "transcript debe ser una instancia "
            "de Transcript"
        ),
    ):
        generator.generate(
            object()
        )


def test_generator_does_not_call_service_when_transcript_is_invalid() -> None:
    (
        generator,
        prompt_formatter,
        meeting_report_service,
        _,
    ) = build_generator()

    with pytest.raises(
        TypeError,
    ):
        generator.generate(
            "transcript inválido"
        )

    assert (
        prompt_formatter.received_transcript
        is None
    )

    assert (
        meeting_report_service.received_prompt
        is None
    )


def test_generator_uses_meeting_report_contract_by_default() -> None:
    generator = MeetingReportGenerator()

    assert (
        generator.prompt_formatter.contract
        == "meeting_report_v1"
    )


def test_generator_declares_meeting_report_return_contract() -> None:
    annotation = (
        MeetingReportGenerator
        .generate
        .__annotations__
        .get(
            "return"
        )
    )

    assert annotation is MeetingReport