"""
loopback_engine.py

Motor encargado de capturar el audio del sistema
(WASAPI Loopback).

Versión inicial.

Todavía no realiza captura.
"""


class LoopbackEngine:

    def __init__(self):

        self._recording = False

    @property
    def is_recording(self):

        return self._recording

    def start(self):

        """
        Inicia la captura del audio del sistema.

        Implementación pendiente.
        """

        self._recording = True

    def stop(self):

        """
        Detiene la captura.

        Implementación pendiente.
        """

        self._recording = False