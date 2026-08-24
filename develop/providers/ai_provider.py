"""
ai_provider.py

Contrato base para proveedores de IA.
"""

from abc import ABC, abstractmethod

from models.provider_health import ProviderHealth


class AIProvider(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str,
        output_schema: dict | None = None,
    ) -> str:
        """
        Genera una respuesta a partir de un prompt.

        Args:
            prompt:
                Contenido textual enviado al modelo.

            output_schema:
                JSON Schema opcional utilizado para
                restringir estructuralmente la respuesta.

                Si es None, el proveedor decide el mecanismo
                genérico más apropiado para solicitar JSON.
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