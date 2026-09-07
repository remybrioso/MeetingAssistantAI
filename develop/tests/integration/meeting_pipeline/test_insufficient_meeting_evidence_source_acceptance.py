from pathlib import Path

import pytest

from exceptions.insufficient_meeting_evidence_error import (
    InsufficientMeetingEvidenceError,
)
from exceptions.insufficient_meeting_semantic_evidence_error import (
    InsufficientMeetingSemanticEvidenceError,
)
from models.recording_session import RecordingSession
from models.transcript import Segment, Transcript
from services.meeting_knowledge_assembler import (
    MeetingKnowledgeAssembler,
)
from services.meeting_pipeline_service import (
    MeetingPipelineService,
)
from services.meeting_report_generator import (
    MeetingReportGenerator,
)
from services.staged_chunk_knowledge_service import (
    StagedChunkKnowledgeService,
)
from services.transcript_analyzer import TranscriptAnalyzer
from services.transcript_chunker import TranscriptChunker
from services.transcript_storage_service import (
    TranscriptStorageService,
)
from services.transcript_validator import TranscriptValidator
from services.workspace_service import WorkspaceService


class EmptyKnowledgeProvider:

    model = "fake-structured-output"

    def __init__(
        self,
        response: str | None = None,
        responses: list[str] | None = None,
    ) -> None:
        self.calls = []
        if response is not None and responses is not None:
            raise ValueError(
                "Use response o responses, no ambos."
            )
        self.responses = list(
            responses
            if responses is not None
            else [
                response
                if response is not None
                else '{"items": [], "ignored_segment_ids": []}'
            ]
        )

    def generate(
        self,
        prompt,
        schema,
    ) -> str:
        self.calls.append(
            (
                prompt,
                schema,
            )
        )

        if not self.responses:
            raise AssertionError(
                "El proveedor recibió más llamadas que respuestas configuradas."
            )

        return self.responses.pop(0)


class CapturingMeetingKnowledgeAssembler(
    MeetingKnowledgeAssembler
):

    def __init__(self) -> None:
        self.result = None

    def assemble(
        self,
        chunks,
        source_chunk_count,
    ):
        self.result = super().assemble(
            chunks=chunks,
            source_chunk_count=source_chunk_count,
        )

        return self.result


class UnexpectedConsolidationService:

    def __init__(self) -> None:
        self.calls = 0

    def generate(
        self,
        meeting_knowledge,
    ):
        self.calls += 1
        raise AssertionError(
            "La consolidación global no debe ejecutarse."
        )


class CapturingDeliveryService:

    def __init__(self) -> None:
        self.calls = 0

    def deliver(
        self,
        report,
        workspace,
    ) -> None:
        self.calls += 1


def build_non_meeting_transcript() -> Transcript:
    return Transcript(
        segments=[
            Segment(
                start=0.0,
                end=18.0,
                speaker="NARRATOR",
                text=(
                    "El informe meteorológico describe nubes "
                    "dispersas durante la mañana, temperaturas "
                    "moderadas en la tarde y lluvias aisladas "
                    "durante la noche en varias provincias del "
                    "país, según los datos históricos publicados."
                ),
            )
        ]
    )


@pytest.mark.integration
def test_structurally_valid_non_meeting_stops_before_report_delivery(
    tmp_path: Path,
) -> None:
    transcript = build_non_meeting_transcript()
    analyzer = TranscriptAnalyzer()
    validator = TranscriptValidator()
    analysis = analyzer.analyze(
        transcript
    )
    valid, errors = validator.validate(
        analysis
    )

    assert valid is True
    assert errors == []
    assert analysis.total_words > 20
    assert analysis.total_characters > 80

    session = RecordingSession(
        base_output_dir=str(
            tmp_path
        ),
        session_prefix="meeting_cat_001_source",
    )
    workspace = WorkspaceService().create(
        session.session_dir
    )
    session.attach_workspace(
        workspace
    )

    storage = TranscriptStorageService()
    storage.save(
        transcript,
        workspace.transcript_json,
    )

    provider = EmptyKnowledgeProvider(
        responses=[
            '{"items": [], "ignored_segment_ids": [0]}',
            '{"items": [], "confirmed_ignored_segment_ids": [0]}',
        ]
    )
    knowledge_assembler = (
        CapturingMeetingKnowledgeAssembler()
    )
    consolidation_service = (
        UnexpectedConsolidationService()
    )
    delivery_service = CapturingDeliveryService()

    generator = MeetingReportGenerator(
        transcript_chunker=TranscriptChunker(),
        chunk_knowledge_service=(
            StagedChunkKnowledgeService(
                provider=provider
            )
        ),
        meeting_knowledge_assembler=(
            knowledge_assembler
        ),
        consolidation_service=(
            consolidation_service
        ),
    )

    pipeline = MeetingPipelineService(
        artifact_generator=generator,
        artifact_delivery_service=(
            delivery_service
        ),
        transcript_storage_service=storage,
        transcript_analyzer=analyzer,
        transcript_validator=validator,
    )

    with pytest.raises(
        InsufficientMeetingSemanticEvidenceError,
    ) as error:
        pipeline.process(
            session
        )

    assert len(provider.calls) == 2
    assert knowledge_assembler.result is not None
    assert (
        knowledge_assembler
        .result
        .source_chunk_count
        == 1
    )
    assert (
        knowledge_assembler
        .result
        .content_chunk_count
        == 0
    )
    assert (
        knowledge_assembler
        .result
        .has_content
        is False
    )

    assert error.value.source_chunk_count == 1
    assert error.value.content_chunk_count == 0
    assert consolidation_service.calls == 0
    assert delivery_service.calls == 0

    assert not workspace.meeting_report_json.exists()
    assert not workspace.action_items_json.exists()
    assert not workspace.decisions_json.exists()


@pytest.mark.integration
def test_malformed_chunk_model_output_remains_technical_failure(
    tmp_path: Path,
) -> None:
    transcript = build_non_meeting_transcript()
    session = RecordingSession(
        base_output_dir=str(
            tmp_path
        ),
        session_prefix="meeting_cat_001_malformed",
    )
    workspace = WorkspaceService().create(
        session.session_dir
    )
    session.attach_workspace(
        workspace
    )

    storage = TranscriptStorageService()
    storage.save(
        transcript,
        workspace.transcript_json,
    )

    provider = EmptyKnowledgeProvider(
        response="malformed model output"
    )
    consolidation_service = (
        UnexpectedConsolidationService()
    )
    delivery_service = CapturingDeliveryService()

    generator = MeetingReportGenerator(
        transcript_chunker=TranscriptChunker(),
        chunk_knowledge_service=(
            StagedChunkKnowledgeService(
                provider=provider
            )
        ),
        meeting_knowledge_assembler=(
            MeetingKnowledgeAssembler()
        ),
        consolidation_service=(
            consolidation_service
        ),
    )

    pipeline = MeetingPipelineService(
        artifact_generator=generator,
        artifact_delivery_service=(
            delivery_service
        ),
        transcript_storage_service=storage,
        transcript_analyzer=TranscriptAnalyzer(),
        transcript_validator=TranscriptValidator(),
    )

    with pytest.raises(
        ValueError,
        match=(
            "ChunkClassification no contiene un objeto JSON"
        ),
    ) as error:
        pipeline.process(
            session
        )

    assert not isinstance(
        error.value,
        InsufficientMeetingEvidenceError,
    )
    assert len(provider.calls) == 1
    assert consolidation_service.calls == 0
    assert delivery_service.calls == 0
