import unittest
import os
import tempfile
import json
from unittest.mock import MagicMock, patch, Mock
from amsha.crew_forge.orchestrator.db.amsha_crew_db_application import AmshaCrewDBApplication
from amsha.crew_forge.orchestrator.db.atomic_crew_db_manager import AtomicCrewDBManager
from amsha.llm_factory.domain.model.llm_type import LLMType
from amsha.crew_forge.exceptions import CrewConfigurationException, CrewManagerException

class TestAmshaCrewDBApplication(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_paths = {
            "job": os.path.join(self.test_dir, "job.yaml"),
            "app": os.path.join(self.test_dir, "app.yaml"),
            "llm": os.path.join(self.test_dir, "llm.yaml")
        }
        
        # Create dummy config files
        with open(self.config_paths["job"], 'w') as f:
            f.write("crew_name: test_crew\nusecase: test_usecase\ncrews: {test_crew: {input: {topic: AI}, steps: []}}")
        with open(self.config_paths["app"], 'w') as f:
            f.write("output_dir_path: output")
        with open(self.config_paths["llm"], 'w') as f:
            f.write("llm: {model: gpt-4}")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)

    @patch('amsha.crew_forge.orchestrator.db.amsha_crew_db_application.LLMContainer')
    @patch('amsha.crew_forge.orchestrator.db.amsha_crew_db_application.AtomicCrewDBManager')
    @patch('amsha.crew_forge.orchestrator.db.amsha_crew_db_application.DbCrewOrchestrator')
    def test_initialization(self, mock_orchestrator, mock_manager, mock_container):
        # Setup mock container and builder
        mock_builder = MagicMock()
        mock_container.return_value.llm_builder.return_value = mock_builder
        mock_llm = MagicMock()
        mock_llm.provider.model_name = "test-model"
        mock_builder.build_creative.return_value = mock_llm
        
        app = AmshaCrewDBApplication(self.config_paths, LLMType.CREATIVE)
        
        self.assertEqual(app.model_name, "test-model")
        mock_manager.assert_called_once()
        mock_orchestrator.assert_called_once()
    @patch('amsha.crew_forge.orchestrator.db.amsha_crew_db_application.LLMContainer')
    @patch('amsha.crew_forge.orchestrator.db.amsha_crew_db_application.AtomicCrewDBManager')
    @patch('amsha.crew_forge.orchestrator.db.amsha_crew_db_application.DbCrewOrchestrator')
    def test_initialization_evaluation(self, mock_orchestrator, mock_manager, mock_container):
        # Setup mock container and builder
        mock_builder = MagicMock()
        mock_container.return_value.llm_builder.return_value = mock_builder
        mock_llm = MagicMock()
        mock_llm.provider.model_name = "eval-model"
        mock_builder.build_evaluation.return_value = mock_llm
        
        app = AmshaCrewDBApplication(self.config_paths, LLMType.EVALUATION)
        self.assertEqual(app.model_name, "eval-model")

    @patch('amsha.crew_forge.orchestrator.db.amsha_crew_db_application.LLMContainer')
    @patch('amsha.crew_forge.orchestrator.db.amsha_crew_db_application.AtomicCrewDBManager')
    def test_prepare_inputs_direct(self, mock_manager, mock_container):
        mock_builder = MagicMock()
        mock_container.return_value.llm_builder.return_value = mock_builder
        mock_llm = MagicMock()
        mock_builder.build_creative.return_value = mock_llm
        app = AmshaCrewDBApplication(self.config_paths, LLMType.CREATIVE)
        
        app.job_config = {
            "crews": {
                "test_crew": {
                    "input": {"topic": "AI direct"}
                }
            }
        }
        inputs = app._prepare_inputs_for("test_crew")
        self.assertEqual(inputs, "AI direct")

    @patch('amsha.crew_forge.orchestrator.db.amsha_crew_db_application.LLMContainer')
    @patch('amsha.crew_forge.orchestrator.db.amsha_crew_db_application.AtomicCrewDBManager')
    def test_prepare_multiple_inputs_direct(self, mock_manager, mock_container):
        mock_builder = MagicMock()
        mock_container.return_value.llm_builder.return_value = mock_builder
        mock_llm = MagicMock()
        mock_builder.build_creative.return_value = mock_llm
        app = AmshaCrewDBApplication(self.config_paths, LLMType.CREATIVE)
        
        app.job_config = {
            "crews": {
                "test_crew": {
                    "input": [{"key_name": "topic", "source": "direct", "value": "AI direct"}]
                }
            }
        }
        inputs = app._prepare_multiple_inputs_for("test_crew")
        self.assertEqual(inputs, {"topic": "AI direct"})

    @patch('amsha.crew_forge.orchestrator.db.amsha_crew_db_application.LLMContainer')
    @patch('amsha.crew_forge.orchestrator.db.amsha_crew_db_application.AtomicCrewDBManager')
    def test_prepare_inputs_file(self, mock_manager, mock_container):
        # Mock LLM init
        mock_builder = MagicMock()
        mock_container.return_value.llm_builder.return_value = mock_builder
        mock_llm = MagicMock()
        mock_builder.build_creative.return_value = mock_llm
        
        app = AmshaCrewDBApplication(self.config_paths, LLMType.CREATIVE)
        
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

    @patch('amsha.crew_forge.orchestrator.db.amsha_crew_db_application.LLMContainer')
    @patch('amsha.crew_forge.orchestrator.db.amsha_crew_db_application.AtomicCrewDBManager')
    def test_prepare_multiple_inputs_file(self, mock_manager, mock_container):
        # Mock LLM init
        mock_builder = MagicMock()
        mock_container.return_value.llm_builder.return_value = mock_builder
        mock_llm = MagicMock()
        mock_builder.build_creative.return_value = mock_llm
        
        app = AmshaCrewDBApplication(self.config_paths, LLMType.CREATIVE)
        
        # Create a temp file to load from
        data_file = os.path.join(self.test_dir, "data.json")
        with open(data_file, 'w') as f:
            json.dump({"topic": "AI from file"}, f)
            
        app.job_config = {
            "crews": {
                "test_crew": {
                    "input": [
                        {"key_name": "topic", "source": "file", "path": data_file, "format": "json"}
                    ]
                }
            }
        }
        
        inputs = app._prepare_multiple_inputs_for("test_crew")
        self.assertEqual(inputs, {"topic": {"topic": "AI from file"}})

    @patch('amsha.crew_forge.orchestrator.db.amsha_crew_db_application.LLMContainer')
    @patch('amsha.crew_forge.orchestrator.db.amsha_crew_db_application.AtomicCrewDBManager')
    @patch('amsha.crew_forge.orchestrator.db.amsha_crew_db_application.JsonCleanerUtils')
    def test_clean_json(self, mock_cleaner, mock_manager, mock_container):
        mock_builder = MagicMock()
        mock_container.return_value.llm_builder.return_value = mock_builder
        mock_llm = MagicMock()
        mock_builder.build_creative.return_value = mock_llm
        app = AmshaCrewDBApplication(self.config_paths, LLMType.CREATIVE)
        
        mock_cleaner.return_value.process_file.return_value = True
        self.assertTrue(app.clean_json("test.json"))
        
        mock_cleaner.return_value.process_file.return_value = False
        self.assertFalse(app.clean_json("test.json"))

class TestAtomicCrewDBManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.app_config_path = os.path.join(self.test_dir, "app.yaml")
        with open(self.app_config_path, 'w') as f:
            f.write("mongo:\n  uri: mongodb://localhost:27017\n  db_name: test_db\noutput_dir_path: output")
        
        self.job_config = {
            "crew_name": "test_crew",
            "usecase": "test_usecase",
            "crews": {
                "test_crew": {
                    "steps": [
                        {"agent_key": "Researcher", "task_key": "Research"}
                    ]
                }
            }
        }

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)

    @patch('amsha.crew_forge.orchestrator.db.atomic_crew_db_manager.CrewForgeContainer')
    def test_initialization_success(self, mock_container):
        mock_blueprint_service = MagicMock()
        mock_container.return_value.crew_blueprint_service.return_value = mock_blueprint_service
        mock_blueprint_service.get_config.return_value = MagicMock()
        
        manager = AtomicCrewDBManager(
            llm=MagicMock(),
            app_config_path=self.app_config_path,
            job_config=self.job_config,
            model_name="gpt-4"
        )
        self.assertEqual(manager.model_name, "gpt-4")

    @patch('amsha.crew_forge.orchestrator.db.atomic_crew_db_manager.CrewForgeContainer')
    def test_initialization_missing_keys(self, mock_container):
        # Missing crew_name
        with self.assertRaises(CrewConfigurationException):
            AtomicCrewDBManager(MagicMock(), self.app_config_path, {"usecase": "u"}, "gpt-4")
        # Missing usecase
        with self.assertRaises(CrewConfigurationException):
            AtomicCrewDBManager(MagicMock(), self.app_config_path, {"crew_name": "c"}, "gpt-4")

    @patch('amsha.crew_forge.orchestrator.db.atomic_crew_db_manager.CrewForgeContainer')
    def test_build_atomic_crew_success(self, mock_container):
        from crewai import LLM
        mock_llm = MagicMock(spec=LLM)
        
        mock_blueprint_service = MagicMock()
        mock_container.return_value.crew_blueprint_service.return_value = mock_blueprint_service
        
        mock_blueprint = MagicMock()
        mock_blueprint.tasks = {"Research": "task-id-1"}
        mock_blueprint.agents = {"Researcher": "agent-id-1"}
        mock_blueprint_service.get_config.return_value = mock_blueprint
        
        mock_builder = MagicMock()
        mock_container.return_value.atomic_db_builder.return_value = mock_builder
        mock_builder.get_last_agent.return_value = MagicMock()
        mock_builder.build.return_value = "MockCrew"
        
        manager = AtomicCrewDBManager(
            llm=mock_llm,
            app_config_path=self.app_config_path,
            job_config=self.job_config,
            model_name="gpt-4"
        )
        
        crew = manager.build_atomic_crew("test_crew", "suffix")
        self.assertEqual(crew, "MockCrew")
        mock_container.return_value.atomic_db_builder.assert_called_once()
        mock_builder.add_task.assert_called_once_with(
            task_id="task-id-1", 
            agent=mock_builder.get_last_agent(), 
            output_filename="gpt-4_Research_suffix"
        )

    @patch('amsha.crew_forge.orchestrator.db.atomic_crew_db_manager.CrewForgeContainer')
    def test_build_atomic_crew_missing_keys(self, mock_container):
        from crewai import LLM
        mock_llm = MagicMock(spec=LLM)
        mock_blueprint_service = MagicMock()
        mock_container.return_value.crew_blueprint_service.return_value = mock_blueprint_service
        mock_blueprint_service.get_config.return_value = MagicMock()
        
        manager = AtomicCrewDBManager(mock_llm, self.app_config_path, self.job_config, "gpt-4")
        
        # Missing task_key
        self.job_config["crews"]["test_crew"]["steps"] = [{"agent_key": "a"}]
        with self.assertRaises(CrewConfigurationException):
            manager.build_atomic_crew("test_crew")
            
        # Missing agent_key
        self.job_config["crews"]["test_crew"]["steps"] = [{"task_key": "t"}]
        with self.assertRaises(CrewConfigurationException):
            manager.build_atomic_crew("test_crew")

    @patch('amsha.crew_forge.orchestrator.db.atomic_crew_db_manager.CrewForgeContainer')
    def test_build_atomic_crew_blueprint_missing(self, mock_container):
        from crewai import LLM
        mock_llm = MagicMock(spec=LLM)
        mock_blueprint_service = MagicMock()
        mock_container.return_value.crew_blueprint_service.return_value = mock_blueprint_service
        
        mock_blueprint = MagicMock()
        mock_blueprint.tasks = {}
        mock_blueprint.agents = {}
        mock_blueprint_service.get_config.return_value = mock_blueprint
        
        manager = AtomicCrewDBManager(mock_llm, self.app_config_path, self.job_config, "gpt-4")
        
        with self.assertRaises(CrewConfigurationException):
            manager.build_atomic_crew("test_crew")

    @patch('amsha.crew_forge.orchestrator.db.atomic_crew_db_manager.CrewForgeContainer')
    def test_build_atomic_crew_with_knowledge(self, mock_container):
        from crewai import LLM
        mock_llm = MagicMock(spec=LLM)
        
        mock_blueprint_service = MagicMock()
        mock_container.return_value.crew_blueprint_service.return_value = mock_blueprint_service
        mock_blueprint = MagicMock()
        mock_blueprint.tasks = {"Research": "t1"}
        mock_blueprint.agents = {"Researcher": "a1"}
        mock_blueprint_service.get_config.return_value = mock_blueprint
        
        mock_builder = MagicMock()
        mock_container.return_value.atomic_db_builder.return_value = mock_builder
        mock_builder.get_last_agent.return_value = MagicMock()
        mock_builder.build.return_value = "MockCrew"
        
        self.job_config["crews"]["test_crew"]["knowledge_sources"] = ["crew.pdf"]
        self.job_config["crews"]["test_crew"]["steps"][0]["knowledge_sources"] = ["agent.pdf"]
        
        manager = AtomicCrewDBManager(mock_llm, self.app_config_path, self.job_config, "gpt-4")
        
        with patch('amsha.crew_forge.knowledge.amsha_crew_docling_source.AmshaCrewDoclingSource') as mock_source:
            crew = manager.build_atomic_crew("test_crew")
            self.assertEqual(crew, "MockCrew")
            self.assertEqual(mock_source.call_count, 2)

    @patch('amsha.crew_forge.orchestrator.db.atomic_crew_db_manager.CrewForgeContainer')
    def test_build_atomic_crew_unexpected_failure(self, mock_container):
        from crewai import LLM
        mock_llm = MagicMock(spec=LLM)
        mock_blueprint_service = MagicMock()
        mock_container.return_value.crew_blueprint_service.return_value = mock_blueprint_service
        mock_blueprint_service.get_config.return_value = MagicMock()
        
        manager = AtomicCrewDBManager(mock_llm, self.app_config_path, self.job_config, "gpt-4")
        mock_container.return_value.atomic_db_builder.side_effect = Exception("Failed")
        
        with self.assertRaises(CrewManagerException):
            manager.build_atomic_crew("test_crew")

    @patch('amsha.crew_forge.orchestrator.db.atomic_crew_db_manager.CrewForgeContainer')
    def test_build_atomic_crew_failure(self, mock_container):
        manager = AtomicCrewDBManager(
            llm=MagicMock(),
            app_config_path=self.app_config_path,
            job_config=self.job_config,
            model_name="gpt-4"
        )
        
        # Crew not in job_config
        with self.assertRaises(CrewConfigurationException):
            manager.build_atomic_crew("missing_crew")

    @patch('amsha.crew_forge.orchestrator.db.atomic_crew_db_manager.CrewForgeContainer')
    def test_get_last_output_file(self, mock_container):
        from crewai import LLM
        mock_llm = MagicMock(spec=LLM)
        mock_blueprint_service = MagicMock()
        mock_container.return_value.crew_blueprint_service.return_value = mock_blueprint_service
        mock_blueprint_service.get_config.return_value = MagicMock()
        
        manager = AtomicCrewDBManager(mock_llm, self.app_config_path, self.job_config, "gpt-4")
        manager._output_file = "last.json"
        self.assertEqual(manager.output_file, "last.json")

if __name__ == '__main__':
    unittest.main()
