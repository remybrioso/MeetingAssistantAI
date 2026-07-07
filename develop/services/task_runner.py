"""
task_runner.py

Infraestructura para ejecutar tareas en segundo plano.
"""

import threading
import traceback


class TaskRunner:

    def run(self, target, *args, **kwargs):

        def wrapper():
            try:
                print("[TaskRunner] Tarea iniciada.")
                target(*args, **kwargs)
                print("[TaskRunner] Tarea finalizada correctamente.")
            except Exception:
                print("[TaskRunner] ERROR en tarea:")
                traceback.print_exc()

        thread = threading.Thread(
            target=wrapper,
            daemon=True
        )

        thread.start()

        return thread