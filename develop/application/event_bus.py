"""
event_bus.py

Bus de eventos de la aplicación.
Permite que los componentes se comuniquen sin depender unos de otros.
"""

from collections import defaultdict
from typing import Callable, Any


class EventBus:
    """Bus de eventos simple."""

    def __init__(self):
        self._listeners: dict[str, list[Callable[..., Any]]] = defaultdict(list)

    def subscribe(self, event_name: str, callback: Callable[..., Any]) -> None:
        """
        Suscribe una función a un evento.

        Parameters
        ----------
        event_name : str
            Nombre del evento.
        callback : Callable
            Función que será ejecutada cuando ocurra el evento.
        """
        self._listeners[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback: Callable[..., Any]) -> None:
        """
        Elimina una suscripción.
        """
        if callback in self._listeners[event_name]:
            self._listeners[event_name].remove(callback)

    def emit(self, event_name: str, *args, **kwargs) -> None:
        """
        Dispara un evento.
        """
        for callback in self._listeners[event_name]:
            callback(*args, **kwargs)

    def clear(self) -> None:
        """
        Elimina todos los eventos registrados.
        """
        self._listeners.clear()