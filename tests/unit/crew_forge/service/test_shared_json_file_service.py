"""
Unit tests for SharedJSONFileService class.
"""
import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from amsha.crew_forge.service.shared_json_file_service import SharedJSONFileService
from amsha.crew_forge.exceptions import CrewForgeException


class TestSharedJSONFileService(unittest.TestCase):
    """Test cases for SharedJSONFileService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = SharedJSONFileService()
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_initialization(self):
        """Test proper initialization of SharedJSONFileService."""
        self.assertIsNotNone(self.service)
        
    @patch('amsha.crew_forge.service.shared_json_file_service.JsonCleanerUtils')
    def test_clean_json_success(self, mock_cleaner_class):
        """Test successful JSON cleaning."""
        # Create a dummy file
        file_path = os.path.join(self.test_dir, "test.json")
        with open(file_path, 'w') as f:
            f.write("{}")
            
        mock_cleaner_instance = mock_cleaner_class.return_value
        mock_cleaner_instance.process_file.return_value = True
        mock_cleaner_instance.output_file_path = file_path
        
        result = self.service.clean_json(file_path)
        
        self.assertTrue(result)
        mock_cleaner_class.assert_called_once_with(file_path)
        mock_cleaner_instance.process_file.assert_called_once()

    def test_clean_json_file_not_found(self):
        """Test clean_json when file does not exist."""
        with self.assertRaises(CrewForgeException) as context:
            self.service.clean_json("nonexistent.json")
        
        self.assertIn("Output file not found", str(context.exception))

    @patch('amsha.crew_forge.service.shared_json_file_service.JsonCleanerUtils')
    @patch('pathlib.Path.exists')
    def test_clean_json_failure(self, mock_exists, mock_cleaner_class):
        """Test clean_json failure cases."""
        # Case 1: File not found
        mock_exists.return_value = False
        with self.assertRaises(CrewForgeException):
            self.service.clean_json("missing.json")
            
        # Case 2: Cleaner returns False
        mock_exists.return_value = True
        mock_cleaner = mock_cleaner_class.return_value
        mock_cleaner.process_file.return_value = False
        res = self.service.clean_json("test.json")
        self.assertFalse(res)

        # Case 3: Unexpected exception
        mock_cleaner.process_file.side_effect = Exception("Unexpected")
        with self.assertRaises(CrewForgeException):
            self.service.clean_json("test.json")

    @patch('amsha.crew_forge.service.shared_json_file_service.JsonCleanerUtils')
    def test_clean_json_with_metrics_success(self, mock_cleaner_class):
        """Test successful JSON cleaning with metrics."""
        # Create a dummy file
        file_path = os.path.join(self.test_dir, "test.json")
        with open(file_path, 'w') as f:
            f.write("{}")
            
        mock_cleaner_instance = mock_cleaner_class.return_value
        mock_cleaner_instance.process_file.return_value = True
        mock_cleaner_instance.output_file_path = file_path
        
        success, output_path = self.service.clean_json_with_metrics(file_path)
        
        self.assertTrue(success)
        self.assertEqual(output_path, file_path)

    @patch('amsha.crew_forge.service.shared_json_file_service.JsonCleanerUtils')
    @patch('pathlib.Path.exists')
    def test_clean_json_with_metrics_failure(self, mock_exists, mock_cleaner_class):
        """Test clean_json_with_metrics failure cases."""
        # Case 1: File not found
        mock_exists.return_value = False
        with self.assertRaises(CrewForgeException):
            self.service.clean_json_with_metrics("missing.json")
            
        # Case 2: Cleaner returns False
        mock_exists.return_value = True
        mock_cleaner = mock_cleaner_class.return_value
        mock_cleaner.process_file.return_value = False
        success, path = self.service.clean_json_with_metrics("test.json")
        self.assertFalse(success)
        self.assertIsNone(path)

        # Case 3: Unexpected exception
        mock_cleaner.process_file.side_effect = Exception("Unexpected")
        with self.assertRaises(CrewForgeException):
            self.service.clean_json_with_metrics("test.json")

    def test_ensure_output_directory_from_file_path(self):
        """Test ensure_output_directory when given a file path."""
        file_path = os.path.join(self.test_dir, "subdir", "test.json")
        
        result = self.service.ensure_output_directory(file_path)
        
        expected_dir = Path(self.test_dir) / "subdir"
        self.assertEqual(result, expected_dir)
        self.assertTrue(expected_dir.exists())

    def test_ensure_output_directory_from_dir_path(self):
        """Test ensure_output_directory when given a directory path."""
        dir_path = os.path.join(self.test_dir, "new_dir")
        
        result = self.service.ensure_output_directory(dir_path)
        
        expected_dir = Path(dir_path)
        self.assertEqual(result, expected_dir)
        self.assertTrue(expected_dir.exists())

    def test_get_output_file_path(self):
        """Test get_output_file_path standardized construction."""
        base_path = os.path.join(self.test_dir, "output")
        filename = "result.json"
        
        result = self.service.get_output_file_path(base_path, filename)
        
        expected_path = os.path.join(base_path, filename)
        self.assertEqual(result, expected_path)
        self.assertTrue(Path(base_path).exists())

if __name__ == '__main__':
    unittest.main()
