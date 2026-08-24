import pytest

from models.artifacts.meeting_report import MeetingReport
from models.prompt import Prompt
from models.transcript import Transcript
from services.meeting_report_generator import (
    MeetingReportGenerator,
)


class FakePromptFormatter:

    def __init__(self) -> None:
        self.calls = 0
        self.prompt = Prompt(
            content="Prompt original de prueba.",
            version="meeting_report_v1",
        )

    def format(
        self,
        transcript,
    ) -> Prompt:
        self.calls += 1
        return self.prompt


class FakeMeetingReportService:

    def __init__(
        self,
        results,
    ) -> None:
        self.results = list(
            results
        )
        self.calls = 0
        self.received_prompts = []

    def generate(
        self,
        prompt,
    ):
        self.received_prompts.append(
            prompt
        )

        result = self.results[
            self.calls
        ]
        self.calls += 1

        if isinstance(
            result,
            Exception,
        ):
            raise result

        return result


class FakeValidator:

    def __init__(
        self,
        results,
    ) -> None:
        self.results = list(
            results
        )
        self.calls = 0

    def validate(
        self,
        report,
    ):
        result = self.results[
            self.calls
        ]
        self.calls += 1
        return result


def build_transcript() -> Transcript:
    return Transcript()


def build_report() -> MeetingReport:
    return MeetingReport(
        artifact_type="meeting_report",
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
        title="Reunión técnica",
        executive_summary=(
            "Se revisó el estado general del proyecto "
            "y se acordaron los próximos pasos."
        ),
        key_points=[
            "Se revisó el estado general del proyecto.",
        ],
    )


def test_generator_returns_valid_report_on_first_attempt() -> None:
    report = build_report()

    formatter = FakePromptFormatter()
    service = FakeMeetingReportService(
        [
            report,
        ]
    )
    validator = FakeValidator(
        [
            (
                True,
                [],
            ),
        ]
    )

    generator = MeetingReportGenerator(
        prompt_formatter=formatter,
        meeting_report_service=service,
        validator=validator,
    )

    result = generator.generate(
        build_transcript()
    )

    assert result is report
    assert formatter.calls == 1
    assert service.calls == 1
    assert validator.calls == 1

    assert (
        service.received_prompts[0]
        is formatter.prompt
    )


def test_generator_uses_corrective_prompt_after_domain_error() -> None:
    report = build_report()

    formatter = FakePromptFormatter()

    service = FakeMeetingReportService(
        [
            ValueError(
                "MeetingReport title no puede estar vacío."
            ),
            report,
        ]
    )

    validator = FakeValidator(
        [
            (
                True,
                [],
            ),
        ]
    )

    generator = MeetingReportGenerator(
        prompt_formatter=formatter,
        meeting_report_service=service,
        validator=validator,
    )

    result = generator.generate(
        build_transcript()
    )

    assert result is report
    assert service.calls == 2

    first_prompt = service.received_prompts[0]
    second_prompt = service.received_prompts[1]

    assert first_prompt is formatter.prompt
    assert second_prompt is not first_prompt

    assert (
        second_prompt.version
        == first_prompt.version
    )

    assert (
        first_prompt.content
        in second_prompt.content
    )

    assert (
        "MeetingReport title no puede estar vacío."
        in second_prompt.content
    )

    assert (
        "Genera nuevamente TODO el documento desde cero."
        in second_prompt.content
    )


def test_generator_uses_corrective_prompt_after_validator_failure() -> None:
    first_report = build_report()
    second_report = build_report()

    service = FakeMeetingReportService(
        [
            first_report,
            second_report,
        ]
    )

    validator = FakeValidator(
        [
            (
                False,
                [
                    "El título es demasiado corto.",
                ],
            ),
            (
                True,
                [],
            ),
        ]
    )

    generator = MeetingReportGenerator(
        prompt_formatter=FakePromptFormatter(),
        meeting_report_service=service,
        validator=validator,
    )

    result = generator.generate(
        build_transcript()
    )

    assert result is second_report
    assert service.calls == 2
    assert validator.calls == 2

    corrective_prompt = (
        service.received_prompts[1]
    )

    assert (
        "El título es demasiado corto."
        in corrective_prompt.content
    )


def test_generator_reports_invalid_after_exhausting_attempts() -> None:
    service = FakeMeetingReportService(
        [
            ValueError(
                "MeetingReport title no puede estar vacío."
            ),
            ValueError(
                "MeetingReport executive_summary "
                "no puede estar vacío."
            ),
        ]
    )

    generator = MeetingReportGenerator(
        prompt_formatter=FakePromptFormatter(),
        meeting_report_service=service,
        validator=FakeValidator(
            []
        ),
    )

    with pytest.raises(
        ValueError,
        match="MeetingReport inválido:",
    ) as error:
        generator.generate(
            build_transcript()
        )

    assert (
        "executive_summary"
        in str(
            error.value
        )
    )

    assert service.calls == 2


def test_corrective_prompt_preserves_contract_version() -> None:
    base_prompt = Prompt(
        content="Contenido original.",
        version="meeting_report_v1",
    )

    corrected = (
        MeetingReportGenerator
        ._build_corrective_prompt(
            base_prompt=base_prompt,
            errors=[
                "El título está vacío.",
            ],
        )
    )

    assert corrected.version == "meeting_report_v1"
    assert "Contenido original." in corrected.content
    assert "El título está vacío." in corrected.content


def test_generator_rejects_non_transcript() -> None:
    generator = MeetingReportGenerator(
        prompt_formatter=FakePromptFormatter(),
        meeting_report_service=FakeMeetingReportService(
            []
        ),
        validator=FakeValidator(
            []
        ),
    )

    with pytest.raises(
        TypeError,
        match="transcript debe ser una instancia",
    ):
        generator.generate(
            object()
        )
