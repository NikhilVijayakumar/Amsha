import os
from typing import List, Dict, Any

import numpy as np
import pandas as pd
from nikhil.amsha.utils.json_utils import JsonUtils
from nikhil.vak.utils.yaml_utils import YamlUtils


class EvaluationReportTool:
    """
    A class to generate a consolidated Excel report by loading and combining
    graded evaluations from multiple JSON input files.
    """

    def __init__(self, config_path: str):
        """Initializes the tool by loading the configuration file."""
        print(f"Loading configuration from: {config_path}")
        self.config = YamlUtils.yaml_safe_load(config_path)
        self.grading_scale = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}

    def run(self):
        """Runs the consolidated reporting job defined in the config file."""
        print("🚀 Starting consolidated reporting tool...")
        report_config = self.config.get('evaluation_report', {})
        if report_config:
            self._generate_evaluation_report(report_config)
        else:
            print("❌ Error: 'evaluation_report' configuration not found in YAML.")
        print("\n🎉 Reporting process complete.")

    def _apply_relative_grading(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies relative grading based on the distribution of 'totalFinalScore'."""
        if 'totalFinalScore' not in df.columns or df.empty:
            print("  -> ⚠️ Cannot apply relative grading: Missing 'totalFinalScore' or empty data.")
            df['Relative Grade'] = 'N/A'
            df['Grade Point'] = 0.0
            return df

        scores = df['totalFinalScore']
        mean = np.mean(scores)
        std = np.std(scores)

        # Define grade boundaries based on standard deviations from the mean
        grade_boundaries = [
            (mean + std, 'A'),
            (mean, 'B'),
            (mean - std, 'C'),
        ]

        def get_grade(score):
            for boundary, grade in grade_boundaries:
                if score >= boundary:
                    return grade
            return 'D'

        df['Relative Grade'] = scores.apply(get_grade)
        df['Grade Point'] = df['Relative Grade'].map(self.grading_scale).fillna(0.0)

        return df

    def _generate_evaluation_report(self, job_config: Dict[str, Any]):
        """
        Loads graded evaluations from multiple JSON files, consolidates them,
        and generates the multi-sheet Excel report.
        """
        job_name = job_config.get('name', 'Consolidated Evaluation Report')
        print(f"\nProcessing Job: '{job_name}'")

        input_files = job_config.get('input_files', [])
        if not input_files:
            print("  -> ❌ Error: 'input_files' list is empty in YAML configuration.")
            return

        output_excel = job_config['output_excel']
        output_json = job_config.get('output_json')

        all_evaluations: List[Dict[str, Any]] = []

        # --- STEP 1: Load and Consolidate Data from Multiple Files ---
        for input_file in input_files:
            try:
                print(f"  -> Loading data from: {input_file}")

                # 🔑 FIX 1: Extract the 'eval_model' name from the input filename
                basename = os.path.basename(input_file)
                eval_model_name = basename.replace('aggregated_results_', '').replace('.json', '')

                full_data = JsonUtils.load_json_from_file(input_file)
                evaluations_list = full_data.get('gradedEvaluations', [])

                if evaluations_list:
                    # 🔑 FIX 2: Add the 'eval_model' name to each dictionary
                    for record in evaluations_list:
                        record['eval_model'] = eval_model_name

                    # Append all list items to the master list
                    all_evaluations.extend(evaluations_list)
                    print(f"     -> Added {len(evaluations_list)} evaluations (as '{eval_model_name}').")
                else:
                    print(f"     -> ⚠️ No 'gradedEvaluations' found in {input_file}.")

            except Exception as e:
                print(f"  -> ❌ Error loading JSON file '{input_file}': {e}")

        if not all_evaluations:
            print(f"  -> ⚠️ No data found across all input files. Aborting report generation.")
            return

        # Convert the consolidated list of dicts into a single DataFrame
        # This df_full now contains the new 'eval_model' column
        df_full = pd.DataFrame(all_evaluations)

        # --- STEP 2: Pre-process and Pivot for Summary ---

        # 🔑 FIX 3: Add 'eval_model' to the columns to keep
        summary_cols = ['fileName', 'plotTitle', 'finalScore', 'eval_model']
        df_summary_base = df_full[summary_cols].copy()

        # 🔑 FIX 4: Use a new regex to extract 'gen_model' from 'fileName'
        # The 'eval_model' column already exists and is correct.
        # This regex captures everything after the first underscore and before '.json'
        df_summary_base['gen_model'] = df_summary_base['fileName'].str.extract(
            r'[^_]+_(.+)\.json$', expand=False
        )

        # Fallback for any regex misses
        df_summary_base['gen_model'] = df_summary_base['gen_model'].fillna(
            df_summary_base['fileName'].str.replace('.json', '', regex=False)
        )

        # Ensure the score column is numeric before aggregation
        df_summary_base['finalScore'] = pd.to_numeric(df_summary_base['finalScore'], errors='coerce').fillna(0)

        # Pivot to get evaluation models as columns
        pivot_df = df_summary_base.pivot_table(
            index=['gen_model', 'plotTitle'],
            columns='eval_model',  # This will now correctly use 'gemini', 'gpt', etc.
            values='finalScore',
            aggfunc='first'
        ).reset_index()

        # Clean up columns and prepare for final summary
        pivot_df.rename(columns={'gen_model': 'Generation Model', 'plotTitle': 'Plot Title'}, inplace=True)
        pivot_df.columns.name = None

        # --- STEP 3: Calculate Total Score and Apply Relative Grading ---
        # 'score_cols' will now correctly be ['gemini', 'gpt', 'llama', 'qwen']
        score_cols = [col for col in pivot_df.columns if col not in ['Generation Model', 'Plot Title']]

        # This will now work as intended
        if not score_cols:
            print("  -> ⚠️ No score columns found after pivot. Cannot calculate total score.")
            pivot_df['totalFinalScore'] = 0.0
        else:
            pivot_df['totalFinalScore'] = pivot_df[score_cols].sum(axis=1).round(2)

        # Apply relative grading on the totalFinalScore
        summary_final_df = self._apply_relative_grading(pivot_df)

        # Reorder columns for the final Summary sheet
        summary_cols_order = ['Generation Model', 'Plot Title', 'totalFinalScore', 'Relative Grade',
                              'Grade Point'] + score_cols
        # Filter for columns that actually exist, in case one was empty
        summary_cols_order = [col for col in summary_cols_order if col in summary_final_df.columns]
        summary_final_df = summary_final_df[summary_cols_order]

        # --- STEP 4: Prepare Individual DataFrames for Sheets (based on EVAL model) ---
        # 🔑 FIX 5: This logic is now much simpler and more robust
        eval_models = df_full['eval_model'].unique()
        individual_dfs: Dict[str, pd.DataFrame] = {}
        for model in eval_models:
            # Filter rows for the current evaluation model
            model_df = df_full[df_full['eval_model'] == model].copy()
            # Drop the intermediate model column
            model_df.drop(columns=['eval_model'], errors='ignore', inplace=True)
            individual_dfs[model] = model_df

        # --- STEP 5: Save to Excel ---
        try:
            os.makedirs(os.path.dirname(output_excel), exist_ok=True)
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                # Save individual reports (one sheet per evaluation model)
                for model, df in individual_dfs.items():
                    if df.empty:
                        print(f"  -> ⚠️ Skipping empty sheet for model: '{model}'")
                        continue
                    # Sheet name limited to 31 chars
                    sheet_name = str(model)[:31].replace('-', '_').replace('.', '_')
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"  -> Wrote sheet: '{sheet_name}' ({model})")

                # Save the final summary
                if not summary_final_df.empty:
                    summary_final_df.to_excel(writer, sheet_name='Final_Summary', index=False)
                    print("  -> Wrote sheet: 'Final_Summary' with aggregated scores and relative grading.")
                else:
                    print("  -> ⚠️ Skipping empty 'Final_Summary' sheet.")

            print(f"  -> ✅ Success! Consolidated Excel report saved to '{output_excel}'")
        except Exception as e:
            print(f"  -> ❌ Error saving Excel file for job '{job_name}': {e}")

        # --- STEP 6: Save to JSON ---
        if output_json:
            try:
                # Convert the final summary DataFrame to a dictionary
                final_summary_data = summary_final_df.to_dict('records')

                output_data = {
                    "reportDescription": "Summary of generation models graded by multiple evaluation models.",
                    "gradedSummaryByGenerationModel": final_summary_data
                }

                os.makedirs(os.path.dirname(output_json), exist_ok=True)
                JsonUtils.save_json_to_file(output_data, output_json)
                print(f"  -> ✅ Success! Summary JSON saved to '{output_json}'")
            except Exception as e:
                print(f"  -> ❌ Error saving JSON file: {e}")