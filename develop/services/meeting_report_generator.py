"""
meeting_report_generator.py

Generador de MeetingReport a partir de un Transcript completo
mediante extracción por chunks y consolidación global.
"""

from models.artifacts.meeting_report import MeetingReport
from models.prompt import Prompt
from models.transcript import Transcript
from services.artifact_generator import ArtifactGenerator
from services.chunk_knowledge_service import ChunkKnowledgeService
from services.chunk_prompt_formatter import ChunkPromptFormatter
from services.meeting_knowledge_assembler import (
    MeetingKnowledgeAssembler,
)
from services.meeting_knowledge_prompt_formatter import (
    MeetingKnowledgePromptFormatter,
)
from services.meeting_report_consolidation_service import (
    MeetingReportConsolidationService,
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
        -> N x ChunkKnowledge
        -> MeetingKnowledge
        -> Prompt de consolidación
        -> MeetingReport

    La extracción de cada chunk ocurre exactamente una vez por
    ejecución. Si la consolidación final falla por contenido
    inválido, se permite un segundo intento correctivo utilizando
    el mismo MeetingKnowledge ya extraído.

    No realiza persistencia ni exportación.
    """

    MAX_CONSOLIDATION_ATTEMPTS = 2

    def __init__(
        self,
        transcript_chunker=None,
        chunk_prompt_formatter=None,
        chunk_knowledge_service=None,
        meeting_knowledge_assembler=None,
        consolidation_prompt_formatter=None,
        consolidation_service=None,
    ) -> None:
        self.transcript_chunker = (
            transcript_chunker
            if transcript_chunker is not None
            else TranscriptChunker()
        )

        self.chunk_prompt_formatter = (
            chunk_prompt_formatter
            if chunk_prompt_formatter is not None
            else ChunkPromptFormatter()
        )

        self.chunk_knowledge_service = (
            chunk_knowledge_service
            if chunk_knowledge_service is not None
            else ChunkKnowledgeService()
        )

        self.meeting_knowledge_assembler = (
            meeting_knowledge_assembler
            if meeting_knowledge_assembler is not None
            else MeetingKnowledgeAssembler()
        )

        self.consolidation_prompt_formatter = (
            consolidation_prompt_formatter
            if consolidation_prompt_formatter is not None
            else MeetingKnowledgePromptFormatter()
        )

        self.consolidation_service = (
            consolidation_service
            if consolidation_service is not None
            else MeetingReportConsolidationService()
        )

    def generate(
        self,
        transcript: Transcript,
    ) -> MeetingReport:
        """
        Genera un MeetingReport con cobertura de toda la reunión.

        Los errores de infraestructura del proveedor no se
        capturan aquí y continúan propagándose.

        Los ValueError producidos durante extracción por chunk
        también se propagan inmediatamente. Solo la consolidación
        final dispone de un segundo intento correctivo.
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
            chunk_prompt = (
                self.chunk_prompt_formatter.format(
                    chunk
                )
            )

            knowledge = (
                self.chunk_knowledge_service.generate(
                    prompt=chunk_prompt,
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

        base_prompt = (
            self.consolidation_prompt_formatter.format(
                meeting_knowledge
            )
        )

        current_prompt = base_prompt
        last_errors: list[str] = []

        for attempt in range(
            1,
            self.MAX_CONSOLIDATION_ATTEMPTS + 1,
        ):
            try:
                return self.consolidation_service.generate(
                    prompt=current_prompt,
                    meeting_knowledge=meeting_knowledge,
                )
            except ValueError as ex:
                last_errors = [
                    str(
                        ex
                    )
                ]

                if (
                    attempt
                    < self.MAX_CONSOLIDATION_ATTEMPTS
                ):
                    current_prompt = (
                        self._build_corrective_prompt(
                            base_prompt=base_prompt,
                            errors=last_errors,
                        )
                    )

        raise ValueError(
            "MeetingReport inválido después de la "
            "consolidación: "
            + "; ".join(
                last_errors
            )
        )

    @staticmethod
    def _build_corrective_prompt(
        base_prompt: Prompt,
        errors: list[str],
    ) -> Prompt:
        """
        Construye el segundo Prompt de consolidación.

        Conserva íntegramente MeetingKnowledge y el contrato
        original. Solo añade feedback específico de la generación
        final rechazada.
        """

        if not isinstance(
            base_prompt,
            Prompt,
        ):
            raise TypeError(
                "base_prompt debe ser una instancia de Prompt."
            )

        if not isinstance(
            errors,
            list,
        ):
            raise TypeError(
                "errors debe ser una lista."
            )

        error_text = "\n".join(
            f"- {error}"
            for error in errors
        )

        correction = f"""

INSTRUCCIONES CORRECTIVAS PARA LA CONSOLIDACIÓN

La generación global anterior fue rechazada por los siguientes
problemas:

{error_text}

Genera nuevamente TODO el MeetingReport desde cero utilizando
exclusivamente el MeetingKnowledge incluido en este Prompt.

Reglas obligatorias para este nuevo intento:

- No inventes hechos ausentes de MeetingKnowledge.
- No inventes ni modifiques evidencias.
- Para topics, decisions, action_items, risks y pending_items,
  utiliza únicamente referencias de evidencia ya presentes en la
  misma categoría semántica de MeetingKnowledge.
- Conserva exactamente speaker, start, end y excerpt de cada
  evidencia utilizada.
- No conviertas topics o posibilidades en decisiones, acciones,
  riesgos o pendientes.
- No inventes owner, due_date ni status de acciones.
- No devuelvas cadenas vacías en campos obligatorios.
- title debe ser descriptivo y representar la reunión completa.
- executive_summary debe representar conocimiento relevante del
  conjunto completo de chunks.
- key_points debe contener al menos un punto global relevante.
- Si una sección opcional no tiene información suficiente, utiliza
  una lista vacía.
- Respeta exactamente el JSON Schema solicitado.
- Devuelve únicamente el objeto JSON requerido.
"""

        return Prompt(
            content=(
                base_prompt.content
                + correction
            ),
            version=base_prompt.version,
        )
