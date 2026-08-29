import inspect

import pytest

from models.artifacts.meeting_report import MeetingReport
from models.chunk_knowledge import ChunkKnowledge
from models.meeting_knowledge import MeetingKnowledge
from models.transcript import Segment, Transcript
from models.transcript_chunk import TranscriptChunk
from services.artifact_generator import ArtifactGenerator
from services.meeting_report_generator import (
    MeetingReportGenerator,
)
from services.staged_chunk_knowledge_service import (
    StagedChunkKnowledgeService,
)
from services.staged_meeting_report_consolidation_service import (
    StagedMeetingReportConsolidationService,
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
    ) -> None:
        self.results = dict(
            results
        )
        self.calls = 0
        self.received_chunks = []

    def generate(
        self,
        chunk,
    ):
        self.calls += 1
        self.received_chunks.append(
            chunk
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
            end=10.0,
            speaker="LOCAL",
            text=(
                "Se revisó el estado general "
                "del proyecto."
            ),
        )
    )

    return transcript


def build_chunk() -> TranscriptChunk:
    return TranscriptChunk(
        index=0,
        segments=[
            Segment(
                start=0.0,
                end=10.0,
                speaker="LOCAL",
                text=(
                    "Se revisó el estado general "
                    "del proyecto."
                ),
            ),
        ],
    )


def build_chunk_knowledge() -> ChunkKnowledge:
    return ChunkKnowledge(
        chunk_index=0,
        start=0.0,
        end=10.0,
        key_points=[
            (
                "Se revisó el estado general "
                "del proyecto."
            ),
        ],
    )


def build_meeting_knowledge() -> MeetingKnowledge:
    return MeetingKnowledge(
        source_chunk_count=1,
        chunks=[
            build_chunk_knowledge(),
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
            "Estado general del proyecto"
        ),
        executive_summary=(
            "Se revisó el estado general del proyecto "
            "y se identificaron los elementos relevantes "
            "para continuar el seguimiento."
        ),
        key_points=[
            (
                "Se revisó el estado general "
                "del proyecto."
            ),
        ],
    )


def build_generator(
    consolidation_results=None,
):
    chunk = build_chunk()
    knowledge = build_chunk_knowledge()
    meeting_knowledge = (
        build_meeting_knowledge()
    )

    chunker = FakeTranscriptChunker(
        [
            chunk,
        ]
    )

    chunk_service = (
        FakeChunkKnowledgeService(
            {
                0: knowledge,
            }
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


def test_meeting_report_generator_implements_artifact_generator() -> None:
    generator = build_generator()[0]

    assert isinstance(
        generator,
        ArtifactGenerator,
    )


def test_generator_chunks_transcript_before_knowledge_extraction() -> None:
    (
        generator,
        chunker,
        chunk_service,
        _,
        _,
        _,
    ) = build_generator()

    transcript = build_transcript()

    generator.generate(
        transcript
    )

    assert chunker.calls == 1
    assert (
        chunker.received_transcript
        is transcript
    )

    assert chunk_service.calls == 1
    assert (
        chunk_service.received_chunks[
            0
        ].index
        == 0
    )


def test_generator_assembles_complete_meeting_knowledge() -> None:
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

    assert assembler.calls == 1
    assert (
        assembler.received_source_chunk_count
        == 1
    )
    assert len(
        assembler.received_chunks
    ) == 1
    assert (
        assembler.received_chunks[
            0
        ].chunk_index
        == 0
    )


def test_generator_passes_meeting_knowledge_directly_to_staged_consolidation() -> None:
    (
        generator,
        _,
        _,
        _,
        consolidation_service,
        meeting_knowledge,
    ) = build_generator()

    generator.generate(
        build_transcript()
    )

    assert consolidation_service.calls == 1
    assert (
        consolidation_service
        .received_knowledge[
            0
        ]
        is meeting_knowledge
    )


def test_generator_returns_consolidated_meeting_report() -> None:
    report = build_report()

    generator = build_generator(
        consolidation_results=[
            report,
        ]
    )[0]

    result = generator.generate(
        build_transcript()
    )

    assert result is report
    assert isinstance(
        result,
        MeetingReport,
    )


def test_generator_rejects_invalid_consolidated_report_after_retry() -> None:
    (
        generator,
        _,
        chunk_service,
        _,
        consolidation_service,
        _,
    ) = build_generator(
        consolidation_results=[
            ValueError(
                "narrativa global inválida"
            ),
            ValueError(
                "narrativa global inválida"
            ),
        ]
    )

    with pytest.raises(
        ValueError,
        match=(
            "MeetingReport inválido después "
            "de la consolidación staged"
        ),
    ):
        generator.generate(
            build_transcript()
        )

    assert chunk_service.calls == 1
    assert consolidation_service.calls == 2


def test_generator_rejects_invalid_transcript_before_dependencies() -> None:
    (
        generator,
        chunker,
        chunk_service,
        assembler,
        consolidation_service,
        _,
    ) = build_generator()

    with pytest.raises(
        TypeError,
        match=(
            "transcript debe ser una instancia"
        ),
    ):
        generator.generate(
            object()
        )

    assert chunker.calls == 0
    assert chunk_service.calls == 0
    assert assembler.calls == 0
    assert consolidation_service.calls == 0


def test_generator_uses_staged_contracts_by_default() -> None:
    generator = MeetingReportGenerator()

    assert isinstance(
        generator.chunk_knowledge_service,
        StagedChunkKnowledgeService,
    )

    assert (
        generator
        .chunk_knowledge_service
        .CLASSIFICATION_CONTRACT
        == "chunk_classification_v1"
    )

    assert (
        generator
        .chunk_knowledge_service
        .ACTION_METADATA_CONTRACT
        == "chunk_action_metadata_v1"
    )

    assert isinstance(
        generator.consolidation_service,
        StagedMeetingReportConsolidationService,
    )

    assert (
        generator
        .consolidation_service
        .SEMANTIC_CONSOLIDATION_CONTRACT
        == "meeting_semantic_consolidation_v1"
    )

    assert (
        generator
        .consolidation_service
        .NARRATIVE_CONTRACT
        == "meeting_report_narrative_v1"
    )

    assert (
        generator
        .consolidation_service
        .FINAL_PIPELINE_VERSION
        == "meeting_report_global_staged_v1"
    )


def test_generator_no_longer_exposes_legacy_consolidation_formatter() -> None:
    generator = MeetingReportGenerator()

    assert not hasattr(
        generator,
        "consolidation_prompt_formatter",
    )

    parameters = (
        inspect.signature(
            MeetingReportGenerator.__init__
        ).parameters
    )

    assert (
        "consolidation_prompt_formatter"
        not in parameters
    )


def test_generator_declares_meeting_report_return_contract() -> None:
    signature = inspect.signature(
        MeetingReportGenerator.generate
    )

    assert (
        signature.return_annotation
        is MeetingReport
    )
