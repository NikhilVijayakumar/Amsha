"""
Unit tests for ContributionAnalyzer class.
"""
import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from amsha.crew_monitor.service.contribution_analyzer import ContributionAnalyzer


class TestContributionAnalyzer(unittest.TestCase):
    """Test cases for ContributionAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, 'config.yaml')
        self.input_json = os.path.join(self.test_dir, 'input.json')
        self.output_json = os.path.join(self.test_dir, 'output.json')
        self.output_excel = os.path.join(self.test_dir, 'output.xlsx')
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_initialization_with_valid_config(self):
        """Test proper initialization with valid YAML config."""
        # Create a simple YAML config
        import yaml
        config_data = {'analyze_contributions': []}
        with open(self.config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        analyzer = ContributionAnalyzer(self.config_file)
        
        self.assertIsNotNone(analyzer.config)
        self.assertIn('analyze_contributions', analyzer.config)
    
    def test_calculate_feature_contribution_basic(self):
        """Test basic feature contribution calculation."""
        clustered_data = {
            'features': [
                {
                    'featureName': 'Feature1',
                    'contributingFeatures': ['LLM1', 'LLM2', 'LLM3']
                },
                {
                    'featureName': 'Feature2',
                    'contributingFeatures': ['LLM1']
                }
            ]
        }
        
        result = ContributionAnalyzer._calculate_feature_contribution(
            clustered_data, total_llms=4, feature_list_key='features'
        )
        
        self.assertEqual(result['features'][0]['contributionPercentage'], 75.0)  # 3/4 * 100
        self.assertEqual(result['features'][1]['contributionPercentage'], 25.0)  # 1/4 * 100
    
    def test_calculate_feature_contribution_zero_contributors(self):
        """Test feature contribution with zero contributors."""
        clustered_data = {
            'features': [
                {
                    'featureName': 'Feature1',
                    'contributingFeatures': []
                }
            ]
        }
        
        result = ContributionAnalyzer._calculate_feature_contribution(
            clustered_data, total_llms=5, feature_list_key='features'
        )
        
        self.assertEqual(result['features'][0]['contributionPercentage'], 0.0)
    
    def test_calculate_feature_contribution_all_contributors(self):
        """Test feature contribution when all LLMs contribute."""
        clustered_data = {
            'features': [
                {
                    'featureName': 'Feature1',
                    'contributingFeatures': ['LLM1', 'LLM2', 'LLM3', 'LLM4', 'LLM5']
                }
            ]
        }
        
        result = ContributionAnalyzer._calculate_feature_contribution(
            clustered_data, total_llms=5, feature_list_key='features'
        )
        
        self.assertEqual(result['features'][0]['contributionPercentage'], 100.0)
    
    def test_calculate_feature_contribution_invalid_total_llms(self):
        """Test handling of invalid total_llms value."""
        clustered_data = {'features': []}
        
        # Test with zero
        result = ContributionAnalyzer._calculate_feature_contribution(
            clustered_data, total_llms=0, feature_list_key='features'
        )
        self.assertEqual(result, clustered_data)
        
        # Test with negative
        result = ContributionAnalyzer._calculate_feature_contribution(
            clustered_data, total_llms=-1, feature_list_key='features'
        )
        self.assertEqual(result, clustered_data)
    
    def test_calculate_feature_contribution_rounding(self):
        """Test that percentages are properly rounded to 2 decimal places."""
        clustered_data = {
            'features': [
                {
                    'featureName': 'Feature1',
                    'contributingFeatures': ['LLM1', 'LLM2']
                }
            ]
        }
        
        result = ContributionAnalyzer._calculate_feature_contribution(
            clustered_data, total_llms=3, feature_list_key='features'
        )
        
        # 2/3 * 100 = 66.666... should be rounded to 66.67
        self.assertEqual(result['features'][0]['contributionPercentage'], 66.67)
    
    def test_calculate_feature_contribution_custom_key(self):
        """Test feature contribution with custom feature list key."""
        clustered_data = {
            'custom_features': [
                {
                    'featureName': 'Feature1',
                    'contributingFeatures': ['LLM1', 'LLM2']
                }
            ]
        }
        
        result = ContributionAnalyzer._calculate_feature_contribution(
            clustered_data, total_llms=4, feature_list_key='custom_features'
        )
        
        self.assertEqual(result['custom_features'][0]['contributionPercentage'], 50.0)
    
    def test_save_summary_to_excel_basic(self):
        """Test basic Excel summary saving."""
        processed_data = {
            'features': [
                {
                    'featureName': 'Feature1',
                    'contributionPercentage': 75.0,
                    'contributingFeatures': ['LLM1', 'LLM2', 'LLM3'],
                    'description': 'Test feature',
                    'coreActors': ['Actor1', 'Actor2']
                }
            ]
        }
        
        ContributionAnalyzer._save_summary_to_excel(
            processed_data, self.output_excel, 'features'
        )
        
        self.assertTrue(os.path.exists(self.output_excel))
        
        # Verify Excel content
        import pandas as pd
        df = pd.read_excel(self.output_excel)
        
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['Feature Name'], 'Feature1')
        self.assertEqual(df.iloc[0]['Contribution %'], 75.0)
        self.assertEqual(df.iloc[0]['Contributing LLMs (Count)'], 3)
    
    def test_save_summary_to_excel_empty_features(self):
        """Test Excel saving with empty features list."""
        processed_data = {'features': []}
        
        # Should not raise exception
        ContributionAnalyzer._save_summary_to_excel(
            processed_data, self.output_excel, 'features'
        )
        
        # File should not be created for empty data
        self.assertFalse(os.path.exists(self.output_excel))
    
    def test_save_summary_to_excel_creates_directory(self):
        """Test that Excel saving creates parent directories."""
        nested_path = os.path.join(self.test_dir, 'nested', 'deep', 'output.xlsx')
        processed_data = {
            'features': [
                {
                    'featureName': 'Feature1',
                    'contributionPercentage': 50.0,
                    'contributingFeatures': ['LLM1'],
                    'description': 'Test',
                    'coreActors': []
                }
            ]
        }
        
        ContributionAnalyzer._save_summary_to_excel(
            processed_data, nested_path, 'features'
        )
        
        self.assertTrue(os.path.exists(nested_path))
    
    def test_save_summary_to_excel_multiple_features(self):
        """Test Excel saving with multiple features."""
        processed_data = {
            'features': [
                {
                    'featureName': 'Feature1',
                    'contributionPercentage': 75.0,
                    'contributingFeatures': ['LLM1', 'LLM2', 'LLM3'],
                    'description': 'First feature',
                    'coreActors': ['Actor1']
                },
                {
                    'featureName': 'Feature2',
                    'contributionPercentage': 25.0,
                    'contributingFeatures': ['LLM1'],
                    'description': 'Second feature',
                    'coreActors': ['Actor2', 'Actor3']
                }
            ]
        }
        
        ContributionAnalyzer._save_summary_to_excel(
            processed_data, self.output_excel, 'features'
        )
        
        import pandas as pd
        df = pd.read_excel(self.output_excel)
        
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[1]['Feature Name'], 'Feature2')
        self.assertEqual(df.iloc[1]['Core Actors'], 'Actor2, Actor3')
    
    @patch('amsha.crew_monitor.service.contribution_analyzer.JsonUtils.load_json_from_file')
    @patch('amsha.crew_monitor.service.contribution_analyzer.JsonUtils.save_json_to_file')
    def test_process_job_success(self, mock_save, mock_load):
        """Test successful job processing."""
        # Mock data loading
        mock_load.return_value = {
            'features': [
                {
                    'featureName': 'Feature1',
                    'contributingFeatures': ['LLM1', 'LLM2']
                }
            ]
        }
        
        job_config = {
            'name': 'Test Job',
            'input_file': 'input.json',
            'output_json_file': 'output.json',
            'total_llms': 4,
            'options': {'feature_list_key': 'features'}
        }
        
        # Create minimal config
        config_data = {'analyze_contributions': [job_config]}
        import yaml
        with open(self.config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        analyzer = ContributionAnalyzer(self.config_file)
        analyzer._process_job(job_config)
        
        # Verify save was called
        self.assertTrue(mock_save.called)
        
        # Verify the processed data has contribution percentages
        saved_data = mock_save.call_args[0][0]
        self.assertIn('contributionPercentage', saved_data['features'][0])
        self.assertEqual(saved_data['features'][0]['contributionPercentage'], 50.0)
    
    @patch('amsha.crew_monitor.service.contribution_analyzer.JsonUtils.load_json_from_file')
    def test_process_job_missing_input_file(self, mock_load):
        """Test job processing when input file is missing."""
        mock_load.return_value = None  # Simulate file not found
        
        job_config = {
            'name': 'Test Job',
            'input_file': 'missing.json',
            'total_llms': 4
        }
        
        config_data = {'analyze_contributions': [job_config]}
        import yaml
        with open(self.config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        analyzer = ContributionAnalyzer(self.config_file)
        
        # Should not raise exception
        analyzer._process_job(job_config)
    
    @patch('amsha.crew_monitor.service.contribution_analyzer.JsonUtils.load_json_from_file')
    @patch('amsha.crew_monitor.service.contribution_analyzer.JsonUtils.save_json_to_file')
    def test_run_multiple_jobs(self, mock_save, mock_load):
        """Test running multiple analysis jobs."""
        mock_load.return_value = {
            'features': [
                {'featureName': 'F1', 'contributingFeatures': ['LLM1']}
            ]
        }
        
        config_data = {
            'analyze_contributions': [
                {
                    'name': 'Job1',
                    'input_file': 'input1.json',
                    'output_json_file': 'output1.json',
                    'total_llms': 2
                },
                {
                    'name': 'Job2',
                    'input_file': 'input2.json',
                    'output_json_file': 'output2.json',
                    'total_llms': 3
                }
            ]
        }
        
        import yaml
        with open(self.config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        analyzer = ContributionAnalyzer(self.config_file)
        analyzer.run()
        
        # Should have called save twice (once for each job)
        self.assertEqual(mock_save.call_count, 2)


    def test_save_summary_to_excel_exception(self):
        """Test that _save_summary_to_excel handles exceptions gracefully."""
        import yaml
        config_data = {'analyze_contributions': []}
        with open(self.config_file, 'w') as f:
            yaml.dump(config_data, f)
        analyzer = ContributionAnalyzer(self.config_file)
        
        processed_data = {
            'features': [{'featureName': 'F1', 'contributionPercentage': 50}]
        }
        with patch('pandas.DataFrame.to_excel', side_effect=Exception("Excel Error")), \
             patch('builtins.print') as mock_print:
            analyzer._save_summary_to_excel(processed_data, "dummy.xlsx", "features")
            mock_print.assert_any_call("  -> ❌ Error saving Excel file: Excel Error")


if __name__ == '__main__':
    unittest.main()
