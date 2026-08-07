import pytest

from models.transcript import Transcript
from services.artifact_generator import (
    ArtifactGenerator,
)


class FakeArtifactGenerator(
    ArtifactGenerator
):

    def __init__(self) -> None:
        self.received_transcript = None
        self.artifact = object()

    def generate(
        self,
        transcript: Transcript,
    ):
        self.received_transcript = transcript

        return self.artifact


def test_artifact_generator_contract_can_be_implemented() -> None:
    transcript = Transcript()

    generator = FakeArtifactGenerator()

    result = generator.generate(
        transcript
    )

    assert result is generator.artifact

    assert (
        generator.received_transcript
        is transcript
    )


def test_artifact_generator_cannot_be_instantiated_directly() -> None:
    with pytest.raises(
        TypeError,
    ):
        ArtifactGenerator()