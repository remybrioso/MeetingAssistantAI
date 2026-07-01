"""
recording_state.py

Estados posibles de una grabación.
"""

from enum import Enum


class RecordingState(Enum):

    IDLE = "idle"

    STARTING = "starting"

    RECORDING = "recording"

    PAUSED = "paused"

    STOPPING = "stopping"

    FINISHED = "finished"

    ERROR = "error"