import numpy as np
from sklearn.decomposition import LatentDirichletAllocation

from nikhil.amsha.topic_modelling.base_topic_modeler import BaseTopicModeler


class LDATopicModeler(BaseTopicModeler):

    def __init__(self, n_components=10, random_state=42, **kwargs):
        super().__init__(n_components=n_components, random_state=random_state, **kwargs)
        self.model = LatentDirichletAllocation(
            n_components=self.n_components,
            random_state=self.random_state,
            **self.kwargs
        )

    def _fit_model(self, data_matrix, original_documents):
        if data_matrix is None or not hasattr(data_matrix, 'shape'):
            raise TypeError("data_matrix (TF-IDF matrix) is required for LDA.")
        self.model.fit(data_matrix)

    def _get_topics_terms_impl(self, top_n_words):
        if self.feature_names is None:
            raise RuntimeError("feature_names are missing. Fit the model with feature_names.")

        topic_words = {}
        for topic_idx, topic in enumerate(self.model.components_):
            top_features_ind = topic.argsort()[:-top_n_words - 1:-1]
            topic_words[topic_idx] = [(self.feature_names[i], topic[i]) for i in top_features_ind]
        return topic_words

    def _get_document_assignments_impl(self, data_matrix, original_documents):
        if data_matrix is None:
            raise ValueError("data_matrix is required for LDA document assignments.")
        doc_topic_probs = self.model.transform(data_matrix)
        return [np.argmax(doc_probs) for doc_probs in doc_topic_probs]