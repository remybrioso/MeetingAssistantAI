"""
artifact_generator.py

Contrato base para generadores de artefactos de MAI.
"""

from abc import ABC, abstractmethod

from models.transcript import Transcript


class ArtifactGenerator(ABC):
    """
    Contrato común para cualquier componente capaz de
    transformar un Transcript en un artefacto de dominio.

    El contrato no conoce proveedores de IA, prompts,
    parsers, almacenamiento ni formatos de exportación.
    """

    @abstractmethod
    def generate(
        self,
        transcript: Transcript,
    ):
        """
        Genera un artefacto de dominio a partir de un
        Transcript.
        """

        raise NotImplementedError