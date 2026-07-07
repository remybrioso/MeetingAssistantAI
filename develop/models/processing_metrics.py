from dataclasses import dataclass, asdict


@dataclass
class ProcessingMetrics:

    audio_duration: float = 0.0
    transcription_time: float = 0.0
    save_time: float = 0.0
    total_time: float = 0.0

    segments: int = 0
    words: int = 0

    language: str = "unknown"

    @property
    def speed_factor(self):

        if self.total_time <= 0:
            return 0.0

        return self.audio_duration / self.total_time

    def as_dict(self):

        data = asdict(self)

        data["speed_factor"] = round(
            self.speed_factor,
            2
        )

        return data