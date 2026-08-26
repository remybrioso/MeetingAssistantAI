"""
chunk_knowledge_service.py

Genera ChunkKnowledge mediante un proveedor de IA con
salida estructurada.
"""

from models.chunk_knowledge import ChunkKnowledge
from models.prompt import Prompt
from models.transcript_chunk import TranscriptChunk
from providers.ollama_provider import OllamaProvider
from services.chunk_knowledge_parser import (
    ChunkKnowledgeParser,
)
from services.json_schema_loader import (
    JsonSchemaLoader,
)


class ChunkKnowledgeService:
    """
    Genera conocimiento estructurado para un único chunk.

    No divide transcripts, no consolida chunks y no genera
    el MeetingReport final.
    """

    CONTRACT = "chunk_knowledge_v1"

    def __init__(
        self,
        provider=None,
        parser=None,
        schema_loader=None,
    ) -> None:
        self.provider = (
            provider
            if provider is not None
            else OllamaProvider()
        )
        self.parser = (
            parser
            if parser is not None
            else ChunkKnowledgeParser()
        )
        self.schema_loader = (
            schema_loader
            if schema_loader is not None
            else JsonSchemaLoader()
        )

    def generate(
        self,
        prompt: Prompt,
        chunk: TranscriptChunk,
    ) -> ChunkKnowledge:
        if not isinstance(prompt, Prompt):
            raise TypeError(
                "prompt debe ser una instancia de Prompt."
            )

        if not isinstance(chunk, TranscriptChunk):
            raise TypeError(
                "chunk debe ser una instancia "
                "de TranscriptChunk."
            )

        if prompt.version != self.CONTRACT:
            raise ValueError(
                "ChunkKnowledgeService requiere el contrato "
                f"{self.CONTRACT}. "
                f"Recibido: {prompt.version}."
            )

        schema = self.schema_loader.load(
            prompt.version
        )

        response = self.provider.generate(
            prompt.content,
            schema,
        )

        return self.parser.parse(
            response=response,
            chunk=chunk,
        )
