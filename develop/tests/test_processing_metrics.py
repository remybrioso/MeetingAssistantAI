from models.processing_metrics import ProcessingMetrics


metrics = ProcessingMetrics(

    audio_duration=30,

    transcription_time=5.8,

    save_time=0.1,

    total_time=5.9,

    segments=8,

    words=72,

    language="es"
)

print(metrics.as_dict())

assert metrics.speed_factor > 5

print()
print("Prueba satisfactoria.")