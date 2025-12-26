"""
Unit tests for CrewBluePrintService.
"""
import unittest
from unittest.mock import MagicMock
from amsha.crew_forge.service.crew_blueprint_service import CrewBluePrintService
from amsha.crew_forge.repo.interfaces.i_crew_config_repository import ICrewConfigRepository


class TestCrewBluePrintService(unittest.TestCase):
    """Test cases for CrewBluePrintService."""

    def setUp(self):
        self.mock_repo = MagicMock(spec=ICrewConfigRepository)
        self.service = CrewBluePrintService(self.mock_repo)

    def test_get_config(self):
        """Test get_config."""
        self.service.get_config("name", "usecase")
        self.mock_repo.get_crew_by_name_and_usecase.assert_called_with("name", "usecase")

    def test_get_all_config(self):
        """Test get_all_config."""
        self.service.get_all_config()
        self.mock_repo.get_all_crew_configs.assert_called()


if __name__ == '__main__':
    unittest.main()
