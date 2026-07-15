"""
health_check.py

Contrato base para todas las comprobaciones de salud.
"""

from abc import ABC, abstractmethod

from services.health.health_result import HealthResult


class HealthCheck(ABC):

    @abstractmethod
    def run(self) -> HealthResult:
        """
        Ejecuta una comprobación y devuelve su resultado.

        Un HealthCheck no debe propagar excepciones.
        """
        raise NotImplementedError
