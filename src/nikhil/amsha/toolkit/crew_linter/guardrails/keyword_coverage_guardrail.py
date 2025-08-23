# src/nikhil/amsha/toolkit/crew_linter/guardrails/keyword_coverage_guardrail.py
from typing import Optional

from nikhil.amsha.toolkit.crew_linter.domain.models.keyword_coverage_data import KeywordCoverageInput, KeywordCoverageResult


class KeywordCoverageGuardrail:
    def __init__(self, data: KeywordCoverageInput):
        self.data = data
        self.result: Optional[KeywordCoverageResult] = None


    def check(self):
        text_lower = self.data.text.lower()

        present = [keyword for keyword in self.data.keywords if keyword.lower() in text_lower]
        missing = [keyword for keyword in self.data.keywords if keyword.lower() not in text_lower]

        num_keywords = len(self.data.keywords)
        num_present = len(present)
        coverage_ratio = num_present / num_keywords if num_keywords > 0 else 0.0

        self.result = KeywordCoverageResult(
            all_keywords_present=len(missing) == 0,
            missing_keywords=missing,
            present_keywords=present,
            coverage_ratio=coverage_ratio
        )
