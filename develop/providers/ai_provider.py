"""
ai_provider.py

Contrato base para proveedores de IA.
"""

from abc import ABC, abstractmethod


class AIProvider(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str
    ) -> str:
        """
        Genera una respuesta a partir de un prompt.
        """
        pass