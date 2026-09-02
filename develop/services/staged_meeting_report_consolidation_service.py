"""
staged_meeting_report_consolidation_service.py

Orquesta la consolidación global staged de Meeting Assistant AI.

Etapas:

G1. consolidación semántica global mediante referencias;
G1C. reconciliación determinista de cobertura fuente;
G2. narrativa global grounded mediante item_ids;
G3. ensamblado determinista de MeetingReport;
G4. validación final de grounding y calidad.

El proveedor de IA se utiliza exactamente dos veces.
"""

from models.artifacts.meeting_report import (
    MeetingReport,
)
from models.meeting_knowledge import (
    MeetingKnowledge,
)
from models.prompt import Prompt
from providers.ollama_provider import (
    OllamaProvider,
)
from services.json_schema_loader import (
    JsonSchemaLoader,
)
from services.logger_service import LoggerService
from services.meeting_report_narrative_parser import (
    MeetingReportNarrativeParser,
)
from services.meeting_report_narrative_prompt_formatter import (
    MeetingReportNarrativePromptFormatter,
)
from services.meeting_report_staged_assembler import (
    MeetingReportStagedAssembler,
)
from services.meeting_semantic_coverage_service import (
    MeetingSemanticCoverageService,
)
from services.meeting_semantic_consolidation_parser import (
    CrossItemSourceReferenceReuseError,
    MeetingSemanticConsolidationParser,
)
from services.meeting_semantic_consolidation_prompt_formatter import (
    MeetingSemanticConsolidationPromptFormatter,
)
from services.validators.meeting_report_grounding_validator import (
    MeetingReportGroundingValidator,
)
from services.validators.meeting_report_validator import (
    MeetingReportValidator,
)


class StagedMeetingReportConsolidationService:
    """
    Consolida MeetingKnowledge mediante dos contratos globales
    pequeños y reconstrucción determinista del dominio final.

    El LLM nunca devuelve evidencia completa ni metadata final de
    acciones.
    """

    SEMANTIC_CONSOLIDATION_CONTRACT = (
        "meeting_semantic_consolidation_v1"
    )

    NARRATIVE_CONTRACT = (
        "meeting_report_narrative_v1"
    )

    FINAL_PIPELINE_VERSION = (
        "meeting_report_global_staged_v1"
    )

    PROVIDER_NAME = "ollama"

    def __init__(
        self,
        provider=None,
        semantic_prompt_formatter=None,
        semantic_parser=None,
        semantic_coverage_service=None,
        narrative_prompt_formatter=None,
        narrative_parser=None,
        report_assembler=None,
        schema_loader=None,
        grounding_validator=None,
        report_validator=None,
        logger=None,
    ) -> None:
        self.provider = (
            provider
            if provider is not None
            else OllamaProvider()
        )

        self.semantic_prompt_formatter = (
            semantic_prompt_formatter
            if semantic_prompt_formatter is not None
            else MeetingSemanticConsolidationPromptFormatter()
        )

        self.semantic_parser = (
            semantic_parser
            if semantic_parser is not None
            else MeetingSemanticConsolidationParser()
        )

        self.semantic_coverage_service = (
            semantic_coverage_service
            if semantic_coverage_service is not None
            else MeetingSemanticCoverageService()
        )

        self.narrative_prompt_formatter = (
            narrative_prompt_formatter
            if narrative_prompt_formatter is not None
            else MeetingReportNarrativePromptFormatter()
        )

        self.narrative_parser = (
            narrative_parser
            if narrative_parser is not None
            else MeetingReportNarrativeParser()
        )

        self.report_assembler = (
            report_assembler
            if report_assembler is not None
            else MeetingReportStagedAssembler()
        )

        self.schema_loader = (
            schema_loader
            if schema_loader is not None
            else JsonSchemaLoader()
        )

        self.grounding_validator = (
            grounding_validator
            if grounding_validator is not None
            else MeetingReportGroundingValidator()
        )

        self.report_validator = (
            report_validator
            if report_validator is not None
            else MeetingReportValidator()
        )

        self.logger = (
            logger
            if logger is not None
            else LoggerService()
        )

    def generate(
        self,
        meeting_knowledge: MeetingKnowledge,
    ) -> MeetingReport:
        """
        Ejecuta G1 + G2 + ensamblado + validaciones finales.
        """

        if not isinstance(
            meeting_knowledge,
            MeetingKnowledge,
        ):
            raise TypeError(
                "meeting_knowledge debe ser una instancia "
                "de MeetingKnowledge."
            )

        if not meeting_knowledge.has_content:
            raise ValueError(
                "meeting_knowledge no contiene conocimiento "
                "suficiente para consolidar."
            )

        semantic_consolidation = (
            self._generate_semantic_consolidation(
                meeting_knowledge
            )
        )

        narrative = (
            self._generate_narrative(
                semantic_consolidation
            )
        )

        report = self.report_assembler.assemble(
            meeting_knowledge=meeting_knowledge,
            semantic_consolidation=(
                semantic_consolidation
            ),
            narrative=narrative,
            provider=self.PROVIDER_NAME,
            model=self._provider_model(),
            prompt_version=(
                self.FINAL_PIPELINE_VERSION
            ),
        )

        self._validate_report(
            report=report,
            meeting_knowledge=meeting_knowledge,
        )

        return report

    def _generate_semantic_consolidation(
        self,
        meeting_knowledge: MeetingKnowledge,
    ):
        prompt = (
            self.semantic_prompt_formatter.format(
                meeting_knowledge
            )
        )

        self._require_prompt_contract(
            prompt=prompt,
            expected_contract=(
                self.SEMANTIC_CONSOLIDATION_CONTRACT
            ),
            stage_name=(
                "consolidación semántica global"
            ),
        )

        schema = self.schema_loader.load(
            prompt.version
        )

        response = self.provider.generate(
            prompt.content,
            schema,
        )

        try:
            parsed_consolidation = self.semantic_parser.parse(
                response=response,
                meeting_knowledge=(
                    meeting_knowledge
                ),
            )
        except CrossItemSourceReferenceReuseError as ex:
            self.logger.warning(
                "La consolidación semántica G1 fue descartada; "
                "razón: referencias fuente reutilizadas entre "
                "items consolidados; referencias reutilizadas: "
                + ", ".join(
                    str(key)
                    for key in ex.reused_source_keys
                )
                + "; estrategia: consolidación de identidad "
                "determinista."
            )

            return (
                self.semantic_coverage_service
                .build_identity_consolidation(
                    meeting_knowledge
                )
            )

        return self.semantic_coverage_service.reconcile(
            semantic_consolidation=(
                parsed_consolidation
            ),
            meeting_knowledge=meeting_knowledge,
        )

    def _generate_narrative(
        self,
        semantic_consolidation,
    ):
        prompt = (
            self.narrative_prompt_formatter.format(
                semantic_consolidation
            )
        )

        self._require_prompt_contract(
            prompt=prompt,
            expected_contract=(
                self.NARRATIVE_CONTRACT
            ),
            stage_name=(
                "narrativa global"
            ),
        )

        schema = self.schema_loader.load(
            prompt.version
        )

        response = self.provider.generate(
            prompt.content,
            schema,
        )

        return self.narrative_parser.parse(
            response=response,
            semantic_consolidation=(
                semantic_consolidation
            ),
        )

    def _validate_report(
        self,
        report: MeetingReport,
        meeting_knowledge: MeetingKnowledge,
    ) -> None:
        grounded, grounding_errors = (
            self.grounding_validator.validate(
                report=report,
                meeting_knowledge=(
                    meeting_knowledge
                ),
            )
        )

        if not grounded:
            raise ValueError(
                "El MeetingReport staged no conserva "
                "grounding válido. Detalle: "
                + "; ".join(
                    grounding_errors
                )
            )

        valid, validation_errors = (
            self.report_validator.validate(
                report
            )
        )

        if not valid:
            raise ValueError(
                "El MeetingReport staged consolidado "
                "es inválido. Detalle: "
                + "; ".join(
                    validation_errors
                )
            )

    def _provider_model(self) -> str:
        model = getattr(
            self.provider,
            "model",
            None,
        )

        if not isinstance(
            model,
            str,
        ):
            raise TypeError(
                "provider.model debe ser una cadena."
            )

        normalized = model.strip()

        if not normalized:
            raise ValueError(
                "provider.model no puede estar vacío."
            )

        return normalized

    @staticmethod
    def _require_prompt_contract(
        prompt: Prompt,
        expected_contract: str,
        stage_name: str,
    ) -> None:
        if not isinstance(
            prompt,
            Prompt,
        ):
            raise TypeError(
                f"El formatter de {stage_name} debe "
                "devolver una instancia de Prompt."
            )

        if (
            prompt.version
            != expected_contract
        ):
            raise ValueError(
                f"El stage de {stage_name} requiere "
                f"el contrato {expected_contract}. "
                f"Recibido: {prompt.version}."
            )
