"""
Unit tests for SharedInputPreparationService class.
"""
import unittest
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from amsha.crew_forge.service.shared_input_preparation_service import SharedInputPreparationService
from amsha.crew_forge.exceptions import CrewConfigurationException, InputPreparationException


class TestSharedInputPreparationService(unittest.TestCase):
    """Test cases for SharedInputPreparationService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = SharedInputPreparationService()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_initialization(self):
        """Test proper initialization of SharedInputPreparationService."""
        self.assertIsNotNone(self.service)
        
    def test_prepare_inputs_for_direct_success(self):
        """Test successful input preparation with direct values."""
        job_config = {
            "crews": {
                "test_crew": {
                    "input": {
                        "topic": "AI Agents"
                    }
                }
            }
        }
        
        result = self.service.prepare_inputs_for("test_crew", job_config)
        
        self.assertEqual(result, "AI Agents")

    def test_prepare_inputs_for_file_text_success(self):
        """Test successful input preparation from text file."""
        file_path = os.path.join(self.test_dir, "input.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Hello from file")
            
        job_config = {
            "crews": {
                "test_crew": {
                    "input": {
                        "content": {
                            "source": "file",
                            "path": file_path,
                            "format": "text"
                        }
                    }
                }
            }
        }
        
        result = self.service.prepare_inputs_for("test_crew", job_config)
        
        self.assertEqual(result, "Hello from file")

    def test_prepare_inputs_for_file_json_success(self):
        """Test successful input preparation from JSON file."""
        file_path = os.path.join(self.test_dir, "input.json")
        data = {"key": "value"}
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
            
        job_config = {
            "crews": {
                "test_crew": {
                    "input": {
                        "data": {
                            "source": "file",
                            "path": file_path,
                            "format": "json"
                        }
                    }
                }
            }
        }
        
        result = self.service.prepare_inputs_for("test_crew", job_config)
        
        self.assertEqual(result, data)

    def test_prepare_inputs_for_crew_not_found(self):
        """Test error when crew definition is missing."""
        job_config = {"crews": {}}
        
        with self.assertRaises(CrewConfigurationException) as context:
            self.service.prepare_inputs_for("nonexistent", job_config)
        
        self.assertIn("crew definition not found", str(context.exception))

    def test_prepare_inputs_for_file_not_found(self):
        """Test error when input file is missing."""
        job_config = {
            "crews": {
                "test_crew": {
                    "input": {
                        "content": {
                            "source": "file",
                            "path": "nonexistent.txt"
                        }
                    }
                }
            }
        }
        
        with self.assertRaises(InputPreparationException) as context:
            self.service.prepare_inputs_for("test_crew", job_config)
        
        self.assertIn("Input file not found", str(context.exception))

    def test_prepare_multiple_inputs_for_success(self):
        """Test successful preparation of multiple inputs."""
        file_path = os.path.join(self.test_dir, "input.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("File content")
            
        job_config = {
            "crews": {
                "test_crew": {
                    "input": [
                        {
                            "key_name": "topic",
                            "source": "direct",
                            "value": "AI"
                        },
                        {
                            "key_name": "context",
                            "source": "file",
                            "path": file_path
                        }
                    ]
                }
            }
        }
        
        result = self.service.prepare_multiple_inputs_for("test_crew", job_config)
        
        self.assertEqual(result, {
            "topic": "AI",
            "context": "File content"
        })

    def test_prepare_multiple_inputs_invalid_format(self):
        """Test error when multiple inputs format is invalid (missing key_name)."""
        job_config = {
            "crews": {
                "test_crew": {
                    "input": [
                        {"source": "direct", "value": "AI"}
                    ]
                }
            }
        }
        
        with self.assertRaises(CrewConfigurationException) as context:
            self.service.prepare_multiple_inputs_for("test_crew", job_config)
        
        self.assertIn("missing 'key_name'", str(context.exception))

    def test_prepare_multiple_inputs_invalid_source(self):
        """Test error when input source is invalid."""
        job_config = {
            "crews": {
                "test_crew": {
                    "input": [
                        {
                            "key_name": "test",
                            "source": "invalid"
                        }
                    ]
                }
            }
        }
        
        with self.assertRaises(CrewConfigurationException) as context:
            self.service.prepare_multiple_inputs_for("test_crew", job_config)
        
        self.assertIn("invalid input source", str(context.exception))

    def test_prepare_inputs_for_failure(self):
        """Test prepare_inputs_for failure cases."""
        # Case 1: Crew not found
        job_config = {"crews": {}}
        with self.assertRaises(CrewConfigurationException):
            self.service.prepare_inputs_for("missing", job_config)
            
        # Case 2: File not found
        job_config = {
            "crews": {
                "c1": {"input": {"p1": {"source": "file", "path": "missing.txt"}}}
            }
        }
        with patch('pathlib.Path.exists', return_value=False):
            with self.assertRaises(InputPreparationException):
                self.service.prepare_inputs_for("c1", job_config)

        # Case 3: Unexpected exception
        with patch('pathlib.Path.exists', side_effect=Exception("Unexpected")):
            with self.assertRaises(InputPreparationException):
                self.service.prepare_inputs_for("c1", job_config)

    def test_prepare_multiple_inputs_for_failure(self):
        """Test prepare_multiple_inputs_for failure cases."""
        # Case 1: Crew not found
        job_config = {"crews": {}}
        with self.assertRaises(CrewConfigurationException):
            self.service.prepare_multiple_inputs_for("missing", job_config)
            
        # Case 2: Invalid input definition (missing key_name)
        job_config = {
            "crews": {
                "c1": {"input": [{"source": "direct", "value": "v1"}]}
            }
        }
        with self.assertRaises(CrewConfigurationException):
            self.service.prepare_multiple_inputs_for("c1", job_config)
            
        # Case 3: Invalid input source
        job_config = {
            "crews": {
                "c1": {"input": [{"key_name": "k1", "source": "invalid"}]}
            }
        }
        with self.assertRaises(CrewConfigurationException):
            self.service.prepare_multiple_inputs_for("c1", job_config)

        # Case 4: File not found
        job_config = {
            "crews": {
                "c1": {"input": [{"key_name": "k1", "source": "file", "path": "missing.txt"}]}
            }
        }
        with patch('pathlib.Path.exists', return_value=False):
            with self.assertRaises(InputPreparationException):
                self.service.prepare_multiple_inputs_for("c1", job_config)

        # Case 5: Unexpected exception
        with patch('pathlib.Path.exists', side_effect=Exception("Unexpected")):
            with self.assertRaises(InputPreparationException):
                self.service.prepare_multiple_inputs_for("c1", job_config)


if __name__ == '__main__':
    unittest.main()
