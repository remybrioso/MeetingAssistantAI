import requests

from ai_config import REQUEST_TIMEOUT
from providers.ollama_provider import (
    OllamaProvider,
)


class FakeResponse:

    def __init__(
        self,
        payload: dict,
        *,
        status_code: int = 200,
        text: str = "",
        error: bool = False,
    ) -> None:
        self.payload = payload
        self.status_code = status_code
        self.text = text
        self.error = error
        self.raise_called = False

    def raise_for_status(
        self,
    ) -> None:
        self.raise_called = True

        if self.error:
            raise requests.HTTPError(
                f"{self.status_code} Client Error",
                response=self,
            )

    def json(
        self,
    ) -> dict:
        return self.payload


def test_generate_sends_structured_output_schema(
    monkeypatch,
) -> None:
    calls = []

    schema = {
        "type": "object",
        "properties": {
            "value": {
                "type": "string",
            },
        },
        "required": [
            "value",
        ],
    }

    response = FakeResponse(
        {
            "response": (
                '{"value":"ok"}'
            ),
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
        base_url=(
            "http://localhost:11434"
        ),
    )

    result = provider.generate(
        "Genera JSON.",
        schema,
    )

    assert result == (
        '{"value":"ok"}'
    )

    assert response.raise_called is True

    assert calls == [
        {
            "url": (
                "http://localhost:11434"
                "/api/generate"
            ),
            "json": {
                "model": "qwen2.5:3b",
                "prompt": (
                    "Genera JSON."
                ),
                "format": schema,
                "stream": False,
                "think": False,
                "options": {
                    "temperature": 0.1,
                    "num_ctx": 8192,
                },
            },
            "timeout": REQUEST_TIMEOUT,
        }
    ]


def test_generate_uses_generic_json_without_schema(
    monkeypatch,
) -> None:
    captured = {}

    response = FakeResponse(
        {
            "response": (
                '{"ok":true}'
            ),
        }
    )

    def fake_post(
        url,
        *,
        json,
        timeout,
    ):
        captured.update(
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

    provider = OllamaProvider()

    result = provider.generate(
        "Genera JSON."
    )

    assert result == (
        '{"ok":true}'
    )

    assert (
        captured[
            "json"
        ][
            "format"
        ]
        == "json"
    )


def test_generate_preserves_ollama_http_error_detail(
    monkeypatch,
) -> None:
    error_detail = (
        "Failed to initialize samplers: "
        "failed to parse grammar"
    )

    response = FakeResponse(
        {
            "error": error_detail,
        },
        status_code=400,
        text=(
            '{"error":"'
            + error_detail
            + '"}'
        ),
        error=True,
    )

    monkeypatch.setattr(
        "providers.ollama_provider.requests.post",
        lambda *args, **kwargs: response,
    )

    provider = OllamaProvider()

    try:
        provider.generate(
            "Genera JSON.",
            {
                "type": "object",
            },
        )
    except requests.HTTPError as ex:
        error_message = str(
            ex
        )

        assert (
            "HTTP 400"
            in error_message
        )

        assert (
            error_detail
            in error_message
        )

        assert (
            ex.response
            is response
        )
    else:
        raise AssertionError(
            "Se esperaba requests.HTTPError."
        )


def test_generate_falls_back_to_response_text_for_http_error_detail(
    monkeypatch,
) -> None:
    response = FakeResponse(
        {},
        status_code=500,
        text=(
            "internal Ollama failure"
        ),
        error=True,
    )

    monkeypatch.setattr(
        "providers.ollama_provider.requests.post",
        lambda *args, **kwargs: response,
    )

    provider = OllamaProvider()

    try:
        provider.generate(
            "Genera JSON."
        )
    except requests.HTTPError as ex:
        assert (
            "internal Ollama failure"
            in str(ex)
        )
    else:
        raise AssertionError(
            "Se esperaba requests.HTTPError."
        )
