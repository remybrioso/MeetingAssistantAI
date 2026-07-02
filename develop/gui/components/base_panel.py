"""
base_panel.py

Clase base para todos los paneles de la interfaz.
"""

import customtkinter as ctk

from application.dependency_container import container


class BasePanel(ctk.CTkFrame):
    """
    Clase base para todos los paneles de la GUI.

    Proporciona acceso centralizado a los servicios comunes y
    utilidades para trabajar con eventos y actualizaciones seguras
    de la interfaz.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.bus = container.get("event_bus")
        self.state = container.get("app_state")
        self.config = container.get("configuration")
        self.logger = container.get("logger")

    def subscribe(self, event_name, callback):
        """
        Registra un callback en el EventBus.
        """
        self.bus.subscribe(event_name, callback)

    def publish(self, event_name, *args):
        """
        Publica un evento en el EventBus.
        """
        self.bus.emit(event_name, *args)

    def run_on_ui(self, callback):
        """
        Ejecuta un callback de forma segura
        sobre el hilo principal de la interfaz.
        """
        self.after(0, callback)