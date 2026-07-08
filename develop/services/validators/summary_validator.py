"""
summary_validator.py

Validador del dominio Summary.
"""

from models.artifacts.summary import Summary


class SummaryValidator:

    MIN_POINTS = 3
    MAX_POINTS = 10

    MIN_SUMMARY_LENGTH = 30
    MAX_SUMMARY_LENGTH = 5000

    def validate(
        self,
        summary: Summary
    ) -> tuple[bool, list[str]]:

        errors = []

        if not summary.title.strip():
            errors.append("El título está vacío.")

        if not summary.executive_summary.strip():
            errors.append("El resumen ejecutivo está vacío.")

        summary_length = len(summary.executive_summary)

        if summary_length < self.MIN_SUMMARY_LENGTH:
            errors.append(
                "El resumen ejecutivo es demasiado corto."
            )

        if summary_length > self.MAX_SUMMARY_LENGTH:
            errors.append(
                "El resumen ejecutivo es demasiado largo."
            )

        if len(summary.key_points) < self.MIN_POINTS:
            errors.append(
                f"Debe contener al menos {self.MIN_POINTS} puntos clave."
            )

        if len(summary.key_points) > self.MAX_POINTS:
            errors.append(
                f"No debe contener más de {self.MAX_POINTS} puntos clave."
            )

        for index, point in enumerate(summary.key_points, start=1):

            if not point.strip():
                errors.append(
                    f"El punto clave #{index} está vacío."
                )

        return (
            len(errors) == 0,
            errors
        )