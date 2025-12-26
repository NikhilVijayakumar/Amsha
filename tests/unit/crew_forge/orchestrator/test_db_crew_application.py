"""
Unit tests for DBCrewApplication and DbCrewOrchestrator.
"""
import unittest
import os
import tempfile
from unittest.mock import MagicMock, patch
from amsha.crew_forge.orchestrator.db.db_crew_application import DbCrewApplication
from amsha.crew_forge.orchestrator.db.db_crew_orchestrator import DbCrewOrchestrator
from amsha.crew_forge.protocols.crew_manager import CrewManager
from amsha.execution_runtime.domain.execution_mode import ExecutionMode
from amsha.crew_forge.exceptions import CrewConfigurationException
from amsha.llm_factory.domain.model.llm_type import LLMType

class TestDbCrewApplication(unittest.TestCase):
    """Test cases for DbCrewApplication."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_paths = {
            "job": os.path.join(self.test_dir, "job.yaml"),
            "app": os.path.join(self.test_dir, "app.yaml"),
            "llm": os.path.join(self.test_dir, "llm.yaml")
        }
        with open(self.config_paths["job"], 'w') as f:
            f.write("crew_name: test_crew\nusecase: test_usecase\ncrews: {test_crew: {input: {topic: AI}}}")
        with open(self.config_paths["app"], 'w') as f:
            f.write("output_dir_path: output")
        with open(self.config_paths["llm"], 'w') as f:
            f.write("llm: {model: gpt-4}")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)

    @patch('amsha.crew_forge.orchestrator.db.db_crew_application.SharedLLMInitializationService')
    @patch('amsha.crew_forge.orchestrator.db.db_crew_application.AtomicCrewDBManager')
    @patch('amsha.crew_forge.orchestrator.db.db_crew_application.DbCrewOrchestrator')
    def test_run(self, mock_orchestrator, mock_manager, mock_llm_service):
        mock_llm_service.initialize_llm.return_value = (MagicMock(), "gpt-4")
        app = DbCrewApplication(self.config_paths, LLMType.CREATIVE)
        
        # Test run
        mock_orchestrator.return_value.run_crew.return_value = "Result"
        res = app.run_crew("test_crew", {"topic": "AI"})
        self.assertEqual(res, "Result")
        mock_orchestrator.return_value.run_crew.assert_called_with(
            "test_crew",
            {"topic": "AI"},
            mode=ExecutionMode.INTERACTIVE
        )

    @patch('amsha.crew_forge.orchestrator.db.db_crew_application.SharedLLMInitializationService')
    @patch('amsha.crew_forge.orchestrator.db.db_crew_application.AtomicCrewDBManager')
    @patch('amsha.crew_forge.orchestrator.db.db_crew_application.DbCrewOrchestrator')
    def test_run_background(self, mock_orchestrator, mock_manager, mock_llm_service):
        mock_llm_service.initialize_llm.return_value = (MagicMock(), "gpt-4")
        app = DbCrewApplication(self.config_paths, LLMType.CREATIVE)
        
        # Test run_background
        mock_orchestrator.return_value.run_crew.return_value = "Handle"
        res = app.run_crew("test_crew", {"topic": "AI"}, mode=ExecutionMode.BACKGROUND)
        self.assertEqual(res, "Handle")
        mock_orchestrator.return_value.run_crew.assert_called_with(
            "test_crew",
            {"topic": "AI"},
            mode=ExecutionMode.BACKGROUND
        )

    @patch('amsha.crew_forge.orchestrator.db.db_crew_application.SharedLLMInitializationService')
    @patch('amsha.crew_forge.orchestrator.db.db_crew_application.AtomicCrewDBManager')
    def test_prepare_inputs(self, mock_manager, mock_llm_service):
        mock_llm_service.initialize_llm.return_value = (MagicMock(), "gpt-4")
        app = DbCrewApplication(self.config_paths, LLMType.CREATIVE)
        
        # Mock input service
        app._input_service = MagicMock()
        app._input_service.prepare_multiple_inputs_for.return_value = {"topic": "AI"}
        
        inputs = app.prepare_inputs_for("test_crew")
        self.assertEqual(inputs, {"topic": "AI"})

    @patch('amsha.crew_forge.orchestrator.db.db_crew_application.SharedLLMInitializationService')
    @patch('amsha.crew_forge.orchestrator.db.db_crew_application.AtomicCrewDBManager')
    def test_prepare_inputs_fallback(self, mock_manager, mock_llm_service):
        mock_llm_service.initialize_llm.return_value = (MagicMock(), "gpt-4")
        app = DbCrewApplication(self.config_paths, LLMType.CREATIVE)
        
        # Mock multiple inputs to fail
        app._input_service = MagicMock()
        app._input_service.prepare_multiple_inputs_for.side_effect = KeyError("missing")
        app._input_service.prepare_inputs_for.return_value = {"topic": "fallback"}
        
        result = app.prepare_inputs_for("test_crew")
        self.assertEqual(result, {"topic": "fallback"})
        app._input_service.prepare_inputs_for.assert_called_once()

    @patch('amsha.crew_forge.orchestrator.db.db_crew_application.SharedLLMInitializationService')
    @patch('amsha.crew_forge.orchestrator.db.db_crew_application.AtomicCrewDBManager')
    @patch('amsha.crew_forge.orchestrator.db.db_crew_application.DbCrewOrchestrator')
    def test_run_crew_background(self, mock_orchestrator, mock_manager, mock_llm_service):
        mock_llm_service.initialize_llm.return_value = (MagicMock(), "gpt-4")
        app = DbCrewApplication(self.config_paths, LLMType.CREATIVE)
        
        mock_orchestrator.return_value.run_crew.return_value = MagicMock()
        result = app.run_crew("test_crew", {"topic": "AI"}, mode=ExecutionMode.BACKGROUND)
        self.assertEqual(result, mock_orchestrator.return_value.run_crew.return_value)
        mock_orchestrator.return_value.run_crew.assert_called_once_with("test_crew", {"topic": "AI"}, mode=ExecutionMode.BACKGROUND)

    @patch('amsha.crew_forge.orchestrator.db.db_crew_application.SharedLLMInitializationService')
    @patch('amsha.crew_forge.orchestrator.db.db_crew_application.AtomicCrewDBManager')
    def test_prepare_inputs_fallback(self, mock_manager, mock_llm_service):
        mock_llm_service.initialize_llm.return_value = (MagicMock(), "gpt-4")
        app = DbCrewApplication(self.config_paths, LLMType.CREATIVE)
        
        # Mock input service
        app._input_service = MagicMock()
        app._input_service.prepare_multiple_inputs_for.side_effect = KeyError("missing")
        app._input_service.prepare_inputs_for.return_value = {"topic": "fallback"}
        
        result = app.prepare_inputs_for("test_crew")
        self.assertEqual(result, {"topic": "fallback"})
        app._input_service.prepare_inputs_for.assert_called_once()

    @patch('amsha.crew_forge.orchestrator.db.db_crew_application.SharedLLMInitializationService')
    @patch('amsha.crew_forge.orchestrator.db.db_crew_application.AtomicCrewDBManager')
    def test_backward_compatibility(self, mock_manager, mock_llm_service):
        mock_llm_service.initialize_llm.return_value = (MagicMock(), "gpt-4")
        app = DbCrewApplication(self.config_paths, LLMType.CREATIVE)
        
        app._input_service = MagicMock()
        app._input_service.prepare_inputs_for.return_value = {"k": "v"}
        self.assertEqual(app._prepare_inputs_for("c"), {"k": "v"})
        
        app._input_service.prepare_multiple_inputs_for.return_value = {"k2": "v2"}
        self.assertEqual(app._prepare_multiple_inputs_for("c"), {"k2": "v2"})
        
        with patch('amsha.crew_forge.orchestrator.db.db_crew_application.SharedJSONFileService') as mock_service:
            mock_service.return_value.clean_json.return_value = True
            success, path = DbCrewApplication.clean_json_metrics("test.json")
            self.assertTrue(success)
            self.assertEqual(path, "test.json")

    def test_init_missing_keys(self):
        with self.assertRaises(CrewConfigurationException):
            DbCrewApplication({"job": "j"}, LLMType.CREATIVE)

    def test_init_unexpected_failure(self):
        with patch('amsha.crew_forge.orchestrator.db.db_crew_application.YamlUtils.yaml_safe_load', side_effect=Exception("Unexpected")):
            with self.assertRaises(CrewConfigurationException):
                DbCrewApplication(self.config_paths, LLMType.CREATIVE)

class TestDbCrewOrchestrator(unittest.TestCase):
    """Test cases for DbCrewOrchestrator."""

    @patch('amsha.crew_forge.orchestrator.db.db_crew_orchestrator.BaseCrewOrchestrator.run_crew')
    def test_orchestrator(self, mock_run):
        mock_manager = MagicMock(spec=CrewManager)
        orchestrator = DbCrewOrchestrator(mock_manager)
        
        # Test run_crew
        orchestrator.run_crew("crew", {"i": 1}, "suffix", ExecutionMode.INTERACTIVE)
        mock_run.assert_called_with("crew", {"i": 1}, "suffix", ExecutionMode.INTERACTIVE)
        
        # Test get_last_output_file
        mock_manager.output_file = "file.json"
        self.assertEqual(orchestrator.get_last_output_file(), "file.json")


if __name__ == '__main__':
    unittest.main()
