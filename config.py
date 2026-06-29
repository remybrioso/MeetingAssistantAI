"""
=====================================================
Meeting Assistant AI
Archivo de configuración general
=====================================================
"""

from pathlib import Path

# --------------------------------------------------
# Información de la aplicación
# --------------------------------------------------

APP_NAME = "Meeting Assistant AI"
APP_VERSION = "0.1.0 Alpha"

# --------------------------------------------------
# Directorios
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

LOG_FOLDER = BASE_DIR / "logs"
OUTPUT_FOLDER = BASE_DIR / "output"
TEMP_FOLDER = BASE_DIR / "temp"

# Crear carpetas automáticamente
LOG_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)
TEMP_FOLDER.mkdir(exist_ok=True)

# --------------------------------------------------
# Ventana principal
# --------------------------------------------------

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 650

# --------------------------------------------------
# Tema
# --------------------------------------------------

APPEARANCE_MODE = "dark"
COLOR_THEME = "blue"

# --------------------------------------------------
# Whisper
# --------------------------------------------------

WHISPER_MODEL = "small"

# --------------------------------------------------
# IA Local
# --------------------------------------------------

OLLAMA_MODEL = "qwen2.5:3b"

# --------------------------------------------------
# Idioma
# --------------------------------------------------

LANGUAGE = "es"