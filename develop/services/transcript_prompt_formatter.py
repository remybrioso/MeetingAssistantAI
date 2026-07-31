"""
transcript_prompt_formatter.py

Convierte un Transcript en contenido textual adecuado
para ser enviado al servicio de generación de resúmenes.
"""

import json

from models.transcript import Transcript


class TranscriptPromptFormatter:
    """
    Serializa un Transcript para su inclusión en prompts.

    Este componente no accede al sistema de archivos,
    no invoca proveedores de IA y no modifica el Transcript.
    """

    def format(
        self,
        transcript: Transcript,
    ) -> str:
        """
        Convierte un Transcript en una cadena JSON legible.

        Args:
            transcript:
                Transcripción que será incluida en el prompt.

        Returns:
            str:
                Representación JSON del Transcript.

        Raises:
            TypeError:
                Si el argumento no es un Transcript.
        """

        if not isinstance(
            transcript,
            Transcript,
        ):
            raise TypeError(
                "transcript debe ser una instancia "
                "de Transcript."
            )

        return json.dumps(
            transcript.as_dict(),
            ensure_ascii=False,
            indent=4,
        )