from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LocalLLMConfig:
    base_url: str = "http://localhost:11434/v1"
    model: str = "qwen2.5-coder:7b"
    api_key: str = "local-not-needed"
    timeout: float = 60.0

    @classmethod
    def from_env(cls) -> "LocalLLMConfig":
        return cls(
            base_url=os.getenv("LOCAL_LLM_BASE_URL", cls.base_url).rstrip("/"),
            model=os.getenv("LOCAL_LLM_MODEL", cls.model),
            api_key=os.getenv("LOCAL_LLM_API_KEY", cls.api_key),
            timeout=float(os.getenv("LOCAL_LLM_TIMEOUT", "60")),
        )


class HTTPClient(Protocol):
    def post_json(self, url: str, payload: dict, headers: dict, timeout: float) -> dict: ...


class UrllibHTTPClient:
    def post_json(self, url: str, payload: dict, headers: dict, timeout: float) -> dict:
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **headers}, method="POST")
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - endpoint local/configurado pelo usuário
            return json.loads(response.read().decode("utf-8"))


class LocalOpenAIClient:
    def __init__(self, config: LocalLLMConfig | None = None, http_client: HTTPClient | None = None):
        self.config = config or LocalLLMConfig.from_env()
        self.http_client = http_client or UrllibHTTPClient()

    def complete(self, messages: list[dict[str, str]], temperature: float = 0.0) -> str:
        payload = {"model": self.config.model, "messages": messages, "temperature": temperature}
        headers = {"Authorization": f"Bearer {self.config.api_key}"}
        data = self.http_client.post_json(f"{self.config.base_url}/chat/completions", payload, headers, self.config.timeout)
        return data["choices"][0]["message"]["content"].strip()
