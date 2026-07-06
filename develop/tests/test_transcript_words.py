from models.transcript import Transcript, Segment, Word


transcript = Transcript()

segment = Segment(
    start=0.0,
    end=2.5,
    speaker="LOCAL",
    text="Buenos días.",
    words=[
        Word(start=0.0, end=0.7, text="Buenos", confidence=0.95),
        Word(start=0.8, end=1.3, text="días", confidence=0.94),
    ]
)

transcript.add_segment(segment)

print(transcript.as_dict())

assert len(transcript.segments) == 1
assert len(transcript.segments[0].words) == 2

print()
print("Prueba satisfactoria.")