# reporter.py
import os
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

from amsha.utils.json_utils import JsonUtils
from amsha.utils.yaml_utils import YamlUtils


class ReportingTool:
    """
    A class to generate and combine Excel reports from JSON data based on a YAML configuration.
    """

    def __init__(self, config_path: str):
        """Initializes the tool by loading the configuration file."""
        print(f"Loading configuration from: {config_path}")
        self.config = YamlUtils.yaml_safe_load(config_path)

    def run(self):
        """Runs all reporting jobs defined in the config file."""
        print("🚀 Starting reporting tool...")
        if 'generate_reports' in self.config:
            self._run_generate_jobs()
        if 'combine_reports' in self.config:
            self._run_combine_jobs()
        print("\n🎉 Reporting process complete.")

    def _run_generate_jobs(self):
        """Executes all 'generate report' jobs from the config."""
        print("\n--- Starting: Generate Reports (JSON -> Excel) ---")
        for job_config in self.config.get('generate_reports', []):
            self._generate_single_report(job_config)

    def _run_combine_jobs(self):
        """Executes all 'combine reports' jobs from the config."""
        print("\n--- Starting: Combine Reports (Excel -> Excel) ---")
        for job_config in self.config.get('combine_reports', []):
            self._combine_reports(job_config)

    def _generate_single_report(self, job_config: Dict[str, Any]):
        """Generates a single Excel report from a directory of JSON files."""
        job_name = job_config.get('name', 'Unnamed Generate Job')
        print(f"\nProcessing Job: '{job_name}'")

        input_dir = job_config['input_directory']
        output_filename = job_config['output_filename']
        opts = job_config.get('options', {})

        json_files = JsonUtils._load_json_from_directory(input_dir)
        if not json_files:
            return

        processed_data = []
        for data in json_files:
            row_data = {}
            row_data['Feature Name'] = data.get(opts.get('feature_name_key', 'featureName'), 'Unknown')
            for metric in data.get(opts.get('evaluation_list_key', 'evaluation'), []):
                metric_name = metric.get(opts.get('metric_name_key', 'metricName'))
                if metric_name:
                    row_data[f"{metric_name}_{opts.get('score_key', 'weightedScore')}"] = metric.get(
                        opts.get('score_key', 'weightedScore'))
            row_data.update(data.get(opts.get('summary_key', 'scoreSummary'), {}))
            processed_data.append(row_data)

        df = pd.DataFrame(processed_data)
        if df.empty:
            print(f"  -> ⚠️ No data extracted for job '{job_name}'.")
            return

        # Simple reordering of columns
        cols = df.columns.tolist()
        if 'Feature Name' in cols:
            cols.insert(0, cols.pop(cols.index('Feature Name')))
            df = df[cols]

        # Add Mean row
        numeric_cols = df.select_dtypes(include='number').columns
        mean_df = pd.DataFrame(df[numeric_cols].mean().round(2)).T
        mean_df.index = ['Mean']

        try:
            dirname = os.path.dirname(output_filename)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Evaluation Summary', index=False)
                mean_df.to_excel(writer, sheet_name='Evaluation Summary', startrow=len(df) + 2, header=False)
            print(f"  -> ✅ Success! Report saved to '{output_filename}'")
        except Exception as e:
            print(f"  -> ❌ Error saving Excel file for job '{job_name}': {e}")

    def _combine_reports(self, job_config: Dict[str, Any]):
        """Combines multiple Excel files into a single report."""
        job_name = job_config.get('name', 'Unnamed Combine Job')
        print(f"\nProcessing Job: '{job_name}'")

        output_filename = job_config['output_filename']
        files_and_columns = job_config.get('files_and_columns', {})

        if not files_and_columns:
            print(f"  -> ⚠️ No files specified for combination in job '{job_name}'.")
            return

        valid_files = []
        for file_path_str, columns in files_and_columns.items():
            file_path = Path(file_path_str)
            if file_path.is_file() and file_path.suffix.lower() == '.xlsx':
                valid_files.append((file_path, columns))
            else:
                print(f"  -> ⚠️ Skipping invalid file: '{file_path_str}'")

        if not valid_files:
            print(f"  -> ⚠️ No valid files found to combine for job '{job_name}'.")
            return

        summary_data_list = []
        sheets_to_write = {}
        
        for file_path, columns in valid_files:
            try:
                sheet_name = file_path.stem[:31]
                df = pd.read_excel(file_path)
                sheets_to_write[sheet_name] = df

                required_cols = ['Feature Name'] + columns
                if all(col in df.columns for col in required_cols):
                    chunk = df[df['Feature Name'].notna() & (df['Feature Name'] != 'Mean')][required_cols].copy()
                    chunk['Source Report'] = sheet_name
                    summary_data_list.append(chunk)
            except Exception as e:
                print(f"  -> ❌ Error processing '{file_path}': {e}")

        if not sheets_to_write:
            print(f"  -> ⚠️ No data could be read from the specified files for job '{job_name}'.")
            return

        dirname = os.path.dirname(output_filename)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
            
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
            for sheet_name, df in sheets_to_write.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

            if summary_data_list:
                full_summary_df = pd.concat(summary_data_list, ignore_index=True)
                melted = full_summary_df.melt(
                    id_vars=['Feature Name', 'Source Report'],
                    var_name='Metric',
                    value_name='Value'
                ).dropna(subset=['Value'])

                pivot = melted.pivot_table(
                    index='Feature Name',
                    columns=['Source Report', 'Metric'],
                    values='Value',
                    aggfunc='first'
                )
                pivot.to_excel(writer, sheet_name='Summary')

        print(f"  -> ✅ Success! Combined report saved to '{output_filename}'")

