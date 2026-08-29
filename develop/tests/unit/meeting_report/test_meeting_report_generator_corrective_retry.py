import pytest

from models.artifacts.meeting_report import MeetingReport
from models.chunk_knowledge import ChunkKnowledge
from models.meeting_knowledge import MeetingKnowledge
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
    def __init__(self) -> None:
        self.calls = 0
        self.result = None

    def assemble(
        self,
        chunks,
        source_chunk_count,
    ):
        self.calls += 1
        self.result = MeetingKnowledge(
            source_chunk_count=(
                source_chunk_count
            ),
            chunks=list(
                chunks
            ),
        )
        return self.result


class ConsolidationService:
    def __init__(
        self,
        results,
    ) -> None:
        self.results = list(
            results
        )
        self.calls = 0
        self.received_knowledge = []

    def generate(
        self,
        meeting_knowledge,
    ):
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
            "meeting_report_global_staged_v1"
        ),
        title=(
            "Avance general del proyecto"
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
    assembler = Assembler()
    service = ConsolidationService(
        results
    )

    generator = MeetingReportGenerator(
        transcript_chunker=SingleChunker(),
        chunk_knowledge_service=(
            chunk_service
        ),
        meeting_knowledge_assembler=(
            assembler
        ),
        consolidation_service=service,
    )

    return (
        generator,
        chunk_service,
        assembler,
        service,
    )


def test_generator_returns_report_on_first_staged_consolidation_attempt() -> None:
    report = build_report()

    (
        generator,
        chunk_service,
        assembler,
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
    assert assembler.calls == 1
    assert service.calls == 1


def test_generator_retries_complete_staged_consolidation_after_value_error() -> None:
    report = build_report()

    (
        generator,
        chunk_service,
        assembler,
        service,
    ) = build_generator(
        [
            ValueError(
                "G2 narrative failure"
            ),
            report,
        ]
    )

    result = generator.generate(
        build_transcript()
    )

    assert result is report
    assert chunk_service.calls == 1
    assert assembler.calls == 1
    assert service.calls == 2

    assert (
        service.received_knowledge[
            0
        ]
        is service.received_knowledge[
            1
        ]
    )

    assert (
        service.received_knowledge[
            0
        ]
        is assembler.result
    )


def test_generator_does_not_repeat_chunk_extraction_on_global_retry() -> None:
    report = build_report()

    (
        generator,
        chunk_service,
        assembler,
        service,
    ) = build_generator(
        [
            ValueError(
                "G1 semantic failure"
            ),
            report,
        ]
    )

    generator.generate(
        build_transcript()
    )

    assert service.calls == 2
    assert chunk_service.calls == 1
    assert assembler.calls == 1


def test_generator_reports_last_staged_error_after_exhausting_attempts() -> None:
    (
        generator,
        chunk_service,
        assembler,
        service,
    ) = build_generator(
        [
            ValueError(
                "primer error staged"
            ),
            ValueError(
                "segundo error staged"
            ),
        ]
    )

    with pytest.raises(
        ValueError,
        match=(
            "MeetingReport inválido después "
            "de la consolidación staged"
        ),
    ) as error:
        generator.generate(
            build_transcript()
        )

    assert (
        "segundo error staged"
        in str(
            error.value
        )
    )
    assert service.calls == 2
    assert chunk_service.calls == 1
    assert assembler.calls == 1


def test_generator_does_not_retry_non_value_error_infrastructure_failure() -> None:
    (
        generator,
        chunk_service,
        assembler,
        service,
    ) = build_generator(
        [
            RuntimeError(
                "provider unavailable"
            ),
        ]
    )

    with pytest.raises(
        RuntimeError,
        match="provider unavailable",
    ):
        generator.generate(
            build_transcript()
        )

    assert service.calls == 1
    assert chunk_service.calls == 1
    assert assembler.calls == 1


def test_generator_has_no_legacy_corrective_prompt_builder() -> None:
    assert not hasattr(
        MeetingReportGenerator,
        "_build_corrective_prompt",
    )
