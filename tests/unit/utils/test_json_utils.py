"""
Unit tests for JsonUtils utility class.
"""
import unittest
import json
import tempfile
import os
from pathlib import Path
from amsha.utils.json_utils import JsonUtils


class TestJsonUtils(unittest.TestCase):
    """Test cases for JsonUtils class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test.json')
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up test directory
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_load_json_from_file_success(self):
        """Test successful loading of a valid JSON file."""
        test_data = {"name": "test", "value": 42}
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        result = JsonUtils.load_json_from_file(self.test_file)
        
        self.assertIsNotNone(result)
        self.assertEqual(result, test_data)
        self.assertEqual(result["name"], "test")
        self.assertEqual(result["value"], 42)
    
    def test_load_json_from_file_with_list(self):
        """Test loading JSON file containing a list."""
        test_data = [1, 2, 3, 4, 5]
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        result = JsonUtils.load_json_from_file(self.test_file)
        
        self.assertIsNotNone(result)
        self.assertEqual(result, test_data)
        self.assertIsInstance(result, list)
    
    def test_load_json_from_file_not_found(self):
        """Test handling of FileNotFoundError."""
        non_existent_file = os.path.join(self.test_dir, 'does_not_exist.json')
        
        result = JsonUtils.load_json_from_file(non_existent_file)
        
        self.assertIsNone(result)
    
    def test_load_json_from_file_invalid_json(self):
        """Test handling of invalid JSON content."""
        # Write invalid JSON
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write('{ invalid json content }')
        
        result = JsonUtils.load_json_from_file(self.test_file)
        
        self.assertIsNone(result)
    
    def test_load_json_from_file_empty_path(self):
        """Test handling of empty file path."""
        result = JsonUtils.load_json_from_file('')
        
        self.assertIsNone(result)
    
    def test_load_json_from_file_none_path(self):
        """Test handling of None file path."""
        result = JsonUtils.load_json_from_file(None)
        
        self.assertIsNone(result)
    
    def test_save_json_to_file_success(self):
        """Test successful saving of JSON data to file."""
        test_data = {"name": "test", "value": 42}
        
        result = JsonUtils.save_json_to_file(test_data, self.test_file)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.test_file))
        
        # Verify content
        with open(self.test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data, test_data)
    
    def test_save_json_to_file_with_list(self):
        """Test saving a list to JSON file."""
        test_data = [{"id": 1}, {"id": 2}]
        
        result = JsonUtils.save_json_to_file(test_data, self.test_file)
        
        self.assertTrue(result)
        
        # Verify content
        with open(self.test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data, test_data)
    
    def test_save_json_to_file_creates_directory(self):
        """Test that saving creates parent directories if they don't exist."""
        nested_dir = os.path.join(self.test_dir, 'nested', 'deep', 'path')
        nested_file = os.path.join(nested_dir, 'test.json')
        test_data = {"test": "data"}
        
        result = JsonUtils.save_json_to_file(test_data, nested_file)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(nested_dir))
        self.assertTrue(os.path.exists(nested_file))
    
    def test_save_json_to_file_unicode_content(self):
        """Test saving JSON with unicode content."""
        test_data = {"message": "Hello 世界 🌍"}
        
        result = JsonUtils.save_json_to_file(test_data, self.test_file)
        
        self.assertTrue(result)
        
        # Verify unicode is preserved
        with open(self.test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data["message"], "Hello 世界 🌍")
    
    def test_load_json_from_directory(self):
        """Test loading all JSON files from a directory."""
        # Create multiple JSON files
        file1 = os.path.join(self.test_dir, 'file1.json')
        file2 = os.path.join(self.test_dir, 'file2.json')
        file3 = os.path.join(self.test_dir, 'not_json.txt')
        
        with open(file1, 'w', encoding='utf-8') as f:
            json.dump({"file": 1}, f)
        with open(file2, 'w', encoding='utf-8') as f:
            json.dump({"file": 2}, f)
        with open(file3, 'w', encoding='utf-8') as f:
            f.write("not json")
        
        result = JsonUtils._load_json_from_directory(self.test_dir)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)  # Should only load .json files
        
        # Check that both files were loaded
        values = [item["file"] for item in result]
        self.assertIn(1, values)
        self.assertIn(2, values)
    
    def test_load_json_from_directory_empty(self):
        """Test loading from directory with no JSON files."""
        result = JsonUtils._load_json_from_directory(self.test_dir)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
    
    def test_load_json_from_directory_not_exists(self):
        """Test loading from non-existent directory."""
        non_existent_dir = os.path.join(self.test_dir, 'does_not_exist')
        
        result = JsonUtils._load_json_from_directory(non_existent_dir)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
    
    def test_load_json_from_directory_with_invalid_json(self):
        """Test that invalid JSON files are skipped with warning."""
        valid_file = os.path.join(self.test_dir, 'valid.json')
        invalid_file = os.path.join(self.test_dir, 'invalid.json')
        
        with open(valid_file, 'w', encoding='utf-8') as f:
            json.dump({"valid": True}, f)
        with open(invalid_file, 'w', encoding='utf-8') as f:
            f.write('{ invalid }')
        
        result = JsonUtils._load_json_from_directory(self.test_dir)
        
        # Should load only the valid file
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {"valid": True})


if __name__ == '__main__':
    unittest.main()
