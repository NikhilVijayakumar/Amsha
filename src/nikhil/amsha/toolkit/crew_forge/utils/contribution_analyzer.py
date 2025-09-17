# analyzer.py
import pandas as pd
from typing import Dict, Any
from nikhil.amsha.utils.json_utils import JsonUtils
from nikhil.amsha.utils.yaml_utils import YamlUtils


class ContributionAnalyzer:
    """
    A class to analyze feature contribution from clustered JSON data based on a YAML configuration.
    It calculates the percentage of LLMs that contributed to each feature and saves the
    results to both JSON and Excel formats.
    """

    def __init__(self, config_path: str):
        """Initializes the analyzer by loading the configuration file."""
        print(f"Loading configuration from: {config_path}")
        self.config = YamlUtils.yaml_safe_load(config_path)



    def run(self):
        """Runs all analysis jobs defined in the config file."""
        print("🚀 Starting contribution analysis process...")
        for job_config in self.config.get('analyze_contributions', []):
            self._process_job(job_config)
        print("\n🎉 All analysis jobs are complete.")

    def _process_job(self, job_config: Dict[str, Any]):
        """Processes a single analysis job from the configuration."""
        job_name = job_config.get('name', 'Unnamed Analysis Job')
        print(f"\n--- Running Job: {job_name} ---")

        # --- 1. Load Data ---
        input_file = job_config.get('input_file')
        source_data = JsonUtils.load_json_from_file(input_file)
        if not source_data:
            print(f"❌ Critical Error: Could not load input file for job '{job_name}'. Skipping job.")
            return

        # --- 2. Process Data ---
        print("  -> Calculating contribution percentages...")
        total_llms = job_config.get('total_llms', 1)
        options = job_config.get('options', {})
        feature_list_key = options.get('feature_list_key', 'features')

        processed_data = self._calculate_feature_contribution(source_data, total_llms, feature_list_key)

        # --- 3. Save Outputs ---
        output_json_file = job_config.get('output_json_file')
        if output_json_file:
            JsonUtils.save_json_to_file(processed_data, output_json_file)

        output_excel_file = job_config.get('output_excel_file')
        if output_excel_file:
            self._save_summary_to_excel(processed_data, output_excel_file, feature_list_key)

        print(f"--- Job '{job_name}' complete. ---")



    @staticmethod
    def _calculate_feature_contribution(
            clustered_data: Dict[str, Any], total_llms: int, feature_list_key: str
    ) -> Dict[str, Any]:
        """Calculates the contribution percentage for each feature."""
        if total_llms <= 0:
            print("  -> ❌ Error: Total number of LLMs must be a positive number.")
            return clustered_data

        feature_list = clustered_data.get(feature_list_key, [])
        for feature in feature_list:
            num_contributors = len(feature.get("contributingFeatures", []))
            percentage = (num_contributors / total_llms) * 100
            feature['contributionPercentage'] = round(percentage, 2)
        return clustered_data

    @staticmethod
    def _save_summary_to_excel(
            processed_data: Dict[str, Any], output_filename: str, feature_list_key: str
    ):
        """Saves the key information to an XLSX file."""
        try:
            features_list = processed_data.get(feature_list_key, [])
            if not features_list:
                print("  -> ⚠️ Warning: No features found to export to Excel.")
                return

            rows_for_excel = [
                {
                    'Feature Name': f.get('featureName'),
                    'Contribution %': f.get('contributionPercentage'),
                    'Contributing LLMs (Count)': len(f.get('contributingFeatures', [])),
                    'Description': f.get('description'),
                    'Core Actors': ", ".join(f.get('coreActors', []))
                }
                for f in features_list
            ]

            df = pd.DataFrame(rows_for_excel)
            df.to_excel(output_filename, index=False, engine='openpyxl')
            print(f"  -> ✅ Successfully saved Excel summary to: {output_filename}")
        except Exception as e:
            print(f"  -> ❌ Error saving Excel file: {e}")
