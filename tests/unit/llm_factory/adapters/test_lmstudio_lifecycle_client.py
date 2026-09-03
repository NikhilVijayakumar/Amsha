"""
Unit tests for LMStudioLifecycleClient. Real LM Studio server not required —
urllib.request.urlopen is mocked at the transport boundary.
"""
import json
import unittest
from unittest.mock import MagicMock, patch

from amsha.llm_factory.adapters.lmstudio_lifecycle_client import (
    LMStudioLifecycleClient,
    LMStudioLifecycleError,
)
from amsha.llm_factory.domain.model.lmstudio_lifecycle_config import LMStudioLifecycleConfig


def _response(payload: dict):
    cm = MagicMock()
    cm.__enter__.return_value.read.return_value = json.dumps(payload).encode("utf-8")
    return cm


class TestManagementRoot(unittest.TestCase):
    def test_strips_v1_suffix(self):
        client = LMStudioLifecycleClient("http://localhost:1234/v1")
        self.assertEqual(client._api_root, "http://localhost:1234/api/v1")

    def test_no_v1_suffix(self):
        client = LMStudioLifecycleClient("http://localhost:1234")
        self.assertEqual(client._api_root, "http://localhost:1234/api/v1")


class TestListAndFind(unittest.TestCase):
    @patch("amsha.llm_factory.adapters.lmstudio_lifecycle_client.urllib.request.urlopen")
    def test_all_loaded_instances(self, mock_urlopen):
        mock_urlopen.return_value = _response({
            "models": [
                {"key": "model-a", "loaded_instances": [{"id": "inst-a", "config": {"context_length": 4096}}]},
                {"key": "model-b", "loaded_instances": []},
            ]
        })
        client = LMStudioLifecycleClient("http://localhost:1234/v1")
        result = client.all_loaded_instances()
        self.assertEqual(result, [("model-a", {"id": "inst-a", "config": {"context_length": 4096}})])

    @patch("amsha.llm_factory.adapters.lmstudio_lifecycle_client.urllib.request.urlopen")
    def test_unreachable_raises(self, mock_urlopen):
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("connection refused")
        client = LMStudioLifecycleClient("http://localhost:1234/v1")
        with self.assertRaises(LMStudioLifecycleError):
            client.list_models()


class TestLoad(unittest.TestCase):
    @patch("amsha.llm_factory.adapters.lmstudio_lifecycle_client.urllib.request.urlopen")
    def test_load_context_length_mismatch_raises(self, mock_urlopen):
        mock_urlopen.return_value = _response({"load_config": {"context_length": 4096}})
        client = LMStudioLifecycleClient("http://localhost:1234/v1")
        with self.assertRaises(LMStudioLifecycleError):
            client.load("model-a", context_length=16384)

    @patch("amsha.llm_factory.adapters.lmstudio_lifecycle_client.urllib.request.urlopen")
    def test_load_context_length_match_ok(self, mock_urlopen):
        mock_urlopen.return_value = _response({"load_config": {"context_length": 16384}})
        client = LMStudioLifecycleClient("http://localhost:1234/v1")
        result = client.load("model-a", context_length=16384)
        self.assertEqual(result["load_config"]["context_length"], 16384)


class TestLoadRetry(unittest.TestCase):
    @patch("amsha.llm_factory.adapters.lmstudio_lifecycle_client.time.sleep")
    @patch("amsha.llm_factory.adapters.lmstudio_lifecycle_client.urllib.request.urlopen")
    def test_retries_then_succeeds(self, mock_urlopen, mock_sleep):
        import urllib.error
        ok = _response({"load_config": {"context_length": 4096}})
        mock_urlopen.side_effect = [urllib.error.URLError("busy"), urllib.error.URLError("busy"), ok]
        client = LMStudioLifecycleClient("http://localhost:1234/v1")
        result = client.load("model-a", context_length=4096, max_retries=2, retry_delay=5)
        self.assertEqual(result["load_config"]["context_length"], 4096)
        self.assertEqual(mock_urlopen.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_called_with(5)

    @patch("amsha.llm_factory.adapters.lmstudio_lifecycle_client.time.sleep")
    @patch("amsha.llm_factory.adapters.lmstudio_lifecycle_client.urllib.request.urlopen")
    def test_retries_exhausted_raises(self, mock_urlopen, mock_sleep):
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("down")
        client = LMStudioLifecycleClient("http://localhost:1234/v1")
        with self.assertRaises(LMStudioLifecycleError):
            client.load("model-a", max_retries=2, retry_delay=1)
        self.assertEqual(mock_urlopen.call_count, 3)

    @patch("amsha.llm_factory.adapters.lmstudio_lifecycle_client.urllib.request.urlopen")
    def test_default_no_retry(self, mock_urlopen):
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("down")
        client = LMStudioLifecycleClient("http://localhost:1234/v1")
        with self.assertRaises(LMStudioLifecycleError):
            client.load("model-a")
        self.assertEqual(mock_urlopen.call_count, 1)


class TestEnsureLoaded(unittest.TestCase):
    def _client_with_calls(self):
        client = LMStudioLifecycleClient("http://localhost:1234/v1")
        client.all_loaded_instances = MagicMock()
        client.unload = MagicMock()
        client.load = MagicMock()
        return client

    def test_disabled_is_noop(self):
        client = self._client_with_calls()
        config = LMStudioLifecycleConfig(enabled=False, model_id="model-a")
        client.ensure_loaded(config)
        client.all_loaded_instances.assert_not_called()

    def test_not_loaded_loads_it(self):
        client = self._client_with_calls()
        client.all_loaded_instances.return_value = []
        config = LMStudioLifecycleConfig(enabled=True, model_id="model-a", context_length=8192)
        client.ensure_loaded(config)
        client.load.assert_called_once_with("model-a", 8192, 0, 2.0)
        client.unload.assert_not_called()

    def test_already_loaded_matching_context_reused(self):
        client = self._client_with_calls()
        client.all_loaded_instances.return_value = [
            ("model-a", {"id": "inst-a", "config": {"context_length": 8192}})
        ]
        config = LMStudioLifecycleConfig(enabled=True, model_id="model-a", context_length=8192)
        client.ensure_loaded(config)
        client.load.assert_not_called()
        client.unload.assert_not_called()

    def test_already_loaded_wrong_context_reloads(self):
        client = self._client_with_calls()
        client.all_loaded_instances.return_value = [
            ("model-a", {"id": "inst-a", "config": {"context_length": 4096}})
        ]
        config = LMStudioLifecycleConfig(enabled=True, model_id="model-a", context_length=16384)
        client.ensure_loaded(config)
        client.unload.assert_called_once_with("inst-a")
        client.load.assert_called_once_with("model-a", 16384, 0, 2.0)

    def test_unloads_other_models_by_default(self):
        client = self._client_with_calls()
        client.all_loaded_instances.return_value = [
            ("model-b", {"id": "inst-b", "config": {"context_length": 4096}})
        ]
        config = LMStudioLifecycleConfig(enabled=True, model_id="model-a")
        client.ensure_loaded(config)
        client.unload.assert_called_once_with("inst-b")
        client.load.assert_called_once_with("model-a", None, 0, 2.0)

    def test_unload_other_models_false_leaves_it(self):
        client = self._client_with_calls()
        client.all_loaded_instances.return_value = [
            ("model-b", {"id": "inst-b", "config": {"context_length": 4096}})
        ]
        config = LMStudioLifecycleConfig(enabled=True, model_id="model-a", unload_other_models=False)
        client.ensure_loaded(config)
        client.unload.assert_not_called()
        client.load.assert_called_once_with("model-a", None, 0, 2.0)


if __name__ == "__main__":
    unittest.main()
