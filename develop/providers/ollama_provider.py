"""
ollama_provider.py

Proveedor local de IA usando Ollama.
"""

import time

import requests

from ai_config import (
    HEALTH_TIMEOUT,
    OLLAMA_MODEL,
    OLLAMA_URL,
    REQUEST_TIMEOUT,
)
from models.provider_health import ProviderHealth
from providers.ai_provider import AIProvider


class OllamaProvider(AIProvider):

    PROVIDER_NAME = "Ollama"

    def __init__(
        self,
        model: str = OLLAMA_MODEL,
        base_url: str = OLLAMA_URL,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")

        self.generate_url = (
            f"{self.base_url}/api/generate"
        )

        self.tags_url = (
            f"{self.base_url}/api/tags"
        )

    def generate(
        self,
        prompt: str,
        output_schema: dict | None = None,
    ) -> str:
        """
        Genera contenido JSON mediante Ollama.

        El proveedor no conoce artefactos concretos como
        Summary o MeetingReport.

        Cuando recibe output_schema, utiliza dicho JSON
        Schema como formato estructurado.

        Cuando no recibe schema, exige únicamente una
        respuesta JSON genérica.
        """

        if not isinstance(
            prompt,
            str,
        ):
            raise TypeError(
                "prompt debe ser una cadena."
            )

        if not prompt.strip():
            raise ValueError(
                "prompt no puede estar vacío."
            )

        if (
            output_schema is not None
            and not isinstance(
                output_schema,
                dict,
            )
        ):
            raise TypeError(
                "output_schema debe ser un diccionario "
                "o None."
            )

        response_format = (
            output_schema
            if output_schema is not None
            else "json"
        )

        response = requests.post(
            self.generate_url,
            json={
                "model": self.model,
                "prompt": prompt,
                "format": response_format,
                "stream": False,
                "think": False,
                "options": {
                    "temperature": 0.1,
                    "num_ctx": 8192,
                },
            },
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        payload = response.json()

        generated_text = payload.get(
            "response",
            "",
        ).strip()

        if not generated_text:
            raise ValueError(
                "Ollama devolvió una respuesta vacía."
            )

        return generated_text

    def health(
        self,
    ) -> ProviderHealth:
        start_time = time.perf_counter()

        try:
            response = requests.get(
                self.tags_url,
                timeout=HEALTH_TIMEOUT,
            )

            response.raise_for_status()

            payload = response.json()

            models = self._extract_model_names(
                payload
            )

            response_time_ms = round(
                (
                    time.perf_counter()
                    - start_time
                ) * 1000,
                2,
            )

            model_found = self._model_exists(
                models
            )

            if not model_found:
                return ProviderHealth(
                    provider=self.PROVIDER_NAME,
                    connected=True,
                    model_found=False,
                    model=self.model,
                    response_time_ms=response_time_ms,
                    available_models=models,
                    message=(
                        "Ollama está disponible, "
                        "pero el modelo configurado "
                        "no está instalado."
                    ),
                )

            return ProviderHealth(
                provider=self.PROVIDER_NAME,
                connected=True,
                model_found=True,
                model=self.model,
                response_time_ms=response_time_ms,
                available_models=models,
                message=(
                    "Ollama y el modelo configurado "
                    "están disponibles."
                ),
            )

        except Exception as ex:
            response_time_ms = round(
                (
                    time.perf_counter()
                    - start_time
                ) * 1000,
                2,
            )

            return ProviderHealth(
                provider=self.PROVIDER_NAME,
                connected=False,
                model_found=False,
                model=self.model,
                response_time_ms=response_time_ms,
                available_models=[],
                message=(
                    "No fue posible conectar con Ollama."
                ),
                error=str(ex),
            )

    def _model_exists(
        self,
        available_models: list[str],
    ) -> bool:
        configured_model = (
            self.model
            .strip()
            .lower()
        )

        normalized_models = {
            model.strip().lower()
            for model in available_models
        }

        return (
            configured_model
            in normalized_models
        )

    @staticmethod
    def _extract_model_names(
        payload: dict,
    ) -> list[str]:
        models = []

        for model_data in payload.get(
            "models",
            [],
        ):
            model_name = (
                model_data.get(
                    "name"
                )
                or model_data.get(
                    "model"
                )
            )

            if model_name:
                models.append(
                    model_name
                )

        return models