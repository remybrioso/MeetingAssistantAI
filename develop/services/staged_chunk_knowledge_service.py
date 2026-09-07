"""
staged_chunk_knowledge_service.py

Genera ChunkKnowledge mediante el pipeline staged de
Meeting Assistant AI.

Etapas:

1. clasificación semántica plana;
2. enriquecimiento batch de acciones, solo cuando existen;
3. ensamblado determinista del dominio ChunkKnowledge.
"""

from copy import deepcopy

from models.chunk_action_metadata import (
    ChunkActionMetadata,
)
from models.chunk_classification import (
    ChunkClassification,
    ChunkKnowledgeKind,
)
from models.chunk_knowledge import ChunkKnowledge
from models.prompt import Prompt
from models.transcript_chunk import TranscriptChunk
from providers.ollama_provider import OllamaProvider
from services.chunk_action_metadata_parser import (
    ChunkActionMetadataParser,
)
from services.chunk_action_metadata_prompt_formatter import (
    ChunkActionMetadataPromptFormatter,
)
from services.chunk_classification_parser import (
    ChunkClassificationCoverageError,
    ChunkClassificationParseResult,
    ChunkClassificationParser,
)
from services.chunk_classification_prompt_formatter import (
    ChunkClassificationPromptFormatter,
)
from services.chunk_classification_repair_prompt_formatter import (
    ChunkClassificationRepairPromptFormatter,
)
from services.chunk_ignored_segment_audit_parser import (
    ChunkIgnoredSegmentAuditParser,
)
from services.chunk_ignored_segment_audit_prompt_formatter import (
    ChunkIgnoredSegmentAuditPromptFormatter,
)
from services.chunk_knowledge_assembler import (
    ChunkKnowledgeAssembler,
)
from services.json_schema_loader import (
    JsonSchemaLoader,
)


class StagedChunkKnowledgeService:
    """
    Orquesta la extracción staged de conocimiento para un chunk.

    El proveedor de IA se utiliza:

    - una vez para clasificación;
    - una vez adicional solo si la clasificación incumple cobertura;
    - una vez para metadatos cuando existen acciones válidas.

    La evidencia completa nunca se solicita al proveedor.
    Se reconstruye posteriormente desde TranscriptChunk.
    """

    CLASSIFICATION_CONTRACT = (
        "chunk_classification_v2"
    )

    CLASSIFICATION_REPAIR_CONTRACT = "chunk_classification_repair_v1"

    IGNORED_SEGMENT_AUDIT_CONTRACT = "chunk_ignored_segment_audit_v1"

    ACTION_METADATA_CONTRACT = (
        "chunk_action_metadata_v1"
    )

    def __init__(
        self,
        provider=None,
        classification_prompt_formatter=None,
        classification_parser=None,
        action_metadata_prompt_formatter=None,
        action_metadata_parser=None,
        knowledge_assembler=None,
        schema_loader=None,
        classification_repair_prompt_formatter=None,
        ignored_segment_audit_prompt_formatter=None,
        ignored_segment_audit_parser=None,
    ) -> None:
        self.provider = (
            provider
            if provider is not None
            else OllamaProvider()
        )

        self.classification_prompt_formatter = (
            classification_prompt_formatter
            if classification_prompt_formatter is not None
            else ChunkClassificationPromptFormatter()
        )

        self.classification_parser = (
            classification_parser
            if classification_parser is not None
            else ChunkClassificationParser()
        )

        self.classification_repair_prompt_formatter = (
            classification_repair_prompt_formatter
            if classification_repair_prompt_formatter is not None
            else ChunkClassificationRepairPromptFormatter()
        )

        self.ignored_segment_audit_prompt_formatter = (
            ignored_segment_audit_prompt_formatter
            if ignored_segment_audit_prompt_formatter is not None
            else ChunkIgnoredSegmentAuditPromptFormatter()
        )

        self.ignored_segment_audit_parser = (
            ignored_segment_audit_parser
            if ignored_segment_audit_parser is not None
            else ChunkIgnoredSegmentAuditParser()
        )

        self.action_metadata_prompt_formatter = (
            action_metadata_prompt_formatter
            if action_metadata_prompt_formatter is not None
            else ChunkActionMetadataPromptFormatter()
        )

        self.action_metadata_parser = (
            action_metadata_parser
            if action_metadata_parser is not None
            else ChunkActionMetadataParser()
        )

        self.knowledge_assembler = (
            knowledge_assembler
            if knowledge_assembler is not None
            else ChunkKnowledgeAssembler()
        )

        self.schema_loader = (
            schema_loader
            if schema_loader is not None
            else JsonSchemaLoader()
        )

    def generate(
        self,
        chunk: TranscriptChunk,
    ) -> ChunkKnowledge:
        """
        Genera ChunkKnowledge para un único TranscriptChunk.
        """

        if not isinstance(
            chunk,
            TranscriptChunk,
        ):
            raise TypeError(
                "chunk debe ser una instancia "
                "de TranscriptChunk."
            )

        classification = (
            self._generate_classification(
                chunk
            )
        )

        action_metadata = (
            self._generate_action_metadata(
                chunk=chunk,
                classification=classification,
            )
        )

        return self.knowledge_assembler.assemble(
            chunk=chunk,
            classification=classification,
            action_metadata=action_metadata,
        )

    def _generate_classification(
        self,
        chunk: TranscriptChunk,
    ) -> ChunkClassification:
        prompt = (
            self.classification_prompt_formatter.format(
                chunk
            )
        )

        self._require_prompt_contract(
            prompt=prompt,
            expected_contract=(
                self.CLASSIFICATION_CONTRACT
            ),
            stage_name="clasificación",
        )

        schema = self.schema_loader.load(
            prompt.version
        )
        schema = self._specialize_classification_schema(
            schema, chunk
        )

        response = self.provider.generate(
            prompt.content,
            schema,
        )

        try:
            parsed = self._parse_classification(
                response=response,
                chunk=chunk,
            )
        except ChunkClassificationCoverageError as error:
            repair_prompt = self.classification_repair_prompt_formatter.format(
                chunk=chunk,
                invalid_response=response,
                coverage_error=str(error),
            )
            self._require_prompt_contract(
                prompt=repair_prompt,
                expected_contract=self.CLASSIFICATION_REPAIR_CONTRACT,
                stage_name="reparación de cobertura",
            )
            repaired_response = self.provider.generate(
                repair_prompt.content,
                schema,
            )
            parsed = self._parse_classification(
                response=repaired_response,
                chunk=chunk,
            )

        return self._audit_ignored_segments(
            chunk=chunk,
            parsed=parsed,
        )

    def _parse_classification(
        self,
        response: str,
        chunk: TranscriptChunk,
    ) -> ChunkClassificationParseResult:
        parse_with_metadata = getattr(
            self.classification_parser,
            "parse_with_metadata",
            None,
        )
        if callable(parse_with_metadata):
            return parse_with_metadata(
                response=response,
                chunk=chunk,
            )

        return ChunkClassificationParseResult(
            classification=self.classification_parser.parse(
                response=response,
                chunk=chunk,
            ),
            ignored_segment_ids=(),
        )

    def _audit_ignored_segments(
        self,
        chunk: TranscriptChunk,
        parsed: ChunkClassificationParseResult,
    ) -> ChunkClassification:
        candidate_ids = parsed.ignored_segment_ids
        if not candidate_ids:
            return parsed.classification

        prompt = self.ignored_segment_audit_prompt_formatter.format(
            chunk=chunk,
            candidate_ignored_segment_ids=candidate_ids,
        )
        self._require_prompt_contract(
            prompt=prompt,
            expected_contract=self.IGNORED_SEGMENT_AUDIT_CONTRACT,
            stage_name="auditoría semántica de segmentos ignorados",
        )
        schema = self.schema_loader.load(prompt.version)
        schema = self._specialize_ignored_segment_audit_schema(
            schema,
            candidate_ids,
        )
        response = self.provider.generate(prompt.content, schema)
        audit = self.ignored_segment_audit_parser.parse(
            response=response,
            chunk=chunk,
            candidate_ids=candidate_ids,
        )

        return ChunkClassification(
            chunk_index=parsed.classification.chunk_index,
            start=parsed.classification.start,
            end=parsed.classification.end,
            items=[
                *parsed.classification.items,
                *audit.recovered_items,
            ],
        )

    @staticmethod
    def _specialize_classification_schema(
        schema: dict,
        chunk: TranscriptChunk,
    ) -> dict:
        """Restringe los IDs locales sin modificar el contrato base."""
        specialized_schema = deepcopy(schema)
        valid_segment_ids = list(range(len(chunk.segments)))
        properties = specialized_schema["properties"]
        item_properties = properties["items"]["items"]["properties"]
        item_properties["segment_ids"]["items"]["enum"] = valid_segment_ids
        properties["ignored_segment_ids"]["items"]["enum"] = (
            valid_segment_ids.copy()
        )
        return specialized_schema

    @staticmethod
    def _specialize_ignored_segment_audit_schema(
        schema: dict,
        candidate_ids,
    ) -> dict:
        specialized_schema = deepcopy(schema)
        valid_ids = list(candidate_ids)
        item_properties = (
            specialized_schema["properties"]["items"]["items"]["properties"]
        )
        item_properties["segment_ids"]["items"]["enum"] = valid_ids.copy()
        specialized_schema["properties"]["confirmed_ignored_segment_ids"][
            "items"
        ]["enum"] = valid_ids.copy()
        return specialized_schema

    def _generate_action_metadata(
        self,
        chunk: TranscriptChunk,
        classification: ChunkClassification,
    ) -> ChunkActionMetadata:
        actions = classification.items_of_kind(
            ChunkKnowledgeKind.ACTION
        )

        if not actions:
            return ChunkActionMetadata(
                chunk_index=chunk.index,
                entries=[],
            )

        prompt = (
            self.action_metadata_prompt_formatter.format(
                classification=classification,
                chunk=chunk,
            )
        )

        self._require_prompt_contract(
            prompt=prompt,
            expected_contract=(
                self.ACTION_METADATA_CONTRACT
            ),
            stage_name=(
                "metadatos de acciones"
            ),
        )

        schema = self.schema_loader.load(
            prompt.version
        )

        response = self.provider.generate(
            prompt.content,
            schema,
        )

        return self.action_metadata_parser.parse(
            response=response,
            classification=classification,
            chunk=chunk,
        )

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
                f"El formatter de {stage_name} "
                "debe devolver una instancia de Prompt."
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
