import json

from agent.models import LocalLLMConfig, LocalOpenAIClient


class FakeHTTPClient:
    def __init__(self):
        self.requests = []

    def post_json(self, url, payload, headers, timeout):
        self.requests.append((url, payload, headers, timeout))
        return {"choices": [{"message": {"content": "SELECT * FROM filmes_publicos LIMIT 5"}}]}


def test_config_reads_openai_compatible_environment(monkeypatch):
    monkeypatch.setenv("LOCAL_LLM_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("LOCAL_LLM_MODEL", "qwen2.5-coder:7b")
    config = LocalLLMConfig.from_env()
    assert config.base_url == "http://localhost:11434/v1"
    assert config.model == "qwen2.5-coder:7b"


def test_client_sends_chat_completion_request():
    fake = FakeHTTPClient()
    client = LocalOpenAIClient(LocalLLMConfig(base_url="http://local/v1", model="qwen"), http_client=fake)
    content = client.complete([{"role": "user", "content": "gere sql"}])
    assert content.startswith("SELECT")
    url, payload, headers, timeout = fake.requests[0]
    assert url == "http://local/v1/chat/completions"
    assert payload["model"] == "qwen"
    assert headers["Authorization"].startswith("Bearer")
