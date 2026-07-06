from models.transcript import Transcript, Segment


transcript = Transcript()

transcript.add_segment(
    Segment(
        start=0.0,
        end=2.5,
        speaker="LOCAL",
        text="Buenos días."
    )
)

transcript.add_segment(
    Segment(
        start=2.6,
        end=5.0,
        speaker="REMOTE",
        text="Buenos días, ¿cómo estás?"
    )
)

print(transcript.as_dict())
print()
print("Cantidad de segmentos:", len(transcript.segments))
print("Prueba satisfactoria.")