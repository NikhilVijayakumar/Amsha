from typing import List

import nltk
from gensim.corpora import Dictionary
from gensim.models import LdaModel
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from nikhil.amsha.nlp_eval_utils.exception.missing_nltk_data_exception import MissingNLTKDataException
from nikhil.amsha.nlp_eval_utils.models.lda_topic_data import LdaTopicResult, LdaTopicInput


class LdaTopicGuardrail:
    def __init__(self):
        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            raise MissingNLTKDataException(
                "NLTK 'stopwords' data not found. Please download it using: import nltk; nltk.download('stopwords')")
        try:
            word_tokenize("test")  # Trigger punkt download check implicitly
        except LookupError:
            raise MissingNLTKDataException(
                "NLTK 'punkt' data not found. Please download it using: import nltk; nltk.download('punkt')")

    @staticmethod
    def download_model():
        resources = {
            'corpora/stopwords': 'stopwords',
            'tokenizers/punkt': 'punkt'
        }

        for path, resource in resources.items():
            try:
                nltk.data.find(path)
            except LookupError:
                nltk.download(resource)

    def _preprocess(self, text: str) -> List[str]:
        return [word.lower() for word in word_tokenize(text) if word.isalpha() and word.lower() not in self.stop_words]

    def check(self, data: LdaTopicInput) -> LdaTopicResult:
        processed_texts = [self._preprocess(text) for text in data.texts]
        dictionary = Dictionary(processed_texts)
        corpus = [dictionary.doc2bow(text) for text in processed_texts]

        lda_model = LdaModel(corpus, num_topics=data.num_topics, id2word=dictionary, random_state=42)
        extracted_topics = lda_model.show_topics(num_words=10, formatted=False)

        alignment_scores = []
        for topic_id, terms in extracted_topics:
            topic_keywords = [term for term, prob in terms]
            # Simple keyword overlap for now - can be made more sophisticated
            overlap = len(set(topic_keywords) & set([kw.lower() for kw in data.reference_topics]))
            score = overlap / len(data.reference_topics) if data.reference_topics else 0.0
            alignment_scores.append(score)

        overall_alignment = all(score >= data.similarity_threshold for score in alignment_scores)

        formatted_extracted_topics = [(topic_id, [(dictionary[int(id_)], prob) for id_, prob in terms]) for topic_id, terms in extracted_topics]

        return LdaTopicResult(
            extracted_topics=formatted_extracted_topics,
            topic_alignment_scores=alignment_scores,
            overall_alignment=overall_alignment
        )

