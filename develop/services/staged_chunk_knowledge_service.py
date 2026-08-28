"""
staged_chunk_knowledge_service.py

Genera ChunkKnowledge mediante el pipeline staged de
Meeting Assistant AI.

Etapas:

1. clasificación semántica plana;
2. enriquecimiento batch de acciones, solo cuando existen;
3. ensamblado determinista del dominio ChunkKnowledge.
"""

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
    ChunkClassificationParser,
)
from services.chunk_classification_prompt_formatter import (
    ChunkClassificationPromptFormatter,
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
    - una segunda vez únicamente cuando existen acciones.

    La evidencia completa nunca se solicita al proveedor.
    Se reconstruye posteriormente desde TranscriptChunk.
    """

    CLASSIFICATION_CONTRACT = (
        "chunk_classification_v1"
    )

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

        response = self.provider.generate(
            prompt.content,
            schema,
        )

        return self.classification_parser.parse(
            response=response,
            chunk=chunk,
        )

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