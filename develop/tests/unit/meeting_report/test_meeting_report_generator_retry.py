import pytest

from models.artifacts.meeting_report import MeetingReport
from models.chunk_knowledge import ChunkKnowledge
from models.meeting_knowledge import MeetingKnowledge
from models.transcript import Segment, Transcript
from models.transcript_chunk import TranscriptChunk
from services.meeting_report_generator import (
    MeetingReportGenerator,
)


class FakeTranscriptChunker:
    def __init__(
        self,
        chunks,
    ) -> None:
        self.chunks = list(
            chunks
        )
        self.calls = 0
        self.received_transcript = None

    def chunk(
        self,
        transcript,
    ):
        self.calls += 1
        self.received_transcript = transcript
        return list(
            self.chunks
        )


class FakeChunkKnowledgeService:
    def __init__(
        self,
        results,
        error_at_index=None,
        error=None,
    ) -> None:
        self.results = dict(
            results
        )
        self.error_at_index = (
            error_at_index
        )
        self.error = error
        self.calls = []

    def generate(
        self,
        chunk,
    ):
        self.calls.append(
            chunk
        )

        if (
            self.error_at_index
            == chunk.index
        ):
            raise (
                self.error
                if self.error is not None
                else ValueError(
                    "chunk inválido"
                )
            )

        return self.results[
            chunk.index
        ]


class FakeMeetingKnowledgeAssembler:
    def __init__(
        self,
        result,
    ) -> None:
        self.result = result
        self.calls = 0
        self.received_chunks = None
        self.received_source_chunk_count = None

    def assemble(
        self,
        chunks,
        source_chunk_count,
    ):
        self.calls += 1
        self.received_chunks = list(
            chunks
        )
        self.received_source_chunk_count = (
            source_chunk_count
        )
        return self.result


class FakeConsolidationService:
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
            end=5.0,
            speaker="LOCAL",
            text=(
                "Se revisó el estado inicial "
                "del proyecto."
            ),
        )
    )

    transcript.add_segment(
        Segment(
            start=5.0,
            end=10.0,
            speaker="REMOTE",
            text=(
                "Se acordó continuar "
                "con las pruebas."
            ),
        )
    )

    return transcript


def build_chunks() -> list[TranscriptChunk]:
    return [
        TranscriptChunk(
            index=0,
            segments=[
                Segment(
                    start=0.0,
                    end=5.0,
                    speaker="LOCAL",
                    text=(
                        "Se revisó el estado inicial "
                        "del proyecto."
                    ),
                ),
            ],
        ),
        TranscriptChunk(
            index=1,
            segments=[
                Segment(
                    start=5.0,
                    end=10.0,
                    speaker="REMOTE",
                    text=(
                        "Se acordó continuar "
                        "con las pruebas."
                    ),
                ),
            ],
        ),
    ]


def build_chunk_knowledge():
    return {
        0: ChunkKnowledge(
            chunk_index=0,
            start=0.0,
            end=5.0,
            key_points=[
                (
                    "Se revisó el estado inicial "
                    "del proyecto."
                ),
            ],
        ),
        1: ChunkKnowledge(
            chunk_index=1,
            start=5.0,
            end=10.0,
            conclusions=[
                (
                    "Se continuará con las pruebas."
                ),
            ],
        ),
    }


def build_meeting_knowledge() -> MeetingKnowledge:
    values = build_chunk_knowledge()

    return MeetingKnowledge(
        source_chunk_count=2,
        chunks=[
            values[0],
            values[1],
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
        title=(
            "Estado y continuidad del proyecto"
        ),
        executive_summary=(
            "Se revisó el estado inicial del proyecto "
            "y se confirmó la continuidad de las pruebas."
        ),
        key_points=[
            (
                "Se revisó el estado inicial "
                "del proyecto."
            ),
        ],
    )


def build_generator(
    consolidation_results=None,
):
    chunks = build_chunks()
    knowledge_values = (
        build_chunk_knowledge()
    )
    meeting_knowledge = (
        build_meeting_knowledge()
    )

    chunker = FakeTranscriptChunker(
        chunks
    )
    chunk_service = (
        FakeChunkKnowledgeService(
            knowledge_values
        )
    )
    assembler = (
        FakeMeetingKnowledgeAssembler(
            meeting_knowledge
        )
    )
    consolidation_service = (
        FakeConsolidationService(
            consolidation_results
            if consolidation_results is not None
            else [
                build_report(),
            ]
        )
    )

    generator = MeetingReportGenerator(
        transcript_chunker=chunker,
        chunk_knowledge_service=(
            chunk_service
        ),
        meeting_knowledge_assembler=(
            assembler
        ),
        consolidation_service=(
            consolidation_service
        ),
    )

    return (
        generator,
        chunker,
        chunk_service,
        assembler,
        consolidation_service,
        meeting_knowledge,
    )


def test_generator_processes_every_chunk_once() -> None:
    (
        generator,
        chunker,
        chunk_service,
        assembler,
        consolidation_service,
        meeting_knowledge,
    ) = build_generator()

    transcript = build_transcript()

    result = generator.generate(
        transcript
    )

    assert isinstance(
        result,
        MeetingReport,
    )

    assert chunker.calls == 1
    assert (
        chunker.received_transcript
        is transcript
    )

    assert len(
        chunk_service.calls
    ) == 2

    assert [
        chunk.index
        for chunk in chunk_service.calls
    ] == [
        0,
        1,
    ]

    assert assembler.calls == 1
    assert (
        assembler.received_source_chunk_count
        == 2
    )

    assert [
        knowledge.chunk_index
        for knowledge in (
            assembler.received_chunks
        )
    ] == [
        0,
        1,
    ]

    assert consolidation_service.calls == 1
    assert (
        consolidation_service
        .received_knowledge[
            0
        ]
        is meeting_knowledge
    )


def test_generator_preserves_early_and_late_chunk_knowledge() -> None:
    (
        generator,
        _,
        _,
        assembler,
        _,
        _,
    ) = build_generator()

    generator.generate(
        build_transcript()
    )

    received = (
        assembler.received_chunks
    )

    assert (
        "estado inicial"
        in received[
            0
        ].key_points[
            0
        ]
    )

    assert (
        "continuará"
        in received[
            1
        ].conclusions[
            0
        ]
    )


def test_generator_rejects_non_transcript() -> None:
    generator = build_generator()[0]

    with pytest.raises(
        TypeError,
        match=(
            "transcript debe ser una instancia"
        ),
    ):
        generator.generate(
            object()
        )


def test_generator_rejects_when_chunker_returns_no_chunks() -> None:
    generator = MeetingReportGenerator(
        transcript_chunker=(
            FakeTranscriptChunker(
                []
            )
        ),
    )

    with pytest.raises(
        ValueError,
        match="no produjo chunks analizables",
    ):
        generator.generate(
            Transcript()
        )


def test_generator_propagates_chunk_extraction_error_without_retry() -> None:
    chunks = build_chunks()
    knowledge_values = (
        build_chunk_knowledge()
    )

    chunk_service = (
        FakeChunkKnowledgeService(
            results=knowledge_values,
            error_at_index=1,
            error=ValueError(
                "evidencia inválida del chunk"
            ),
        )
    )

    consolidation_service = (
        FakeConsolidationService(
            [
                build_report(),
            ]
        )
    )

    generator = MeetingReportGenerator(
        transcript_chunker=(
            FakeTranscriptChunker(
                chunks
            )
        ),
        chunk_knowledge_service=(
            chunk_service
        ),
        meeting_knowledge_assembler=(
            FakeMeetingKnowledgeAssembler(
                build_meeting_knowledge()
            )
        ),
        consolidation_service=(
            consolidation_service
        ),
    )

    with pytest.raises(
        ValueError,
        match="evidencia inválida del chunk",
    ):
        generator.generate(
            build_transcript()
        )

    assert len(
        chunk_service.calls
    ) == 2
    assert consolidation_service.calls == 0


def test_generator_rejects_empty_meeting_knowledge_before_consolidation() -> None:
    chunks = build_chunks()

    empty_values = {
        0: ChunkKnowledge(
            chunk_index=0,
            start=0.0,
            end=5.0,
        ),
        1: ChunkKnowledge(
            chunk_index=1,
            start=5.0,
            end=10.0,
        ),
    }

    empty_meeting_knowledge = (
        MeetingKnowledge(
            source_chunk_count=2,
            chunks=[
                empty_values[0],
                empty_values[1],
            ],
        )
    )

    consolidation_service = (
        FakeConsolidationService(
            [
                build_report(),
            ]
        )
    )

    generator = MeetingReportGenerator(
        transcript_chunker=(
            FakeTranscriptChunker(
                chunks
            )
        ),
        chunk_knowledge_service=(
            FakeChunkKnowledgeService(
                empty_values
            )
        ),
        meeting_knowledge_assembler=(
            FakeMeetingKnowledgeAssembler(
                empty_meeting_knowledge
            )
        ),
        consolidation_service=(
            consolidation_service
        ),
    )

    with pytest.raises(
        ValueError,
        match=(
            "no contiene conocimiento suficiente"
        ),
    ):
        generator.generate(
            build_transcript()
        )

    assert consolidation_service.calls == 0


def test_generator_propagates_global_infrastructure_error_without_retry() -> None:
    (
        generator,
        _,
        chunk_service,
        assembler,
        consolidation_service,
        _,
    ) = build_generator(
        consolidation_results=[
            RuntimeError(
                "ollama unavailable"
            ),
        ]
    )

    with pytest.raises(
        RuntimeError,
        match="ollama unavailable",
    ):
        generator.generate(
            build_transcript()
        )

    assert len(
        chunk_service.calls
    ) == 2
    assert assembler.calls == 1
    assert consolidation_service.calls == 1
