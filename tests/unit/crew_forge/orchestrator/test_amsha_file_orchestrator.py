import unittest
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
from amsha.crew_forge.orchestrator.file.amsha_crew_file_application import AmshaCrewFileApplication
from amsha.crew_forge.orchestrator.file.atomic_crew_file_manager import AtomicCrewFileManager
from amsha.llm_factory.domain.model.llm_type import LLMType
from amsha.crew_forge.exceptions import CrewConfigurationException, CrewManagerException

class TestAmshaCrewFileApplication(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_paths = {
            "job": os.path.join(self.test_dir, "job.yaml"),
            "app": os.path.join(self.test_dir, "app.yaml"),
            "llm": os.path.join(self.test_dir, "llm.yaml")
        }
        
        # Create dummy config files
        with open(self.config_paths["job"], 'w') as f:
            f.write("crews: {test_crew: {input: {topic: AI}, steps: []}}")
        with open(self.config_paths["app"], 'w') as f:
            f.write("output_dir_path: output")
        with open(self.config_paths["llm"], 'w') as f:
            f.write("llm: {model: gpt-4}")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)

    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.LLMContainer')
    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.AtomicCrewFileManager')
    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.FileCrewOrchestrator')
    def test_initialization(self, mock_orchestrator, mock_manager, mock_container):
        # Setup mock container and builder
        mock_builder = MagicMock()
        mock_container.return_value.llm_builder.return_value = mock_builder
        mock_llm = MagicMock()
        mock_llm.provider.model_name = "test-model"
        mock_builder.build_creative.return_value = mock_llm
        
        app = AmshaCrewFileApplication(self.config_paths, LLMType.CREATIVE)
        
        self.assertEqual(app.model_name, "test-model")
        mock_manager.assert_called_once()
        mock_orchestrator.assert_called_once()

    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.LLMContainer')
    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.AtomicCrewFileManager')
    def test_prepare_inputs_direct(self, mock_manager, mock_container):
        # Mock LLM init
        mock_builder = MagicMock()
        mock_container.return_value.llm_builder.return_value = mock_builder
        mock_llm = MagicMock()
        mock_builder.build_creative.return_value = mock_llm
        
        app = AmshaCrewFileApplication(self.config_paths, LLMType.CREATIVE)
        app.job_config = {
            "crews": {
                "test_crew": {
                    "input": {"topic": "AI"}
                }
            }
        }
        
        inputs = app._prepare_inputs_for("test_crew")
        # The implementation returns the last value directly for single input format
        self.assertEqual(inputs, "AI")

    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.LLMContainer')
    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.AtomicCrewFileManager')
    def test_prepare_multiple_inputs_direct(self, mock_manager, mock_container):
        # Mock LLM init
        mock_builder = MagicMock()
        mock_container.return_value.llm_builder.return_value = mock_builder
        mock_llm = MagicMock()
        mock_builder.build_creative.return_value = mock_llm
        
        app = AmshaCrewFileApplication(self.config_paths, LLMType.CREATIVE)
        app.job_config = {
            "crews": {
                "test_crew": {
                    "input": [
                        {"key_name": "topic", "source": "direct", "value": "AI"},
                        {"key_name": "mode", "source": "direct", "value": "fast"}
                    ]
                }
            }
        }
        
        inputs = app._prepare_multiple_inputs_for("test_crew")
        self.assertEqual(inputs, {"topic": "AI", "mode": "fast"})

    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.LLMContainer')
    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.AtomicCrewFileManager')
    def test_prepare_inputs_file(self, mock_manager, mock_container):
        # Mock LLM init
        mock_builder = MagicMock()
        mock_container.return_value.llm_builder.return_value = mock_builder
        mock_llm = MagicMock()
        mock_builder.build_creative.return_value = mock_llm
        
        app = AmshaCrewFileApplication(self.config_paths, LLMType.CREATIVE)
        
        # Create a temp file to load from
        data_file = os.path.join(self.test_dir, "data.json")
        with open(data_file, 'w') as f:
            json.dump({"topic": "AI from file"}, f)
            
        app.job_config = {
            "crews": {
                "test_crew": {
                    "input": {
                        "topic": {"source": "file", "path": data_file, "format": "json"}
                    }
                }
            }
        }
        
        inputs = app._prepare_inputs_for("test_crew")
        self.assertEqual(inputs, {"topic": "AI from file"})

    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.LLMContainer')
    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.AtomicCrewFileManager')
    def test_prepare_multiple_inputs_file(self, mock_manager, mock_container):
        # Mock LLM init
        mock_builder = MagicMock()
        mock_container.return_value.llm_builder.return_value = mock_builder
        mock_llm = MagicMock()
        mock_builder.build_creative.return_value = mock_llm
        
        app = AmshaCrewFileApplication(self.config_paths, LLMType.CREATIVE)
        
        # Create a temp file to load from
        data_file = os.path.join(self.test_dir, "data.txt")
        with open(data_file, 'w') as f:
            f.write("AI text from file")
            
        app.job_config = {
            "crews": {
                "test_crew": {
                    "input": [
                        {"key_name": "topic", "source": "file", "path": data_file, "format": "text"}
                    ]
                }
            }
        }
        
        inputs = app._prepare_multiple_inputs_for("test_crew")
        self.assertEqual(inputs, {"topic": "AI text from file"})

    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.LLMContainer')
    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.AtomicCrewFileManager')
    def test_execute_crew_with_retry_success(self, mock_manager, mock_container):
        # Mock LLM init
        mock_builder = MagicMock()
        mock_container.return_value.llm_builder.return_value = mock_builder
        mock_llm = MagicMock()
        mock_builder.build_creative.return_value = mock_llm
        
        app = AmshaCrewFileApplication(self.config_paths, LLMType.CREATIVE)
        app.orchestrator = MagicMock()
        app.orchestrator.run_crew.return_value = "Success"
        app.orchestrator.get_last_output_file.return_value = "out.json"
        
        result = app.execute_crew_with_retry("test_crew", {"topic": "AI"}, max_retries=2)
        
        self.assertEqual(result, "Success")
        self.assertEqual(app.orchestrator.run_crew.call_count, 1)

    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.LLMContainer')
    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.AtomicCrewFileManager')
    def test_execute_crew_with_retry_failure_then_success(self, mock_manager, mock_container):
        # Mock LLM init
        mock_builder = MagicMock()
        mock_container.return_value.llm_builder.return_value = mock_builder
        mock_llm = MagicMock()
        mock_builder.build_creative.return_value = mock_llm
        
        app = AmshaCrewFileApplication(self.config_paths, LLMType.CREATIVE)
        app.orchestrator = MagicMock()
        app.orchestrator.run_crew.return_value = "Success"
        
        # Mock validation to fail first time
        app.validate_execution = MagicMock(side_effect=[False, True])
        
        result = app.execute_crew_with_retry("test_crew", {"topic": "AI"}, max_retries=2)
        
        self.assertEqual(result, "Success")
        self.assertEqual(app.orchestrator.run_crew.call_count, 2)

    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.LLMContainer')
    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.AtomicCrewFileManager')
    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.FileCrewOrchestrator')
    def test_run_success(self, mock_orchestrator, mock_manager, mock_container):
        # Setup mock container and builder
        mock_builder = MagicMock()
        mock_container.return_value.llm_builder.return_value = mock_builder
        mock_llm = MagicMock()
        mock_llm.provider.model_name = "test-model"
        mock_builder.build_creative.return_value = mock_llm
        
        app = AmshaCrewFileApplication(self.config_paths, LLMType.CREATIVE)
        mock_orchestrator.return_value.run_crew.return_value = "Success"
        
        res = app.execute_crew_with_retry("test_crew", {"topic": "AI"})
        self.assertEqual(res, "Success")
        mock_orchestrator.return_value.run_crew.assert_called_once()

    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.LLMContainer')
    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.AtomicCrewFileManager')
    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.FileCrewOrchestrator')
    def test_run_failure_retry(self, mock_orchestrator, mock_manager, mock_container):
        mock_builder = MagicMock()
        mock_container.return_value.llm_builder.return_value = mock_builder
        mock_llm = MagicMock()
        mock_builder.build_creative.return_value = mock_llm
        
        app = AmshaCrewFileApplication(self.config_paths, LLMType.CREATIVE)
        mock_orchestrator.return_value.run_crew.return_value = "Failed"
        mock_orchestrator.return_value.get_last_execution_id.return_value = "exec-1"
        
        # Mock validation to fail
        with patch.object(AmshaCrewFileApplication, 'validate_execution', return_value=False):
            res = app.execute_crew_with_retry("test_crew", {"topic": "AI"}, max_retries=1)
            self.assertEqual(res, "Failed")
            self.assertEqual(mock_orchestrator.return_value.run_crew.call_count, 2)

    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.LLMContainer')
    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.AtomicCrewFileManager')
    def test_prepare_inputs_direct(self, mock_manager, mock_container):
        mock_builder = MagicMock()
        mock_container.return_value.llm_builder.return_value = mock_builder
        mock_llm = MagicMock()
        mock_builder.build_creative.return_value = mock_llm
        app = AmshaCrewFileApplication(self.config_paths, LLMType.CREATIVE)
        
        app.job_config = {
            "crews": {
                "test_crew": {
                    "input": {"topic": "AI direct"}
                }
            }
        }
        inputs = app._prepare_inputs_for("test_crew")
        self.assertEqual(inputs, "AI direct")

    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.LLMContainer')
    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.AtomicCrewFileManager')
    @patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.JsonCleanerUtils')
    def test_clean_json(self, mock_cleaner, mock_manager, mock_container):
        mock_builder = MagicMock()
        mock_container.return_value.llm_builder.return_value = mock_builder
        mock_llm = MagicMock()
        mock_builder.build_creative.return_value = mock_llm
        app = AmshaCrewFileApplication(self.config_paths, LLMType.CREATIVE)
        
        mock_cleaner.return_value.process_file.return_value = True
        self.assertTrue(app.clean_json("test.json"))
        
        mock_cleaner.return_value.process_file.return_value = True
        mock_cleaner.return_value.output_file_path = "clean.json"
        success, path = app.clean_json_metrics("test.json")
        self.assertTrue(success)
        self.assertEqual(path, "clean.json")

    def test_prepare_multiple_inputs_for_json(self):
        with patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.YamlUtils.yaml_safe_load'), \
             patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.LLMContainer') as mock_container, \
             patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.AtomicCrewFileManager'), \
             patch('amsha.crew_forge.orchestrator.file.amsha_crew_file_application.FileCrewOrchestrator'):
            
            mock_builder = MagicMock()
            mock_container.return_value.llm_builder.return_value = mock_builder
            mock_llm = MagicMock()
            mock_llm.provider.model_name = "test-model"
            mock_builder.build_creative.return_value = mock_llm
            
            app = AmshaCrewFileApplication(self.config_paths, LLMType.CREATIVE)
            
            data_file = os.path.join(self.test_dir, "data.json")
            with open(data_file, 'w') as f:
                json.dump({"k": "v"}, f)
                
            app.job_config = {
                "crews": {
                    "c1": {
                        "input": [
                            {"key_name": "p1", "source": "file", "path": data_file, "format": "json"}
                        ]
                    }
                }
            }
            
            inputs = app._prepare_multiple_inputs_for("c1")
            self.assertEqual(inputs, {"p1": {"k": "v"}})

class TestAtomicCrewFileManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.app_config_path = os.path.join(self.test_dir, "app.yaml")
        with open(self.app_config_path, 'w') as f:
            f.write("output_dir_path: output")
        
        self.job_config = {
            "crew_name": "test_crew",
            "crews": {
                "test_crew": {
                    "steps": [
                        {"task_file": "task1.yaml", "agent_file": "agent1.yaml"}
                    ]
                }
            }
        }

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)

    @patch('amsha.crew_forge.orchestrator.file.atomic_crew_file_manager.CrewForgeContainer')
    def test_initialization(self, mock_container):
        manager = AtomicCrewFileManager(
            llm=MagicMock(),
            app_config_path=self.app_config_path,
            job_config=self.job_config,
            model_name="gpt-4"
        )
        self.assertEqual(manager.model_name, "gpt-4")

    @patch('amsha.crew_forge.orchestrator.file.atomic_crew_file_manager.CrewForgeContainer')
    def test_build_atomic_crew_success(self, mock_container):
        from crewai import LLM
        mock_llm = MagicMock(spec=LLM)
        
        mock_builder = MagicMock()
        mock_container.return_value.atomic_yaml_builder.return_value = mock_builder
        mock_builder.get_last_agent.return_value = MagicMock()
        mock_builder.build.return_value = "MockCrew"
        
        manager = AtomicCrewFileManager(
            llm=mock_llm,
            app_config_path=self.app_config_path,
            job_config=self.job_config,
            model_name="gpt-4"
        )
        
        crew = manager.build_atomic_crew("test_crew", "suffix")
        self.assertEqual(crew, "MockCrew")
        mock_container.return_value.atomic_yaml_builder.assert_called_once()
        mock_builder.add_agent.assert_called_once_with(knowledge_sources=None)
        mock_builder.add_task.assert_called_once_with(agent=mock_builder.get_last_agent(), output_filename="gpt-4_suffix")

    @patch('amsha.crew_forge.orchestrator.file.atomic_crew_file_manager.CrewForgeContainer')
    def test_build_atomic_crew_missing_files(self, mock_container):
        from crewai import LLM
        mock_llm = MagicMock(spec=LLM)
        manager = AtomicCrewFileManager(
            llm=mock_llm,
            app_config_path=self.app_config_path,
            job_config=self.job_config,
            model_name="gpt-4"
        )
        
        # Missing task_file
        self.job_config["crews"]["test_crew"]["steps"] = [{"agent_file": "a.yaml"}]
        with self.assertRaises(CrewConfigurationException):
            manager.build_atomic_crew("test_crew")
            
        # Missing agent_file
        self.job_config["crews"]["test_crew"]["steps"] = [{"task_file": "t.yaml"}]
        with self.assertRaises(CrewConfigurationException):
            manager.build_atomic_crew("test_crew")

    @patch('amsha.crew_forge.orchestrator.file.atomic_crew_file_manager.CrewForgeContainer')
    def test_build_atomic_crew_no_steps(self, mock_container):
        self.job_config["crews"]["test_crew"]["steps"] = []
        manager = AtomicCrewFileManager(MagicMock(), self.app_config_path, self.job_config, "gpt-4")
        with self.assertRaises(CrewManagerException):
            manager.build_atomic_crew("test_crew")

    def test_get_last_output_file(self):
        # Mock builder
        manager = AtomicCrewFileManager(MagicMock(), self.app_config_path, self.job_config, "gpt-4")
        manager._output_file = "last.json"
        self.assertEqual(manager.output_file, "last.json")

    @patch('amsha.crew_forge.orchestrator.file.atomic_crew_file_manager.YamlUtils.yaml_safe_load')
    def test_init_failure(self, mock_load):
        mock_load.side_effect = Exception("Failed")
        with self.assertRaises(CrewManagerException):
            AtomicCrewFileManager(MagicMock(), self.app_config_path, self.job_config, "gpt-4")

    def test_build_atomic_crew_unexpected_failure(self):
        from crewai import LLM
        mock_llm = MagicMock(spec=LLM)
        manager = AtomicCrewFileManager(
            llm=mock_llm,
            app_config_path=self.app_config_path,
            job_config=self.job_config,
            model_name="gpt-4"
        )
        manager.crew_container.atomic_yaml_builder = MagicMock(side_effect=Exception("Unexpected"))
        with self.assertRaises(CrewManagerException):
            manager.build_atomic_crew("test_crew")

    @patch('amsha.crew_forge.orchestrator.file.atomic_crew_file_manager.CrewForgeContainer')
    def test_build_atomic_crew_with_knowledge(self, mock_container):
        from crewai import LLM
        mock_llm = MagicMock(spec=LLM)
        
        mock_builder = MagicMock()
        mock_container.return_value.atomic_yaml_builder.return_value = mock_builder
        mock_builder.get_last_agent.return_value = MagicMock()
        mock_builder.build.return_value = "MockCrew"
        
        self.job_config["crews"]["test_crew"]["knowledge_sources"] = ["doc.pdf"]
        self.job_config["crews"]["test_crew"]["steps"][0]["knowledge_sources"] = ["agent_doc.pdf"]
        
        manager = AtomicCrewFileManager(
            llm=mock_llm,
            app_config_path=self.app_config_path,
            job_config=self.job_config,
            model_name="gpt-4"
        )
        
        # Patch where it's imported (inside the method)
        with patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.AmshaCrewDoclingSource') as mock_source:
            crew = manager.build_atomic_crew("test_crew")
            self.assertEqual(crew, "MockCrew")
            self.assertEqual(mock_source.call_count, 2)

    @patch('amsha.crew_forge.orchestrator.file.atomic_crew_file_manager.CrewForgeContainer')
    def test_build_atomic_crew_not_found(self, mock_container):
        from crewai import LLM
        mock_llm = MagicMock(spec=LLM)
        manager = AtomicCrewFileManager(
            llm=mock_llm,
            app_config_path=self.app_config_path,
            job_config=self.job_config,
            model_name="gpt-4"
        )
        
        with self.assertRaises(CrewConfigurationException):
            manager.build_atomic_crew("non_existent")

class TestFileCrewOrchestrator(unittest.TestCase):
    def setUp(self):
        self.manager = MagicMock()
        self.runtime = MagicMock()
        self.state_manager = MagicMock()
        from amsha.crew_forge.orchestrator.file.file_crew_orchestrator import FileCrewOrchestrator
        self.orchestrator = FileCrewOrchestrator(
            manager=self.manager,
            runtime=self.runtime,
            state_manager=self.state_manager
        )

    def test_run_crew_with_validator_success(self):
        from amsha.execution_runtime.domain.execution_mode import ExecutionMode
        self.manager.build_atomic_crew.return_value = MagicMock()
        
        mock_handle = MagicMock()
        self.runtime.submit.return_value = mock_handle
        mock_handle.result.return_value = "Result"
        
        self.manager.output_file = "out.json"
        
        validator = MagicMock(return_value=True)
        
        result = self.orchestrator.run_crew(
            "test_crew", 
            {"topic": "AI"}, 
            mode=ExecutionMode.INTERACTIVE,
            output_validator=validator
        )
        
        self.assertEqual(result, "Result")
        validator.assert_called_once_with("out.json")

    def test_run_crew_with_validator_retry_success(self):
        from amsha.execution_runtime.domain.execution_mode import ExecutionMode
        self.manager.build_atomic_crew.return_value = MagicMock()
        
        mock_handle = MagicMock()
        mock_handle.result.return_value = "Result"
        self.runtime.submit.return_value = mock_handle
        
        self.manager.output_file = "out.json"
        
        # Fail first, succeed second
        validator = MagicMock(side_effect=[False, True])
        
        result = self.orchestrator.run_crew(
            "test_crew", 
            {"topic": "AI"}, 
            mode=ExecutionMode.INTERACTIVE,
            max_retries=1,
            output_validator=validator
        )
        
        self.assertEqual(result, "Result")
        self.assertEqual(validator.call_count, 2)
        self.assertEqual(self.runtime.submit.call_count, 2)

    def test_run_crew_background(self):
        from amsha.execution_runtime.domain.execution_mode import ExecutionMode
        self.manager.build_atomic_crew.return_value = MagicMock()
        mock_handle = MagicMock()
        self.runtime.submit.return_value = mock_handle
        
        result = self.orchestrator.run_crew(
            "test_crew", 
            {"topic": "AI"}, 
            mode=ExecutionMode.BACKGROUND
        )
        
        self.assertEqual(result, mock_handle)
        self.runtime.submit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
