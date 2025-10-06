# evaluator.py

import os
from typing import Dict, Any, List, Tuple, Union

from nikhil.amsha.utils.json_utils import JsonUtils
from nikhil.amsha.utils.yaml_utils import YamlUtils


class EvaluationProcessor:
    """
    A class to process and score LLM evaluation files based on a YAML configuration.
    """

    def __init__(self, config_path: str):
        """
        Initializes the processor by loading the configuration file.
        Args:
            config_path (str): The path to the config.yaml file.
        """
        print(f"Loading configuration from: {config_path}")
        self.config = YamlUtils.yaml_safe_load(config_path)

    @staticmethod
    def _get_score_description(final_score: float, ranges: List[Dict[str, Any]]) -> Tuple[str, str]:
        """Finds the descriptive range for a given score."""
        for score_range in ranges:
            min_val, max_val = score_range["scoreRange"]
            if min_val <= final_score <= max_val:
                return score_range["description"], f"{min_val}-{max_val}"
        return "Not Applicable", "Score is outside all defined ranges."

    def _calculate_evaluation_score(
            self,
            evaluation_result: Dict[str, Any],
            evaluation_rubric: Dict[str, Any],
            rubric_metrics_key: str,
            result_evaluation_key: str
    ) -> Dict[str, Any]:
        """Calculates the weighted score for an LLM evaluation using explicit parameters."""
        metrics_list = evaluation_rubric.get(rubric_metrics_key, [])
        rubric_metrics_map = {metric['name']: metric for metric in metrics_list}

        total_weighted_score, max_possible_score = 0, 0
        for metric in metrics_list:
            max_possible_score += metric.get('scoringRange', [0, 0])[1] * metric.get('weight', 0)

        updated_evaluations = []
        for item in evaluation_result.get(result_evaluation_key, []):
            metric_name = item.get('metricName')
            raw_score = item.get('score', 0)
            if metric_name in rubric_metrics_map:
                weight = rubric_metrics_map[metric_name].get('weight', 0)
                item['weightedScore'] = raw_score * weight
                total_weighted_score += item['weightedScore']
            else:
                print(f"  -> ⚠️ Warning: Metric '{metric_name}' found in result but not in rubric. Ignoring.")
                item['weightedScore'] = 0
            updated_evaluations.append(item)

        final_percentage = (total_weighted_score / max_possible_score) * 100 if max_possible_score > 0 else 0

        percentage_based_ranges = [
            {"scoreRange": [0.0, 64.99], "description": "Weak"},
            {"scoreRange": [65.0, 74.99], "description": "Moderate"},
            {"scoreRange": [75.0, 90.99], "description": "Strong"},
            {"scoreRange": [91.0, 100.0], "description": "Excellent"}
        ]
        description, range_str = self._get_score_description(round(final_percentage, 2), percentage_based_ranges)

        updated_result = evaluation_result.copy()
        updated_result[result_evaluation_key] = updated_evaluations
        updated_result['scoreSummary'] = {
            "totalWeightedScore": round(total_weighted_score, 2),
            "maxPossibleScore": round(max_possible_score, 2),
            "finalScorePercentage": round(final_percentage, 2),
            "tierDescription": description,
            "tierScoreRange": range_str,
        }
        return updated_result

    def _process_job(self, job_config: Dict[str, Any]):
        """Processes a single evaluation job from the configuration."""
        job_name = job_config.get('name', 'Unnamed Job')
        print(f"\n--- Running Job: {job_name} ---")

        rubric = JsonUtils.load_json_from_file(job_config['rubric_path'])
        if not rubric:
            print(f"❌ Critical Error: Could not load rubric for job '{job_name}'. Skipping job.")
            return

        input_dir = job_config['input_directory']
        output_dir = job_config['output_directory']

        if not os.path.isdir(input_dir):
            print(f"❌ Error: Input directory '{input_dir}' does not exist for job '{job_name}'. Skipping job.")
            return

        processed_count = 0
        for filename in os.listdir(input_dir):
            if filename.endswith('.json'):
                input_file_path = os.path.join(input_dir, filename)
                print(f"  -> Processing file: {filename}")
                evaluation_data = JsonUtils.load_json_from_file(input_file_path)

                if evaluation_data:
                    options = job_config.get('options', {})
                    final_result = self._calculate_evaluation_score(
                        evaluation_result=evaluation_data,
                        evaluation_rubric=rubric,
                        rubric_metrics_key=options.get('rubric_metrics_key', 'metrics'),
                        result_evaluation_key=options.get('result_evaluation_key', 'evaluation')
                    )

                    output_file_path = os.path.join(output_dir, filename)
                    if JsonUtils.save_json_to_file(final_result, output_file_path):
                        print(f"  -> ✅ Saved result to: {output_file_path}")
                        processed_count += 1

        print(f"--- Job '{job_name}' complete. Processed {processed_count} files. ---")

    def run_evaluations(self):
        """Runs all evaluation jobs defined in the config file."""
        print("🚀 Starting evaluation process...")
        for job_config in self.config.get('evaluations', []):
            self._process_job(job_config)
        print("\n🎉 All evaluation jobs are complete.")
