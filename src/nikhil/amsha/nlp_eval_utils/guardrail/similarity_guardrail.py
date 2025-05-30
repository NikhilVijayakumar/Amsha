from typing import Optional

from fuzzywuzzy import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from nikhil.amsha.nlp_eval_utils.models.similarity_data import SimilarityInput, SimilarityResult, SimilarityConstants


class SimilarityGuardrail:
    def __init__(self, data: SimilarityInput):
        self.data = data
        self.result:Optional[SimilarityResult] = None

    def check_fuzzy(self) :
        ratio = fuzz.ratio(self.data.source, self.data.target)
        inference_ratio = SimilarityConstants.SIMILAR.value if ratio >= self.data.ratio else SimilarityConstants.NOT_SIMILAR.value
        self.result.inference_ratio = (ratio, inference_ratio)

        partial_ratio = fuzz.partial_ratio(self.data.source, self.data.target)
        inference_partial = SimilarityConstants.POTENTIALLY_RELATED.value  if partial_ratio >= self.data.partial_ratio else SimilarityConstants.UNLIKELY_RELATED.value
        self.result.inference_partial = (partial_ratio, inference_partial)

        token_sort_ratio = fuzz.token_sort_ratio(self.data.source, self.data.target)
        inference_token_sort = SimilarityConstants.ANAGRAMMATIC_MATCH.value  if token_sort_ratio >=self.data.token_sort_ratio else SimilarityConstants.DIFFERENT_TOKEN_ORDER.value
        self.result.inference_token_sort = (token_sort_ratio, inference_token_sort)



    def calculate_cosine_similarity(self):
        if self.data.source_text is not None and self.data.target_text is not None:
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform([self.data.source_text, self.data.target_text])
            similarity_score = cosine_similarity(vectors[0], vectors[1])[0][0]
            inference_cosine = SimilarityConstants.SEMANTICALLY_SIMILAR.value  if similarity_score >= self.data.threshold_cosine else SimilarityConstants.SEMANTICALLY_DIFFERENT.value
            self.result.inference_cosine = similarity_score, inference_cosine


