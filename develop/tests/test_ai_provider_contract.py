from providers.ai_provider import AIProvider


class FakeAIProvider(AIProvider):

    def generate(self, prompt: str) -> str:
        return f"Respuesta simulada para: {prompt}"


provider = FakeAIProvider()

response = provider.generate(
    "Resume esta reunión."
)

print(response)

assert "Respuesta simulada" in response

print()
print("Prueba satisfactoria.")