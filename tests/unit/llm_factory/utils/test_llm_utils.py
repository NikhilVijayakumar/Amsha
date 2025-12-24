"""
Unit tests for LLMUtils utility class.
"""
import unittest
import os
from unittest.mock import patch, MagicMock
from amsha.llm_factory.utils.llm_utils import LLMUtils


class TestLLMUtils(unittest.TestCase):
    """Test cases for LLMUtils class."""
    
    def test_noop_function(self):
        """Test that noop function does nothing and doesn't raise errors."""
        # Should not raise any exception
        result = LLMUtils.noop()
        self.assertIsNone(result)
        
        # With various arguments
        result = LLMUtils.noop("arg1", "arg2", key="value")
        self.assertIsNone(result)
    
    def test_disable_telemetry_sets_env_variable(self):
        """Test that disable_telemetry sets OTEL_SDK_DISABLED."""
        # Clear the env var first if it exists
        if "OTEL_SDK_DISABLED" in os.environ:
            del os.environ["OTEL_SDK_DISABLED"]
        
        LLMUtils.disable_telemetry()
        
        self.assertEqual(os.environ.get("OTEL_SDK_DISABLED"), "true")
    
    @patch('amsha.llm_factory.utils.llm_utils.Telemetry')
    def test_disable_telemetry_modifies_telemetry_class(self, mock_telemetry):
        """Test that disable_telemetry modifies Telemetry class methods."""
        # Setup mock Telemetry class with callable methods
        mock_telemetry.method1 = MagicMock()
        mock_telemetry.method2 = MagicMock()
        
        # Make dir() return method names
        with patch('builtins.dir', return_value=['method1', 'method2', '__init__']):
            with patch('builtins.callable', return_value=True):
                LLMUtils.disable_telemetry()
        
        # Verify env variable is set
        self.assertEqual(os.environ.get("OTEL_SDK_DISABLED"), "true")
    
    def test_extract_model_name_with_lm_studio_prefix(self):
        """Test extracting model name with lm_studio/ prefix."""
        model_string = "lm_studio/gpt-4"
        result = LLMUtils.extract_model_name(model_string)
        
        self.assertEqual(result, "gpt-4")
    
    def test_extract_model_name_with_gemini_prefix(self):
        """Test extracting model name with gemini/ prefix."""
        model_string = "gemini/gemini-pro"
        result = LLMUtils.extract_model_name(model_string)
        
        self.assertEqual(result, "gemini-pro")
    
    def test_extract_model_name_with_openai_prefix(self):
        """Test extracting model name with open_ai/ prefix."""
        model_string = "open_ai/gpt-3.5-turbo"
        result = LLMUtils.extract_model_name(model_string)
        
        self.assertEqual(result, "gpt-3.5-turbo")
    
    def test_extract_model_name_with_azure_prefix(self):
        """Test extracting model name with azure prefix."""
        model_string = "azure-gpt-4"
        result = LLMUtils.extract_model_name(model_string)
        
        # Azure is in prefix list, so it should remove it
        self.assertEqual(result, "-gpt-4")
    
    def test_extract_model_name_without_prefix(self):
        """Test extracting model name without any prefix."""
        model_string = "gpt-4-turbo"
        result = LLMUtils.extract_model_name(model_string)
        
        self.assertEqual(result, "gpt-4-turbo")
    
    def test_extract_model_name_empty_string(self):
        """Test extracting model name from empty string."""
        model_string = ""
        result = LLMUtils.extract_model_name(model_string)
        
        self.assertEqual(result, "")
    
    def test_extract_model_name_with_nested_slash(self):
        """Test extracting model name with nested slashes."""
        model_string = "lm_studio/models/gpt-4"
        result = LLMUtils.extract_model_name(model_string)
        
        # Should only remove the lm_studio/ prefix
        self.assertEqual(result, "models/gpt-4")
    
    def test_extract_model_name_case_sensitivity(self):
        """Test that prefix matching is case-sensitive."""
        model_string = "LM_STUDIO/gpt-4"
        result = LLMUtils.extract_model_name(model_string)
        
        # Should not match because of case difference
        self.assertEqual(result, "LM_STUDIO/gpt-4")
    
    def test_extract_model_name_partial_match(self):
        """Test that partial matches don't trigger prefix removal."""
        model_string = "my_lm_studio/gpt-4"
        result = LLMUtils.extract_model_name(model_string)
        
        # Should not remove anything since it's not a full prefix match
        self.assertEqual(result, "my_lm_studio/gpt-4")
    
    def test_extract_model_name_all_prefixes(self):
        """Test extraction works for all defined prefixes."""
        test_cases = [
            ("lm_studio/model", "model"),
            ("gemini/model", "model"),
            ("open_ai/model", "model"),
            ("azuremodel", "model"),  # azure as prefix without slash
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(input=input_str):
                result = LLMUtils.extract_model_name(input_str)
                self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
