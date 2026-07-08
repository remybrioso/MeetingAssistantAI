from services.response_parser import ResponseParser


response = """
{
    "title": "Resumen Ejecutivo",
    "executive_summary": "Durante la reunión se revisó el avance del proyecto Meeting Assistant AI.",
    "key_points": [
        "Se aprobó AI-006.",
        "Se centralizó la persistencia de artefactos.",
        "Se continuará con ResponseParser."
    ]
}
"""

parser = ResponseParser()

summary = parser.parse_summary(
    response=response,
    provider="ollama",
    model="qwen2.5:3b",
    prompt_version="summary_v1"
)

print(summary.as_dict())

assert summary.title == "Resumen Ejecutivo"
assert len(summary.key_points) == 3

print()
print("ResponseParser validado correctamente.")