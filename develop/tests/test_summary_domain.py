from models.artifacts.summary import Summary


summary = Summary(
    artifact_type="summary",
    provider="ollama",
    model="qwen2.5:3b",
    prompt_version="v1",
    title="Resumen Ejecutivo",
    executive_summary="La reunión revisó el avance del proyecto.",
    key_points=[
        "Se aprobó AI-004.",
        "Se mantiene la estrategia offline.",
        "Se continuará con AI-005."
    ]
)

print(summary.as_dict())

print()
print("Dominio Summary validado correctamente.")