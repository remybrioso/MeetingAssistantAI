"""
transcript_validator.py

Valida si el análisis de una transcripción contiene
evidencia suficiente para continuar el Knowledge Pipeline.
"""

from models.transcript_analysis import TranscriptAnalysis


class TranscriptValidator:
    """
    Toma decisiones a partir de un TranscriptAnalysis.

    No analiza segmentos.
    No abre archivos.
    No consulta proveedores externos.
    """

    MIN_WORDS = 20
    MIN_CHARACTERS = 80

    def validate(
        self,
        analysis: TranscriptAnalysis,
    ) -> tuple[bool, list[str]]:
        """
        Determina si una transcripción contiene evidencia suficiente.

        Returns:
            tuple[bool, list[str]]:
                - bool: True cuando puede continuar el pipeline.
                - list[str]: errores encontrados.
        """

        errors: list[str] = []

        non_empty_segments = (
            analysis.total_segments
            - analysis.empty_segments
        )

        if analysis.total_segments == 0:
            errors.append(
                "La transcripción no contiene segmentos."
            )

        if (
            analysis.total_segments > 0
            and non_empty_segments == 0
        ):
            errors.append(
                "La transcripción no contiene segmentos con texto."
            )

        if analysis.total_words < self.MIN_WORDS:
            errors.append(
                "La transcripción no contiene suficientes palabras "
                f"para generar una minuta. Mínimo requerido: "
                f"{self.MIN_WORDS}."
            )

        if analysis.total_characters < self.MIN_CHARACTERS:
            errors.append(
                "La transcripción no contiene suficiente contenido "
                f"para generar una minuta. Mínimo requerido: "
                f"{self.MIN_CHARACTERS} caracteres."
            )

        return (
            len(errors) == 0,
            errors,
        )