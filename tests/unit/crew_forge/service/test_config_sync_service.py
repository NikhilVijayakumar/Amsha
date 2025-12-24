"""
Unit tests for ConfigSyncService.
"""
import unittest
from unittest.mock import MagicMock, patch
from amsha.crew_forge.service.config_sync_service import ConfigSyncService
from amsha.crew_forge.domain.models.sync_config import SyncConfigData


class TestConfigSyncService(unittest.TestCase):
    """Test cases for ConfigSyncService."""

    def test_synchronize(self):
        """Test synchronize."""
        mock_data = MagicMock(spec=SyncConfigData)
        mock_data.agent_repo = MagicMock()
        mock_data.task_repo = MagicMock()
        mock_data.crew_repo = MagicMock()
        mock_data.domain_root_path = "/root"
        
        service = ConfigSyncService(mock_data)
        
        with patch('amsha.crew_forge.service.config_sync_service.DatabaseSeeder') as mock_seeder_class:
            mock_seeder = mock_seeder_class.return_value
            service.synchronize()
            
            mock_seeder_class.assert_called_with(
                agent_repo=mock_data.agent_repo,
                task_repo=mock_data.task_repo,
                crew_repo=mock_data.crew_repo
            )
            mock_seeder.synchronize.assert_called_with(root_path="/root")


if __name__ == '__main__':
    unittest.main()
