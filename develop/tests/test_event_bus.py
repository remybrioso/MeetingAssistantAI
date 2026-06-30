import sys
from pathlib import Path

# Agrega la raíz del proyecto al PYTHONPATH
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from application.event_bus import EventBus


def saludar(nombre):
    print(f"Hola {nombre}")


bus = EventBus()

bus.subscribe("inicio", saludar)

bus.emit("inicio", "Remy")