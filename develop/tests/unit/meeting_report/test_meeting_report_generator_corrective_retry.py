import pytest

from models.artifacts.meeting_report import MeetingReport
from models.chunk_knowledge import ChunkKnowledge
from models.meeting_knowledge import MeetingKnowledge
from models.prompt import Prompt
from models.transcript import Segment, Transcript
from models.transcript_chunk import TranscriptChunk
from services.meeting_report_generator import (
    MeetingReportGenerator,
)


class SingleChunker:
    def __init__(self) -> None:
        self.chunk_value = TranscriptChunk(
            index=0,
            segments=[
                Segment(
                    start=0.0,
                    end=8.0,
                    speaker="LOCAL",
                    text=(
                        "Se revisó el avance "
                        "general del proyecto."
                    ),
                ),
            ],
        )

    def chunk(
        self,
        transcript,
    ):
        return [
            self.chunk_value,
        ]


class ChunkService:
    def __init__(self) -> None:
        self.calls = 0

    def generate(
        self,
        chunk,
    ):
        self.calls += 1
        return ChunkKnowledge(
            chunk_index=chunk.index,
            start=chunk.start,
            end=chunk.end,
            key_points=[
                (
                    "Se revisó el avance "
                    "general del proyecto."
                ),
            ],
        )


class Assembler:
    def assemble(
        self,
        chunks,
        source_chunk_count,
    ):
        return MeetingKnowledge(
            source_chunk_count=(
                source_chunk_count
            ),
            chunks=list(
                chunks
            ),
        )


class ConsolidationFormatter:
    def __init__(self) -> None:
        self.calls = 0
        self.prompt = Prompt(
            content=(
                "MeetingKnowledge completo."
            ),
            version=(
                "meeting_report_consolidation_v1"
            ),
        )

    def format(
        self,
        meeting_knowledge,
    ):
        self.calls += 1
        return self.prompt


class ConsolidationService:
    def __init__(
        self,
        results,
    ) -> None:
        self.results = list(
            results
        )
        self.calls = 0
        self.received_prompts = []
        self.received_knowledge = []

    def generate(
        self,
        prompt,
        meeting_knowledge,
    ):
        self.received_prompts.append(
            prompt
        )
        self.received_knowledge.append(
            meeting_knowledge
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


def build_transcript() -> Transcript:
    transcript = Transcript()

    transcript.add_segment(
        Segment(
            start=0.0,
            end=8.0,
            speaker="LOCAL",
            text=(
                "Se revisó el avance "
                "general del proyecto."
            ),
        )
    )

    return transcript


def build_report() -> MeetingReport:
    return MeetingReport(
        artifact_type="meeting_report",
        provider="ollama",
        model="fake-model",
        prompt_version=(
            "meeting_report_consolidation_v1"
        ),
        title=(
            "Seguimiento general del proyecto"
        ),
        executive_summary=(
            "Se revisó el avance general del proyecto "
            "y se identificaron los siguientes pasos."
        ),
        key_points=[
            (
                "Se revisó el avance "
                "general del proyecto."
            ),
        ],
    )


def build_generator(
    results,
):
    chunk_service = ChunkService()
    formatter = ConsolidationFormatter()
    service = ConsolidationService(
        results
    )

    generator = MeetingReportGenerator(
        transcript_chunker=SingleChunker(),
        chunk_knowledge_service=(
            chunk_service
        ),
        meeting_knowledge_assembler=Assembler(),
        consolidation_prompt_formatter=(
            formatter
        ),
        consolidation_service=service,
    )

    return (
        generator,
        chunk_service,
        formatter,
        service,
    )


def test_generator_returns_report_on_first_consolidation_attempt() -> None:
    report = build_report()

    (
        generator,
        chunk_service,
        formatter,
        service,
    ) = build_generator(
        [
            report,
        ]
    )

    result = generator.generate(
        build_transcript()
    )

    assert result is report
    assert chunk_service.calls == 1
    assert formatter.calls == 1
    assert service.calls == 1
    assert (
        service.received_prompts[0]
        is formatter.prompt
    )


def test_generator_uses_corrective_prompt_after_consolidation_error() -> None:
    report = build_report()

    (
        generator,
        chunk_service,
        formatter,
        service,
    ) = build_generator(
        [
            ValueError(
                "MeetingReport sin grounding válido: "
                "evidencia inventada."
            ),
            report,
        ]
    )

    result = generator.generate(
        build_transcript()
    )

    assert result is report
    assert chunk_service.calls == 1
    assert formatter.calls == 1
    assert service.calls == 2

    first_prompt = (
        service.received_prompts[0]
    )
    second_prompt = (
        service.received_prompts[1]
    )

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
        "evidencia inventada"
        in second_prompt.content
    )
    assert (
        "No inventes ni modifiques evidencias."
        in second_prompt.content
    )


def test_generator_does_not_repeat_chunk_extraction_on_retry() -> None:
    report = build_report()

    (
        generator,
        chunk_service,
        _,
        service,
    ) = build_generator(
        [
            ValueError(
                "MeetingReport consolidado inválido: "
                "resumen demasiado corto."
            ),
            report,
        ]
    )

    generator.generate(
        build_transcript()
    )

    assert service.calls == 2
    assert chunk_service.calls == 1
    assert (
        service.received_knowledge[0]
        is service.received_knowledge[1]
    )


def test_generator_reports_last_error_after_exhausting_attempts() -> None:
    (
        generator,
        chunk_service,
        _,
        service,
    ) = build_generator(
        [
            ValueError(
                "primer error"
            ),
            ValueError(
                "segundo error"
            ),
        ]
    )

    with pytest.raises(
        ValueError,
        match=(
            "MeetingReport inválido después "
            "de la consolidación"
        ),
    ) as error:
        generator.generate(
            build_transcript()
        )

    assert (
        "segundo error"
        in str(
            error.value
        )
    )
    assert service.calls == 2
    assert chunk_service.calls == 1


def test_corrective_prompt_preserves_consolidation_contract() -> None:
    base_prompt = Prompt(
        content=(
            "MeetingKnowledge original."
        ),
        version=(
            "meeting_report_consolidation_v1"
        ),
    )

    corrected = (
        MeetingReportGenerator
        ._build_corrective_prompt(
            base_prompt=base_prompt,
            errors=[
                (
                    "action_items elemento #1 "
                    "sin grounding."
                ),
            ],
        )
    )

    assert (
        corrected.version
        == "meeting_report_consolidation_v1"
    )
    assert (
        "MeetingKnowledge original."
        in corrected.content
    )
    assert (
        "action_items elemento #1 sin grounding."
        in corrected.content
    )
    assert (
        "misma categoría semántica"
        in corrected.content
    )


def test_corrective_prompt_rejects_invalid_base_prompt() -> None:
    with pytest.raises(
        TypeError,
        match="base_prompt debe ser una instancia",
    ):
        MeetingReportGenerator._build_corrective_prompt(
            base_prompt=object(),
            errors=[],
        )


def test_corrective_prompt_rejects_invalid_errors_collection() -> None:
    with pytest.raises(
        TypeError,
        match="errors debe ser una lista",
    ):
        MeetingReportGenerator._build_corrective_prompt(
            base_prompt=Prompt(
                content="Prompt.",
                version=(
                    "meeting_report_consolidation_v1"
                ),
            ),
            errors=(
                "error",
            ),
        )
