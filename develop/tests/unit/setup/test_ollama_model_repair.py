from dataclasses import dataclass, field

from services.setup.repair_action import RepairAction
from services.setup.repairs.ollama_model_repair import (
    OllamaModelRepair,
)


@dataclass
class FakeHealth:
    connected: bool
    model_found: bool
    model: str = "qwen2.5:3b"
    available_models: list[str] = field(
        default_factory=list
    )


class FakeProvider:

    def __init__(
        self,
        health_results,
        pull_result=None,
        pull_error=None,
    ) -> None:
        self.health_results = list(
            health_results
        )
        self.pull_result = (
            pull_result
            or {
                "status": "success",
            }
        )
        self.pull_error = pull_error
        self.pull_count = 0
        self.health_count = 0

    def health(self):
        result = self.health_results[
            self.health_count
        ]
        self.health_count += 1
        return result

    def pull_model(self):
        self.pull_count += 1

        if self.pull_error is not None:
            raise self.pull_error

        return self.pull_result


def test_ollama_model_repair_downloads_and_verifies() -> None:
    provider = FakeProvider(
        health_results=[
            FakeHealth(
                connected=True,
                model_found=False,
            ),
            FakeHealth(
                connected=True,
                model_found=True,
                available_models=[
                    "qwen2.5:3b",
                ],
            ),
        ]
    )

    repair = OllamaModelRepair(
        provider=provider
    )

    result = repair(
        {
            "capability_id": (
                "artificial-intelligence"
            ),
        }
    )

    assert provider.pull_count == 1
    assert provider.health_count == 2
    assert result.succeeded is True
    assert (
        result.action
        == RepairAction.DOWNLOAD_AI_MODEL
    )
    assert (
        result.details["model"]
        == "qwen2.5:3b"
    )
    assert (
        result.details["pull_status"]
        == "success"
    )


def test_ollama_model_repair_is_idempotent() -> None:
    provider = FakeProvider(
        health_results=[
            FakeHealth(
                connected=True,
                model_found=True,
                available_models=[
                    "qwen2.5:3b",
                ],
            ),
        ]
    )

    repair = OllamaModelRepair(
        provider=provider
    )

    result = repair({})

    assert result.succeeded is True
    assert (
        result.details["already_available"]
        is True
    )
    assert provider.pull_count == 0


def test_ollama_model_repair_requires_running_provider() -> None:
    provider = FakeProvider(
        health_results=[
            FakeHealth(
                connected=False,
                model_found=False,
            ),
        ]
    )

    repair = OllamaModelRepair(
        provider=provider
    )

    result = repair({})

    assert result.failed is True
    assert (
        result.details["reason"]
        == "provider-unavailable"
    )
    assert provider.pull_count == 0


def test_ollama_model_repair_verifies_model_after_pull() -> None:
    provider = FakeProvider(
        health_results=[
            FakeHealth(
                connected=True,
                model_found=False,
            ),
            FakeHealth(
                connected=True,
                model_found=False,
                available_models=[],
            ),
        ]
    )

    repair = OllamaModelRepair(
        provider=provider
    )

    result = repair({})

    assert result.failed is True
    assert (
        result.details["reason"]
        == "model-not-found-after-pull"
    )


def test_ollama_model_repair_reports_pull_exception() -> None:
    provider = FakeProvider(
        health_results=[
            FakeHealth(
                connected=True,
                model_found=False,
            ),
        ],
        pull_error=RuntimeError(
            "pull failed"
        ),
    )

    repair = OllamaModelRepair(
        provider=provider
    )

    result = repair({})

    assert result.failed is True
    assert (
        result.details["reason"]
        == "model-pull-failed"
    )
    assert (
        result.details["error"]
        == "pull failed"
    )
