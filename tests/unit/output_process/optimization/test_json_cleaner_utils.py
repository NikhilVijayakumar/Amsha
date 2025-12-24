"""
Unit tests for JsonCleanerUtils class.
"""
import unittest
import tempfile
import os
import json
from pathlib import Path
from amsha.output_process.optimization.json_cleaner_utils import JsonCleanerUtils


class TestJsonCleanerUtils(unittest.TestCase):
    """Test cases for JsonCleanerUtils class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test.json')
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test proper initialization of JsonCleanerUtils."""
        cleaner = JsonCleanerUtils(self.test_file)
        
        self.assertEqual(str(cleaner.input_file_path), self.test_file)
        self.assertIsNone(cleaner.output_file_path)
    
    def test_process_file_success_with_valid_json(self):
        """Test successful processing of valid JSON file."""
        test_data = {"name": "test", "value": 42}
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        cleaner = JsonCleanerUtils(self.test_file)
        result = cleaner.process_file()
        
        self.assertTrue(result)
        self.assertIsNotNone(cleaner.output_file_path)
        self.assertEqual(cleaner.output_file_path, str(self.test_file))
    
    def test_process_file_with_complex_json(self):
        """Test processing complex nested JSON structure."""
        test_data = {
            "users": [
                {"id": 1, "name": "Alice", "roles": ["admin", "user"]},
                {"id": 2, "name": "Bob", "roles": ["user"]}
            ],
            "metadata": {
                "version": "1.0",
                "timestamp": "2024-12-24T14:00:00Z"
            }
        }
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        cleaner = JsonCleanerUtils(self.test_file)
        result = cleaner.process_file()
        
        self.assertTrue(result)
    
    def test_process_file_file_not_found(self):
        """Test handling of non-existent input file."""
        non_existent_file = os.path.join(self.test_dir, 'does_not_exist.json')
        
        cleaner = JsonCleanerUtils(non_existent_file)
        result = cleaner.process_file()
        
        self.assertFalse(result)
        self.assertIsNone(cleaner.output_file_path)
    
    def test_process_file_invalid_json(self):
        """Test handling of invalid JSON content."""
        # Write invalid JSON
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write('{ invalid json content }')
        
        cleaner = JsonCleanerUtils(self.test_file)
        result = cleaner.process_file()
        
        self.assertFalse(result)
        self.assertIsNone(cleaner.output_file_path)
    
    def test_process_file_empty_json_object(self):
        """Test processing empty JSON object."""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump({}, f)
        
        cleaner = JsonCleanerUtils(self.test_file)
        result = cleaner.process_file()
        
        self.assertTrue(result)
    
    def test_process_file_empty_json_array(self):
        """Test processing empty JSON array."""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        cleaner = JsonCleanerUtils(self.test_file)
        result = cleaner.process_file()
        
        self.assertTrue(result)
    
    def test_process_file_json_with_unicode(self):
        """Test processing JSON with unicode characters."""
        test_data = {
            "message": "Hello 世界 🌍",
            "symbols": "© ® ™ € £"
        }
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False)
        
        cleaner = JsonCleanerUtils(self.test_file)
        result = cleaner.process_file()
        
        self.assertTrue(result)
    
    def test_process_file_with_whitespace(self):
        """Test processing JSON file with extra whitespace."""
        test_data = {"key": "value"}
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write('\n\n  ')
            json.dump(test_data, f)
            f.write('  \n\n')
        
        cleaner = JsonCleanerUtils(self.test_file)
        result = cleaner.process_file()
        
        self.assertTrue(result)
    
    def test_process_file_malformed_json_missing_bracket(self):
        """Test handling of malformed JSON missing closing bracket."""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write('{"key": "value"')
        
        cleaner = JsonCleanerUtils(self.test_file)
        result = cleaner.process_file()
        
        self.assertFalse(result)
    
    def test_process_file_malformed_json_extra_comma(self):
        """Test handling of JSON with trailing comma."""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write('{"key": "value",}')
        
        cleaner = JsonCleanerUtils(self.test_file)
        result = cleaner.process_file()
        
        self.assertFalse(result)
    
    def test_process_file_sets_output_path_correctly(self):
        """Test that output_file_path is set correctly on success."""
        test_data = {"test": True}
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        cleaner = JsonCleanerUtils(self.test_file)
        cleaner.process_file()
        
        self.assertEqual(cleaner.output_file_path, str(self.test_file))
        self.assertTrue(os.path.exists(cleaner.output_file_path))
    
    def test_process_file_with_numbers_and_booleans(self):
        """Test processing JSON with various data types."""
        test_data = {
            "integer": 42,
            "float": 3.14159,
            "boolean_true": True,
            "boolean_false": False,
            "null_value": None
        }
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        cleaner = JsonCleanerUtils(self.test_file)
        result = cleaner.process_file()
        
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
