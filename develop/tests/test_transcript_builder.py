from builders.transcript_builder import TranscriptBuilder


raw_segments = [
    {
        "start": 0.0,
        "end": 2.5,
        "speaker": "LOCAL",
        "text": "Buenos días.",
        "words": [
            {
                "start": 0.0,
                "end": 0.8,
                "text": "Buenos",
                "confidence": 0.95
            },
            {
                "start": 0.9,
                "end": 1.4,
                "text": "días",
                "confidence": 0.94
            }
        ]
    },
    {
        "start": 2.6,
        "end": 5.0,
        "speaker": "REMOTE",
        "text": "Buenos días, ¿cómo estás?"
    }
]

builder = TranscriptBuilder()

transcript = builder.from_segments(raw_segments)

print(transcript.as_dict())

assert len(transcript.segments) == 2
assert transcript.segments[0].speaker == "LOCAL"
assert transcript.segments[1].speaker == "REMOTE"
assert len(transcript.segments[0].words) == 2

print()
print("Prueba satisfactoria.")