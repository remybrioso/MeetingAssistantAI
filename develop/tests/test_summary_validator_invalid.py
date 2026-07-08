from models.artifacts.summary import Summary
from services.validators.summary_validator import SummaryValidator


validator = SummaryValidator()

summary = Summary(
    artifact_type="summary",
    provider="ollama",
    model="qwen2.5:3b",
    prompt_version="summary_v1",
    title="",
    executive_summary="Muy corto",
    key_points=[""]
)

valid, errors = validator.validate(summary)

print(f"Válido: {valid}")

for error in errors:
    print(f"- {error}")

assert not valid
assert len(errors) > 0

print()
print("Validación negativa correcta.")