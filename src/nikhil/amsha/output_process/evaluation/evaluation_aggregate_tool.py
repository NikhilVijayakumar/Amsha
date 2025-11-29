import os
from typing import Dict, Any, List

import numpy as np
import pandas as pd
from nikhil.amsha.utils.json_utils import JsonUtils
from nikhil.amsha.utils.yaml_utils import YamlUtils


class EvaluationAggregationTool:
    """
    Aggregates multiple evaluation JSON files, applies a relative grading based on
    normal distribution, and calculates an overall CGPA.
    """

    def __init__(self, config_path: str,score_summary="scoreSummary",title="plot_title"):
        self.config = YamlUtils.yaml_safe_load(config_path)
        self.score_summary = score_summary
        self.title = title

    def run(self):
        print("🚀 Starting evaluation aggregation process...")
        for job_config in self.config.get('aggregation_jobs', []):
            self._process_job(job_config)
        print("\n🎉 All aggregation jobs are complete.")

    def _process_job(self, job_config: Dict[str, Any]):
        job_name = job_config.get('name', 'Unnamed Aggregation Job')
        print(f"\n--- Running Job: {job_name} ---")

        # --- 1. Load All Data Files ---
        input_dir = job_config.get('input_directory')
        all_evaluations = self._load_all_evaluations(input_dir)
        if not all_evaluations:
            print("❌ Critical Error: No valid evaluation files found. Skipping job.")
            return

        # --- 2. Perform Relative Grading ---
        print("  -> Applying relative grading...")
        grading_scale = job_config.get('grading_scale', {})
        df = pd.DataFrame(all_evaluations)
        df_graded = self._apply_relative_grading(df, grading_scale)

        # --- 3. Calculate Final Summary ---
        final_cgpa = round(df_graded['gradePoint'].mean(), 2)
        mean_score = round(df_graded['finalScorePercentage'].mean(), 2)
        std_dev = round(df_graded['finalScorePercentage'].std(), 2)

        summary_stats = {
            'totalFilesProcessed': len(df_graded),
            'overallCGPA': final_cgpa,
            'meanScorePercentage': mean_score,
            'standardDeviation': std_dev
        }
        print(f"  -> Overall CGPA: {final_cgpa}")

        # --- 4. Save Outputs ---
        graded_evaluations = df_graded.to_dict(orient='records')
        final_output = {
            'aggregationSummary': summary_stats,
            'gradedEvaluations': graded_evaluations
        }

        JsonUtils.save_json_to_file(final_output, job_config.get('output_json_file'))
        self._save_to_excel(df_graded, summary_stats, job_config.get('output_excel_file'))

        print(f"--- Job '{job_name}' complete. ---")

    def _load_all_evaluations(self, input_dir: str) -> List[Dict[str, Any]]:
        evaluations = []
        if not os.path.isdir(input_dir):
            print(f"  -> ❌ Error: Input directory '{input_dir}' not found.")
            return []

        for filename in os.listdir(input_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(input_dir, filename)
                data = JsonUtils.load_json_from_file(filepath)
                if self.score_summary in data and self.title in data:
                    record = {
                        'fileName': filename,
                        self.title: data.get(self.title),
                        **data.get(self.score_summary, {})
                    }
                    evaluations.append(record)
        print(f"  -> Found and loaded {len(evaluations)} evaluation files.")
        return evaluations

    def _apply_relative_grading(self, df: pd.DataFrame, grading_scale: Dict[str, float]) -> pd.DataFrame:
        scores = df['finalScorePercentage']
        mean = np.mean(scores)
        std = np.std(scores)

        def get_grade(score):
            if score > mean + std:
                return 'A'
            elif score > mean:
                return 'B'
            elif score > mean - std:
                return 'C'
            else:
                return 'D'

        df['relativeGrade'] = scores.apply(get_grade)
        df['gradePoint'] = df['relativeGrade'].map(grading_scale)

        # --- NEW LINE ADDED ---
        # Calculate the final score by multiplying the grade point by the percentage
        df['finalScore'] = round(df['gradePoint'] * df['finalScorePercentage'], 2)

        return df

    def _save_to_excel(self, df: pd.DataFrame, summary: Dict[str, Any], output_filename: str):
        if not output_filename:
            return
        try:
            summary_df = pd.DataFrame([summary])

            # --- MODIFIED LINE: Added 'finalScore' to the list of columns to ensure order ---
            excel_df = df[
                ['fileName', self.title, 'finalScorePercentage', 'relativeGrade', 'gradePoint', 'finalScore']]

            with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
                excel_df.to_excel(writer, sheet_name='Relative Grade Details', index=False)
                summary_df.to_excel(writer, sheet_name='Overall Summary', index=False)
            print(f"  -> ✅ Successfully saved aggregated Excel summary to: {output_filename}")
        except Exception as e:
            print(f"  -> ❌ Error saving aggregated Excel file: {e}")



