import time
from llama_cpp import Llama


MODEL_PATH = "resources/models/qwen2.5-3b-instruct-q4_k_m.gguf"

PROMPT = """
Eres un asistente experto en reuniones.
Resume en tres puntos el siguiente texto:

Durante la reunión se revisó el avance del proyecto Meeting Assistant AI.
Se acordó mantener el procesamiento offline, usar modelos locales y continuar
con el diseño del AI Pipeline antes de implementar nuevas funciones.
"""


print("=" * 60)
print("Meeting Assistant AI - LLM Laboratory")
print("=" * 60)

print()
print("Cargando modelo...")

load_start = time.time()

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=4096,
    n_threads=8,
    verbose=False
)

load_time = time.time() - load_start

print(f"Modelo cargado en {load_time:.2f} segundos")

print()
print("Generando respuesta...")

generate_start = time.time()

response = llm(
    PROMPT,
    max_tokens=250,
    temperature=0.2,
    stop=["</s>"]
)

generate_time = time.time() - generate_start

text = response["choices"][0]["text"].strip()

print()
print("=" * 60)
print("RESPUESTA")
print("=" * 60)
print(text)

print()
print("=" * 60)
print("MÉTRICAS")
print("=" * 60)
print(f"Tiempo carga modelo: {load_time:.2f} s")
print(f"Tiempo generación: {generate_time:.2f} s")
print("Prueba finalizada.")