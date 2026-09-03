# src/nikhil/amsha/llm_factory/adapters/lmstudio_lifecycle_client.py
import json
import time
import urllib.error
import urllib.request
from typing import Any, Optional
from urllib.parse import urlsplit, urlunsplit

from amsha.llm_factory.domain.model.lmstudio_lifecycle_config import LMStudioLifecycleConfig


class LMStudioLifecycleError(RuntimeError):
    """LM Studio's model-management API is unreachable or returned an unexpected result."""


class LMStudioLifecycleClient:
    """
    Talks to LM Studio's local model-management REST API
    (GET/POST /api/v1/models, /api/v1/models/load, /api/v1/models/unload) —
    a different path prefix than the OpenAI-compatible /v1/... endpoints
    Amsha already calls for chat completions, on the same host:port.

    LM Studio only. Local only.
    """

    def __init__(self, base_url: str, timeout: float = 30.0, load_timeout: float = 300.0):
        self._api_root = self._to_management_root(base_url)
        self._timeout = timeout
        # Loading a multi-GB model from disk routinely exceeds a normal request
        # timeout — confirmed live against a real LM Studio instance, a 6.8GB
        # model took >30s. Only /models/load uses this longer timeout.
        self._load_timeout = load_timeout

    @staticmethod
    def _to_management_root(base_url: str) -> str:
        parts = urlsplit(base_url)
        path = parts.path.rstrip("/")
        if path.endswith("/v1"):
            path = path[: -len("/v1")]
        return urlunsplit((parts.scheme, parts.netloc, path + "/api/v1", "", ""))

    def _request(self, method: str, path: str, body: Optional[dict] = None, timeout: Optional[float] = None) -> Any:
        url = f"{self._api_root}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json"} if data is not None else {}
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout if timeout is not None else self._timeout) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            raise LMStudioLifecycleError(f"LM Studio management API unreachable at {url}: {exc}") from exc

    def _request_with_retry(self, method: str, path: str, body: Optional[dict] = None,
                             timeout: Optional[float] = None, max_retries: int = 0,
                             retry_delay: float = 2.0) -> Any:
        last_exc: Optional[LMStudioLifecycleError] = None
        for attempt in range(max_retries + 1):
            try:
                return self._request(method, path, body, timeout=timeout)
            except LMStudioLifecycleError as exc:
                last_exc = exc
                if attempt < max_retries:
                    time.sleep(retry_delay)
        assert last_exc is not None
        raise last_exc

    def list_models(self) -> list:
        return self._request("GET", "/models").get("models", [])

    def all_loaded_instances(self) -> list:
        """Returns [(model_key, instance_dict), ...] across every model LM Studio knows about."""
        result = []
        for model in self.list_models():
            for instance in model.get("loaded_instances", []):
                result.append((model.get("key"), instance))
        return result

    def unload(self, instance_id: str) -> None:
        self._request("POST", "/models/unload", {"instance_id": instance_id})

    def load(self, model_id: str, context_length: Optional[int] = None,
              max_retries: int = 0, retry_delay: float = 2.0) -> dict:
        body = {"model": model_id, "echo_load_config": True}
        if context_length is not None:
            body["context_length"] = context_length

        result = self._request_with_retry("POST", "/models/load", body, timeout=self._load_timeout,
                                          max_retries=max_retries, retry_delay=retry_delay)
        applied = (result.get("load_config") or {}).get("context_length")
        if context_length is not None and applied != context_length:
            raise LMStudioLifecycleError(
                f"LM Studio loaded '{model_id}' with context_length={applied}, requested {context_length}"
            )
        return result

    def ensure_loaded(self, config: LMStudioLifecycleConfig) -> None:
        """
        Guardrail run before LLMBuilder.build() constructs the crewai.LLM(...):
        - unloads any other resident model when unload_other_models=True
        - if the target model is loaded with the wrong context_length, unloads
          and reloads it (LM Studio has no in-place context-length change)
        - loads the target model if it isn't loaded at all
        No-op entirely when config.enabled is False.
        """
        if not config.enabled:
            return

        target_instance = None
        for model_key, instance in self.all_loaded_instances():
            if model_key == config.model_id:
                target_instance = instance
            elif config.unload_other_models:
                self.unload(instance["id"])

        if target_instance is None:
            self.load(config.model_id, config.context_length,
                      config.max_load_retries, config.load_retry_delay_seconds)
            return

        current_context = (target_instance.get("config") or {}).get("context_length")
        if config.context_length is not None and current_context != config.context_length:
            self.unload(target_instance["id"])
            self.load(config.model_id, config.context_length,
                      config.max_load_retries, config.load_retry_delay_seconds)
