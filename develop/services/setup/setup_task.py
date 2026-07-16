"""
setup_task.py

Contrato base de las tareas del
MAI Setup & Recovery Engine.
"""

from abc import ABC, abstractmethod

from services.setup.task_result import TaskResult


class SetupTask(ABC):

    task_id: str = "undefined"
    name: str = "Tarea sin nombre"
    critical: bool = True

    @abstractmethod
    def should_run(self) -> bool:
        """
        Indica si la tarea necesita ejecutarse.
        """
        raise NotImplementedError

    @abstractmethod
    def run(self) -> TaskResult:
        """
        Ejecuta la instalación o reparación.

        No debe propagar excepciones.
        """
        raise NotImplementedError

    def verify(self) -> bool:
        """
        Verificación opcional después de ejecutar.

        Las tareas que necesiten comprobación adicional
        pueden sobrescribir este método.
        """
        return True