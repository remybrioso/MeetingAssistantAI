"""
capability.py

Contrato base para las capacidades funcionales de MAI.
"""

from abc import ABC, abstractmethod

from services.setup.capabilities.capability_result import (
    CapabilityResult,
)


class Capability(ABC):

    capability_id: str = "undefined"
    name: str = "Capacidad sin nombre"
    description: str = ""

    @abstractmethod
    def get_tasks(self) -> list:
        """
        Devuelve las tareas técnicas necesarias
        para preparar o verificar la capacidad.
        """
        raise NotImplementedError

    @abstractmethod
    def evaluate(
        self,
        task_results
    ) -> CapabilityResult:
        """
        Convierte los resultados técnicos en un
        estado funcional comprensible.
        """
        raise NotImplementedError
