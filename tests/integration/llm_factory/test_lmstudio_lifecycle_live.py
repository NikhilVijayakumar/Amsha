"""
Live integration test against a real local LM Studio server (proposal 14).
Skipped automatically if LM Studio's management API isn't reachable at
http://localhost:1234 — this test makes real HTTP calls and real model
loads/unloads, it does not mock anything.

Run with the repo's venv:  .venv\\Scripts\\python.exe -m pytest tests/integration/
"""
import urllib.error
import urllib.request

import pytest

from amsha.llm_factory.adapters.lmstudio_lifecycle_client import LMStudioLifecycleClient
from amsha.llm_factory.domain.model.lmstudio_lifecycle_config import LMStudioLifecycleConfig

BASE_URL = "http://localhost:1234/v1"


def _lmstudio_available() -> bool:
    try:
        with urllib.request.urlopen("http://localhost:1234/api/v1/models", timeout=2) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def _smallest_llm_key(client: LMStudioLifecycleClient) -> str:
    models = client.list_models()
    llms = [m for m in models if m.get("type") == "llm"]
    if not llms:
        pytest.skip("LM Studio has no LLM models downloaded to test against")
    return min(llms, key=lambda m: m.get("size_bytes", float("inf")))["key"]


pytestmark = pytest.mark.skipif(not _lmstudio_available(), reason="LM Studio not reachable at localhost:1234")


def test_load_reuse_reload_unload_live():
    client = LMStudioLifecycleClient(BASE_URL)
    model_id = _smallest_llm_key(client)

    # start clean
    for key, instance in client.all_loaded_instances():
        client.unload(instance["id"])

    # not loaded -> loads with requested context
    cfg = LMStudioLifecycleConfig(enabled=True, model_id=model_id, context_length=4096)
    client.ensure_loaded(cfg)
    loaded = client.all_loaded_instances()
    assert loaded and loaded[0][0] == model_id
    assert loaded[0][1]["config"]["context_length"] == 4096

    # already loaded, same context -> reused, no reload (instance id unchanged)
    instance_id_before = loaded[0][1]["id"]
    client.ensure_loaded(cfg)
    loaded_after = client.all_loaded_instances()
    assert loaded_after[0][1]["id"] == instance_id_before

    # different context -> unload + reload
    cfg2 = LMStudioLifecycleConfig(enabled=True, model_id=model_id, context_length=8192)
    client.ensure_loaded(cfg2)
    loaded = client.all_loaded_instances()
    assert loaded[0][1]["config"]["context_length"] == 8192

    # cleanup
    client.unload(loaded[0][1]["id"])
    assert client.all_loaded_instances() == []


def test_disabled_lifecycle_makes_no_calls_live():
    client = LMStudioLifecycleClient(BASE_URL)
    before = client.all_loaded_instances()
    cfg = LMStudioLifecycleConfig(enabled=False, model_id="whatever")
    client.ensure_loaded(cfg)
    assert client.all_loaded_instances() == before
