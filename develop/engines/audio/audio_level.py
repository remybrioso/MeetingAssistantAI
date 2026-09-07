"""
Funciones pequeñas para convertir bloques PCM en niveles visuales.
"""

import numpy as np


AUDIO_LEVEL_FLOOR_DBFS = -60.0


def calculate_audio_level(samples) -> float:
    """
    Calcula un nivel normalizado a partir de un bloque PCM.

    El RMS se convierte a dBFS y se interpola entre -60 dBFS y
    0 dBFS. El bloque puede ser mono o multicanal y nunca se modifica.
    """

    try:
        values = np.asarray(samples)
    except (TypeError, ValueError):
        return 0.0

    if values.size == 0:
        return 0.0

    try:
        with np.errstate(
            over="ignore",
            invalid="ignore",
        ):
            rms = float(
                np.sqrt(
                    np.mean(
                        np.square(
                            values,
                            dtype=np.float64,
                        )
                    )
                )
            )
    except (TypeError, ValueError, FloatingPointError):
        return 0.0

    if np.isinf(rms):
        return 1.0

    if not np.isfinite(rms) or rms <= 0.0:
        return 0.0

    dbfs = 20.0 * np.log10(rms)
    normalized = (
        dbfs - AUDIO_LEVEL_FLOOR_DBFS
    ) / -AUDIO_LEVEL_FLOOR_DBFS

    return float(
        np.clip(
            normalized,
            0.0,
            1.0,
        )
    )
