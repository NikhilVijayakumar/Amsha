"""
Unit tests for YamlUtils utility class.
"""
import unittest
import tempfile
import os
import yaml
from unittest.mock import patch
from amsha.utils.yaml_utils import YamlUtils


class TestYamlUtils(unittest.TestCase):
    """Test cases for YamlUtils class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test.yaml')
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_yaml_safe_load_success(self):
        """Test successful loading of a valid YAML file."""
        test_data = {
            "name": "test",
            "value": 42,
            "nested": {
                "key": "value"
            }
        }
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f)
        
        result = YamlUtils.yaml_safe_load(self.test_file)
        
        self.assertIsNotNone(result)
        self.assertEqual(result, test_data)
        self.assertEqual(result["name"], "test")
        self.assertEqual(result["value"], 42)
        self.assertEqual(result["nested"]["key"], "value")
    
    def test_yaml_safe_load_with_list(self):
        """Test loading YAML file containing a list."""
        test_data = [
            {"id": 1, "name": "first"},
            {"id": 2, "name": "second"}
        ]
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f)
        
        result = YamlUtils.yaml_safe_load(self.test_file)
        
        self.assertIsNotNone(result)
        self.assertEqual(result, test_data)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
    
    def test_yaml_safe_load_empty_file(self):
        """Test loading an empty YAML file."""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write('')
        
        result = YamlUtils.yaml_safe_load(self.test_file)
        
        self.assertIsNone(result)
    
    def test_yaml_safe_load_file_not_found(self):
        """Test that FileNotFoundError causes exit."""
        non_existent_file = os.path.join(self.test_dir, 'does_not_exist.yaml')
        
        with self.assertRaises(SystemExit):
            YamlUtils.yaml_safe_load(non_existent_file)
    
    def test_yaml_safe_load_invalid_yaml(self):
        """Test that invalid YAML causes exit."""
        # Write invalid YAML
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write('key: value\n  invalid: indentation\n bad structure')
        
        with self.assertRaises(SystemExit):
            YamlUtils.yaml_safe_load(self.test_file)
    
    def test_yaml_safe_load_unicode_content(self):
        """Test loading YAML with unicode content."""
        test_data = {
            "message": "Hello 世界",
            "emoji": "🌍"
        }
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f, allow_unicode=True)
        
        result = YamlUtils.yaml_safe_load(self.test_file)
        
        self.assertEqual(result["message"], "Hello 世界")
        self.assertEqual(result["emoji"], "🌍")
    
    def test_yaml_safe_load_complex_structure(self):
        """Test loading complex YAML structure."""
        test_data = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "credentials": {
                    "user": "admin",
                    "password": "secret"
                }
            },
            "services": ["web", "api", "worker"],
            "enabled": True
        }
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f)
        
        result = YamlUtils.yaml_safe_load(self.test_file)
        
        self.assertEqual(result["database"]["host"], "localhost")
        self.assertEqual(result["database"]["port"], 5432)
        self.assertEqual(len(result["services"]), 3)
        self.assertTrue(result["enabled"])
    
    @patch('builtins.print')
    def test_yaml_safe_load_file_not_found_error_message(self, mock_print):
        """Test that file not found produces appropriate error message."""
        non_existent_file = os.path.join(self.test_dir, 'missing.yaml')
        
        with self.assertRaises(SystemExit):
            YamlUtils.yaml_safe_load(non_existent_file)
        
        # Verify error message was printed
        mock_print.assert_called_once()
        call_args = str(mock_print.call_args)
        self.assertIn("Error", call_args)
        self.assertIn("not found", call_args)
    
    @patch('builtins.print')
    def test_yaml_safe_load_invalid_yaml_error_message(self, mock_print):
        """Test that invalid YAML produces appropriate error message."""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write('invalid: [unclosed list')
        
        with self.assertRaises(SystemExit):
            YamlUtils.yaml_safe_load(self.test_file)
        
        # Verify error message was printed
        mock_print.assert_called_once()
        call_args = str(mock_print.call_args)
        self.assertIn("Error", call_args)
        self.assertIn("parse", call_args)


if __name__ == '__main__':
    unittest.main()
