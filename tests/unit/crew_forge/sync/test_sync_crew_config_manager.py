import unittest
import json
import os
import tempfile
from unittest.mock import MagicMock, patch, mock_open
from amsha.crew_forge.sync.manager.sync_crew_config_manager import SyncCrewConfigManager
from amsha.crew_forge.domain.models.crew_config_data import CrewConfigResponse

class TestSyncCrewConfigManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.app_config_path = os.path.join(self.test_dir, "app.yaml")
        self.job_config_path = os.path.join(self.test_dir, "job.yaml")
        self.output_filepath = os.path.join(self.test_dir, "output.json")
        
        with open(self.app_config_path, 'w') as f:
            f.write("database: {url: 'sqlite://'}")
        with open(self.job_config_path, 'w') as f:
            f.write(f"output_filepath: {self.output_filepath}")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)

    @patch('amsha.crew_forge.sync.manager.sync_crew_config_manager.CrewForgeContainer')
    @patch('amsha.utils.yaml_utils.YamlUtils.yaml_safe_load')
    def test_initialization_success(self, mock_yaml, mock_container):
        mock_yaml.side_effect = [
            {"output_filepath": "out.json"}, # job config
            {"db": "config"} # app config
        ]
        mock_blueprint_service = MagicMock()
        mock_container.return_value.crew_blueprint_service.return_value = mock_blueprint_service
        mock_blueprint_service.get_all_config.return_value = []
        
        manager = SyncCrewConfigManager("app.yaml", "job.yaml")
        
        self.assertEqual(manager.output_filepath, "out.json")
        mock_blueprint_service.get_all_config.assert_called_once()

    @patch('amsha.utils.yaml_utils.YamlUtils.yaml_safe_load')
    def test_initialization_missing_output_filepath(self, mock_yaml):
        mock_yaml.return_value = {} # Empty job config
        
        with self.assertRaises(ValueError) as cm:
            SyncCrewConfigManager("app.yaml", "job.yaml")
        
        self.assertIn("output_filepath", str(cm.exception))

    def test_process_blueprint(self):
        # We need a real manager instance, but we can mock the init parts
        with patch('amsha.crew_forge.sync.manager.sync_crew_config_manager.CrewForgeContainer'), \
             patch('amsha.utils.yaml_utils.YamlUtils.yaml_safe_load', return_value={"output_filepath": "out.json"}):
            manager = SyncCrewConfigManager("app.yaml", "job.yaml")
            
        mock_config = MagicMock(spec=CrewConfigResponse)
        mock_config.name = "test_crew"
        mock_config.usecase = "test_usecase"
        mock_config.agents = {"agent1": "id1", "agent2": "id2"}
        mock_config.tasks = {"task1": "id3"}
        
        result = manager._process_blueprint(mock_config)
        
        expected = {
            "name": "test_crew",
            "usecase": "test_usecase",
            "agents": ["agent1", "agent2"],
            "tasks": ["task1"]
        }
        self.assertEqual(result, expected)

    @patch('amsha.crew_forge.sync.manager.sync_crew_config_manager.CrewForgeContainer')
    @patch('amsha.utils.yaml_utils.YamlUtils.yaml_safe_load')
    def test_sync_success(self, mock_yaml, mock_container):
        mock_yaml.side_effect = [
            {"output_filepath": self.output_filepath},
            {"db": "config"}
        ]
        
        mock_config = MagicMock(spec=CrewConfigResponse)
        mock_config.name = "test_crew"
        mock_config.usecase = "test_usecase"
        mock_config.agents = {"agent1": "id1"}
        mock_config.tasks = {"task1": "id2"}
        
        mock_blueprint_service = MagicMock()
        mock_container.return_value.crew_blueprint_service.return_value = mock_blueprint_service
        mock_blueprint_service.get_all_config.return_value = [mock_config]
        
        manager = SyncCrewConfigManager("app.yaml", "job.yaml")
        manager.sync()
        
        # Verify file was created and contains correct data
        self.assertTrue(os.path.exists(self.output_filepath))
        with open(self.output_filepath, 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["name"], "test_crew")

    @patch('amsha.crew_forge.sync.manager.sync_crew_config_manager.CrewForgeContainer')
    @patch('amsha.utils.yaml_utils.YamlUtils.yaml_safe_load', return_value={"output_filepath": "out.json"})
    def test_sync_no_blueprints(self, mock_yaml, mock_container):
        mock_blueprint_service = MagicMock()
        mock_container.return_value.crew_blueprint_service.return_value = mock_blueprint_service
        mock_blueprint_service.get_all_config.return_value = []
        
        manager = SyncCrewConfigManager("app.yaml", "job.yaml")
        
        with patch('builtins.open', mock_open()) as mocked_file:
            manager.sync()
            mocked_file.assert_not_called()

    @patch('amsha.crew_forge.sync.manager.sync_crew_config_manager.CrewForgeContainer')
    @patch('amsha.utils.yaml_utils.YamlUtils.yaml_safe_load')
    def test_sync_io_error(self, mock_yaml, mock_container):
        output_file = os.path.join(self.test_dir, "error_out.json")
        mock_yaml.side_effect = [
            {"output_filepath": output_file},
            {"db": "config"}
        ]
        
        mock_config = MagicMock(spec=CrewConfigResponse)
        mock_config.name = "test_crew"
        mock_config.usecase = "test_usecase"
        mock_config.agents = {"agent1": "id1"}
        mock_config.tasks = {"task1": "id2"}
        
        mock_blueprint_service = MagicMock()
        mock_container.return_value.crew_blueprint_service.return_value = mock_blueprint_service
        mock_blueprint_service.get_all_config.return_value = [mock_config]
        
        manager = SyncCrewConfigManager("app.yaml", "job.yaml")
        
        # Mock open to raise IOError
        with patch('builtins.open', side_effect=IOError("Mocked IO Error")):
            with patch('builtins.print') as mock_print:
                manager.sync()
                # Verify that error message was printed
                # The print call is: print(f"[SyncCrewConfig] ❌ Error: Failed to write to file '{self.output_filepath}'. Reason: {e}")
                found_error = False
                for call in mock_print.call_args_list:
                    args, kwargs = call
                    if args and "Error" in args[0] and "Mocked IO Error" in args[0]:
                        found_error = True
                        break
                self.assertTrue(found_error, f"Expected error message not found in prints: {mock_print.call_args_list}")

if __name__ == '__main__':
    unittest.main()
