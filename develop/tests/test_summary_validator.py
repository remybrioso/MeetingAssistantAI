from models.artifacts.summary import Summary
from services.validators.summary_validator import SummaryValidator


validator = SummaryValidator()

summary = Summary(
    artifact_type="summary",
    provider="ollama",
    model="qwen2.5:3b",
    prompt_version="summary_v1",
    title="Resumen Ejecutivo",
    executive_summary=(
        "Durante la reunión se revisó el avance del proyecto "
        "Meeting Assistant AI y se aprobaron los siguientes pasos."
    ),
    key_points=[
        "Se aprobó AI-005.",
        "Se mantiene el procesamiento offline.",
        "Se iniciará el Sprint de Hardening."
    ]
)

valid, errors = validator.validate(summary)

print(f"Válido: {valid}")

if errors:
    print(errors)

assert valid

print()
print("SummaryValidator validado correctamente.")