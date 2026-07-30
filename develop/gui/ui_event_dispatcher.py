"""
ui_event_dispatcher.py

Adapta eventos del EventBus para que los callbacks de la GUI
se ejecuten exclusivamente en el hilo principal de Tkinter.
"""

from __future__ import annotations

from queue import Empty, Queue
from typing import Any, Callable

from application.event_bus import EventBus


class UIEventDispatcher:
    """
    Puente seguro entre EventBus y la interfaz gráfica.

    Los eventos pueden emitirse desde cualquier hilo. Sus callbacks
    se colocan en una cola y son ejecutados posteriormente por el
    hilo principal de Tkinter.
    """

    def __init__(
        self,
        widget,
        event_bus: EventBus,
        poll_interval_ms: int = 25,
    ) -> None:
        self._widget = widget
        self._event_bus = event_bus
        self._poll_interval_ms = poll_interval_ms

        self._queue: Queue[
            tuple[
                Callable[..., Any],
                tuple[Any, ...],
                dict[str, Any],
            ]
        ] = Queue()

        self._subscriptions: list[
            tuple[str, Callable[..., Any]]
        ] = []

        self._running = False
        self._after_id: str | None = None

    def start(self) -> None:
        """
        Inicia el procesamiento periódico de callbacks.

        Debe invocarse desde el hilo principal de Tkinter.
        """
        if self._running:
            return

        self._running = True
        self._schedule_poll()

    def subscribe(
        self,
        event_name: str,
        callback: Callable[..., Any],
    ) -> None:
        """
        Suscribe un callback gráfico a un evento.

        El wrapper registrado en EventBus no modifica la GUI:
        solamente coloca el trabajo en una Queue segura.
        """

        def enqueue_callback(
            *args: Any,
            **kwargs: Any,
        ) -> None:
            self._queue.put(
                (
                    callback,
                    args,
                    kwargs,
                )
            )

        self._event_bus.subscribe(
            event_name,
            enqueue_callback,
        )

        self._subscriptions.append(
            (
                event_name,
                enqueue_callback,
            )
        )

    def stop(self) -> None:
        """
        Detiene el dispatcher y elimina sus suscripciones.
        """
        if not self._running and not self._subscriptions:
            return

        self._running = False

        if self._after_id is not None:
            try:
                self._widget.after_cancel(
                    self._after_id
                )
            except Exception:
                pass

            self._after_id = None

        for event_name, callback in self._subscriptions:
            self._event_bus.unsubscribe(
                event_name,
                callback,
            )

        self._subscriptions.clear()

    def _schedule_poll(self) -> None:
        if not self._running:
            return

        self._after_id = self._widget.after(
            self._poll_interval_ms,
            self._process_queue,
        )

    def _process_queue(self) -> None:
        self._after_id = None

        try:
            while True:
                callback, args, kwargs = (
                    self._queue.get_nowait()
                )

                try:
                    callback(
                        *args,
                        **kwargs,
                    )
                except Exception as error:
                    self._report_callback_error(
                        error
                    )

        except Empty:
            pass

        finally:
            self._schedule_poll()

    def _report_callback_error(
        self,
        error: Exception,
    ) -> None:
        """
        Envía los errores al mecanismo estándar de Tkinter.
        """
        reporter = getattr(
            self._widget,
            "report_callback_exception",
            None,
        )

        if callable(reporter):
            reporter(
                type(error),
                error,
                error.__traceback__,
            )
        else:
            raise error