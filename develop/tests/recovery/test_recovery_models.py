from datetime import datetime, timedelta, timezone

import pytest

from application.recovery.models import (
    AutomaticAction,
    AutomaticActionType,
    Difficulty,
    HelpLink,
    RecoveryExperience,
    RecoveryResult,
    RecoveryResultStatus,
    RecoveryStep,
    Severity,
)


def build_experience() -> RecoveryExperience:
    return RecoveryExperience(
        recovery_id="CONFIGURE_SYSTEM_AUDIO",
        title="Configurar audio del sistema",
        summary="MAI no puede escuchar el audio reproducido por el equipo.",
        explanation="El micrófono funciona, pero falta una fuente de audio del sistema.",
        impact="Es posible que solamente se transcriba la voz del usuario.",
        severity=Severity.RECOMMENDED,
        difficulty=Difficulty.EASY,
        estimated_time=timedelta(minutes=2),
        can_continue=True,
        steps=(
            RecoveryStep(
                order=1,
                title="Abrir sonido",
                description="Abre la configuración de sonido de Windows.",
            ),
            RecoveryStep(
                order=2,
                title="Seleccionar fuente",
                description="Selecciona una fuente compatible de audio del sistema.",
            ),
        ),
        automatic_actions=(
            AutomaticAction(
                action_id="AUTO_CONFIGURE_SYSTEM_AUDIO",
                label="Configurar automáticamente",
                description="MAI intentará configurar una fuente compatible.",
                action_type=AutomaticActionType.CONFIRMATION_REQUIRED,
            ),
        ),
        help_links=(
            HelpLink(
                label="Abrir guía",
                url="mai://help/audio/configure-system-audio",
            ),
        ),
    )


def test_recovery_experience_is_created() -> None:
    experience = build_experience()

    assert experience.recovery_id == "CONFIGURE_SYSTEM_AUDIO"
    assert experience.steps[0].order == 1
    assert experience.can_continue is True


def test_recovery_step_rejects_zero_order() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        RecoveryStep(order=0, title="Paso", description="Descripción")


def test_recovery_experience_rejects_duplicate_step_orders() -> None:
    with pytest.raises(ValueError, match="orders must be unique"):
        RecoveryExperience(
            recovery_id="TEST",
            title="Título",
            summary="Resumen",
            explanation="Explicación",
            impact="Impacto",
            severity=Severity.WARNING,
            difficulty=Difficulty.MODERATE,
            estimated_time=None,
            can_continue=False,
            steps=(
                RecoveryStep(1, "Paso A", "Descripción A"),
                RecoveryStep(1, "Paso B", "Descripción B"),
            ),
        )


def test_recovery_experience_rejects_unsorted_steps() -> None:
    with pytest.raises(ValueError, match="must be ordered"):
        RecoveryExperience(
            recovery_id="TEST",
            title="Título",
            summary="Resumen",
            explanation="Explicación",
            impact="Impacto",
            severity=Severity.WARNING,
            difficulty=Difficulty.MODERATE,
            estimated_time=None,
            can_continue=False,
            steps=(
                RecoveryStep(2, "Paso B", "Descripción B"),
                RecoveryStep(1, "Paso A", "Descripción A"),
            ),
        )


def test_destructive_action_cannot_run_in_background() -> None:
    with pytest.raises(ValueError, match="Destructive actions"):
        AutomaticAction(
            action_id="DELETE",
            label="Eliminar",
            description="Elimina un recurso.",
            action_type=AutomaticActionType.BACKGROUND,
            destructive=True,
        )


def test_recovery_result_requires_timezone_aware_datetime() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        RecoveryResult(
            recovery_id="TEST",
            status=RecoveryResultStatus.SUCCEEDED,
            occurred_at=datetime(2026, 7, 17),
        )


def test_recovery_result_details_are_immutable() -> None:
    result = RecoveryResult(
        recovery_id="TEST",
        status=RecoveryResultStatus.SUCCEEDED,
        details={"attempt": "1"},
        occurred_at=datetime.now(timezone.utc),
    )

    with pytest.raises(TypeError):
        result.details["attempt"] = "2"


def test_recovery_models_are_immutable() -> None:
    experience = build_experience()

    with pytest.raises(Exception):
        experience.title = "Otro título"
