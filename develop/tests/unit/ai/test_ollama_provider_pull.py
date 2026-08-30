import pytest

from ai_config import OLLAMA_PULL_TIMEOUT
from providers.ollama_provider import OllamaProvider


class FakeResponse:

    def __init__(
        self,
        payload: dict,
    ) -> None:
        self.payload = payload
        self.raise_called = False

    def raise_for_status(self) -> None:
        self.raise_called = True

    def json(self) -> dict:
        return self.payload


def test_ollama_provider_pulls_configured_model(
    monkeypatch,
) -> None:
    calls = []
    response = FakeResponse(
        {
            "status": "success",
        }
    )

    def fake_post(
        url,
        *,
        json,
        timeout,
    ):
        calls.append(
            {
                "url": url,
                "json": json,
                "timeout": timeout,
            }
        )
        return response

    monkeypatch.setattr(
        "providers.ollama_provider.requests.post",
        fake_post,
    )

    provider = OllamaProvider(
        model="qwen2.5:3b",
        base_url="http://localhost:11434",
    )

    result = provider.pull_model()

    assert response.raise_called is True
    assert result == {
        "status": "success",
    }

    assert calls == [
        {
            "url": (
                "http://localhost:11434/api/pull"
            ),
            "json": {
                "model": "qwen2.5:3b",
                "stream": False,
            },
            "timeout": OLLAMA_PULL_TIMEOUT,
        }
    ]


def test_ollama_provider_rejects_unconfirmed_pull(
    monkeypatch,
) -> None:
    response = FakeResponse(
        {
            "status": "pulling manifest",
        }
    )

    monkeypatch.setattr(
        "providers.ollama_provider.requests.post",
        lambda *args, **kwargs: response,
    )

    provider = OllamaProvider()

    with pytest.raises(
        ValueError,
        match="no confirmó",
    ):
        provider.pull_model()
