"""
transcript_storage_service.py

Persistencia de Transcript.
"""

import json

from models.transcript import Transcript, Segment, Word


class TranscriptStorageService:

    def save(self, transcript: Transcript, filename):

        with open(filename, "w", encoding="utf-8") as file:

            json.dump(
                transcript.as_dict(),
                file,
                ensure_ascii=False,
                indent=4
            )

    def save_json(self, data, filename):

        with open(filename, "w", encoding="utf-8") as file:

            json.dump(
                data.as_dict(),
                file,
                ensure_ascii=False,
                indent=4
            )

    def load(self, filename) -> Transcript:

        with open(filename, "r", encoding="utf-8") as file:

            data = json.load(file)

        transcript = Transcript()

        for seg in data["segments"]:

            segment = Segment(
                start=seg["start"],
                end=seg["end"],
                speaker=seg["speaker"],
                text=seg["text"]
            )

            for word in seg.get("words", []):

                segment.words.append(
                    Word(
                        start=word["start"],
                        end=word["end"],
                        text=word["text"],
                        confidence=word.get("confidence")
                    )
                )

            transcript.add_segment(segment)

        return transcript