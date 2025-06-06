import warnings
from abc import ABC, abstractmethod  # For Abstract Base Classes

class BaseTopicModeler(ABC):

    def __init__(self, n_components=10, random_state=42, **kwargs):
        self.n_components = n_components
        self.random_state = random_state
        self.model = None  # Actual model instance (LDA, NMF, BERTopic)
        self.feature_names = None  # Vocabulary for LDA/NMF
        self.kwargs = kwargs  # Store additional model-specific parameters

    def fit(self, data_matrix=None, feature_names=None, original_documents=None):
        self.feature_names = feature_names  # Store feature names if provided
        print(f"Fitting {self.__class__.__name__} model...")
        self._fit_model(data_matrix, original_documents)
        print(f"{self.__class__.__name__} model fitted.")

    @abstractmethod
    def _fit_model(self, data_matrix, original_documents):
        pass

    def get_topics_terms(self, top_n_words=10):
        if self.model is None:
            raise RuntimeError("Model not fitted. Call .fit() first.")
        return self._get_topics_terms_impl(top_n_words)

    @abstractmethod
    def _get_topics_terms_impl(self, top_n_words):
        pass

    def get_document_topic_assignments(self, data_matrix=None, original_documents=None):
        if self.model is None:
            raise RuntimeError("Model not fitted. Call .fit() first.")
        return self._get_document_assignments_impl(data_matrix, original_documents)

    @abstractmethod
    def _get_document_assignments_impl(self, data_matrix, original_documents):
        pass