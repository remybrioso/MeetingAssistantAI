"""
meeting_report_generator.py

Generador de MeetingReport a partir de un Transcript completo
mediante extracción staged por chunks y consolidación global staged.
"""

from models.artifacts.meeting_report import MeetingReport
from models.transcript import Transcript
from services.artifact_generator import ArtifactGenerator
from services.meeting_knowledge_assembler import (
    MeetingKnowledgeAssembler,
)
from services.staged_chunk_knowledge_service import (
    StagedChunkKnowledgeService,
)
from services.staged_meeting_report_consolidation_service import (
    StagedMeetingReportConsolidationService,
)
from services.transcript_chunker import TranscriptChunker


class MeetingReportGenerator(
    ArtifactGenerator
):
    """
    Orquesta la generación global de un MeetingReport.

    Flujo:

    Transcript
        -> TranscriptChunker
        -> N x StagedChunkKnowledgeService
        -> N x ChunkKnowledge
        -> MeetingKnowledge
        -> StagedMeetingReportConsolidationService
        -> MeetingReport

    La extracción staged de cada chunk ocurre exactamente una vez
    por ejecución.

    Si la consolidación global staged falla con ValueError, se
    permite un segundo intento completo de consolidación utilizando
    el mismo MeetingKnowledge ya extraído. La extracción por chunks
    nunca se repite durante ese retry.

    Los errores de infraestructura distintos de ValueError se
    propagan inmediatamente.

    No realiza persistencia ni exportación.
    """

    MAX_CONSOLIDATION_ATTEMPTS = 2

    def __init__(
        self,
        transcript_chunker=None,
        chunk_knowledge_service=None,
        meeting_knowledge_assembler=None,
        consolidation_service=None,
    ) -> None:
        self.transcript_chunker = (
            transcript_chunker
            if transcript_chunker is not None
            else TranscriptChunker()
        )

        self.chunk_knowledge_service = (
            chunk_knowledge_service
            if chunk_knowledge_service is not None
            else StagedChunkKnowledgeService()
        )

        self.meeting_knowledge_assembler = (
            meeting_knowledge_assembler
            if meeting_knowledge_assembler is not None
            else MeetingKnowledgeAssembler()
        )

        self.consolidation_service = (
            consolidation_service
            if consolidation_service is not None
            else StagedMeetingReportConsolidationService()
        )

    def generate(
        self,
        transcript: Transcript,
    ) -> MeetingReport:
        """
        Genera un MeetingReport con cobertura de toda la reunión.

        ValueError de la extracción staged por chunk se propaga
        inmediatamente.

        Solo ValueError de la consolidación global staged dispone
        de un segundo intento sobre el mismo MeetingKnowledge.
        """

        if not isinstance(
            transcript,
            Transcript,
        ):
            raise TypeError(
                "transcript debe ser una instancia de Transcript."
            )

        chunks = self.transcript_chunker.chunk(
            transcript
        )

        if not chunks:
            raise ValueError(
                "Transcript no produjo chunks analizables."
            )

        chunk_knowledge = []

        for chunk in chunks:
            knowledge = (
                self.chunk_knowledge_service.generate(
                    chunk=chunk,
                )
            )

            chunk_knowledge.append(
                knowledge
            )

        meeting_knowledge = (
            self.meeting_knowledge_assembler.assemble(
                chunks=chunk_knowledge,
                source_chunk_count=len(
                    chunks
                ),
            )
        )

        if not meeting_knowledge.has_content:
            raise ValueError(
                "MeetingKnowledge no contiene conocimiento "
                "suficiente para generar un MeetingReport."
            )

        last_error: ValueError | None = None

        for attempt in range(
            1,
            self.MAX_CONSOLIDATION_ATTEMPTS + 1,
        ):
            try:
                return (
                    self.consolidation_service.generate(
                        meeting_knowledge=(
                            meeting_knowledge
                        ),
                    )
                )
            except ValueError as ex:
                last_error = ex

                if (
                    attempt
                    >= self.MAX_CONSOLIDATION_ATTEMPTS
                ):
                    break

        if last_error is None:
            raise RuntimeError(
                "MeetingReportGenerator agotó la consolidación "
                "sin resultado ni error registrado."
            )

        raise ValueError(
            "MeetingReport inválido después de la "
            "consolidación staged: "
            f"{last_error}"
        ) from last_error
