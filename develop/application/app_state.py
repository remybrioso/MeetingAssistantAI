"""
app_state.py

Estado global de la aplicación.
Contiene toda la información compartida entre módulos.
"""

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class AppState:
    """
    Estado central del sistema.
    """

    # Estado de la reunión
    meeting_active: bool = False

    # Estado del audio
    audio_status: str = "idle"  # idle | recording | paused

    # Estado de la IA
    ai_status: str = "idle"  # idle | processing | ready

    # Transcripción
    transcription: str = ""

    # Archivo actual
    current_file: str | None = None
    
        # Estado del asistente de configuración
    setup_wizard_status: str = "pending"
    # pending | running | ready | attention | blocked | failed

    setup_wizard_completed: bool = False

    # Indica si el usuario puede acceder a la aplicación.
    application_ready: bool = False

    # Observadores (UI o servicios)
    _listeners: list[Callable[[str, Any], None]] = field(default_factory=list, repr=False)

    def set(self, key: str, value: Any) -> None:
        """
        Actualiza el estado y notifica cambios.
        """
        setattr(self, key, value)
        self._notify(key, value)

    def get(self, key: str) -> Any:
        """
        Obtiene un valor del estado.
        """
        return getattr(self, key)

    def subscribe(self, callback: Callable[[str, Any], None]) -> None:
        """
        Registra un observador.
        """
        self._listeners.append(callback)

    def _notify(self, key: str, value: Any) -> None:
        """
        Notifica cambios a los observadores.
        """
        for listener in self._listeners:
            listener(key, value)