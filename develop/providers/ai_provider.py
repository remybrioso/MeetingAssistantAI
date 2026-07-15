"""
ai_provider.py

Contrato base para proveedores de IA.
"""

from abc import ABC, abstractmethod

from models.provider_health import ProviderHealth


class AIProvider(ABC):

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Genera una respuesta a partir de un prompt.
        """
        raise NotImplementedError

    @abstractmethod
    def health(self) -> ProviderHealth:
        """
        Comprueba la disponibilidad del proveedor
        y del modelo configurado.

        No debe propagar excepciones.
        """
        raise NotImplementedError