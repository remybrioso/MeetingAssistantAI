"""
=========================================
Sistema de Logs
=========================================
"""

import logging
from pathlib import Path

from config import LOG_FOLDER 

LOG_FILE = Path(LOG_FOLDER) / "meeting_assistant.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger("MeetingAssistant")