from bertopic import BERTopic

from nikhil.amsha.topic_modelling.base_topic_modeler import BaseTopicModeler


class BERTopicModeler(BaseTopicModeler):

    def __init__(self, n_components='auto', random_state=42, **kwargs):
        nr_topics = kwargs.pop('nr_topics', n_components)

        super().__init__(n_components=n_components, random_state=random_state,
                         **kwargs)  # Pass n_components for potential future consistency

        # Default embedding_model and language if not provided in kwargs
        embedding_model = self.kwargs.pop('embedding_model', 'all-MiniLM-L6-v2')
        language = self.kwargs.pop('language', 'english')

        self.model = BERTopic(
            embedding_model=embedding_model,
            language=language,
            nr_topics=nr_topics,  # Use nr_topics here
            # Pass any other BERTopic specific kwargs
            **self.kwargs
        )
        self.topics = None  # To store topics generated by BERTopic's fit_transform
        self.probs = None  # To store probabilities generated by BERTopic's fit_transform

    def _fit_model(self, data_matrix, original_documents):
        if not original_documents or not isinstance(original_documents, list) or not all(
                isinstance(d, str) for d in original_documents):
            raise ValueError("original_documents (list of strings) are required for BERTopic.")

        self.topics, self.probs = self.model.fit_transform(original_documents)
        print(f"Number of topics discovered by BERTopic: {len(self.model.get_topics()) - 1}")  # -1 for outlier topic

    def _get_topics_terms_impl(self, top_n_words):
        topic_terms = self.model.get_topics(full=True)
        filtered_topic_terms = {
            topic_id: [(term, score) for term, score in terms_scores if topic_id != -1]
            for topic_id, terms_scores in topic_terms.items() if topic_id != -1
        }
        for topic_id in filtered_topic_terms:
            filtered_topic_terms[topic_id] = filtered_topic_terms[topic_id][:top_n_words]
        return filtered_topic_terms

    def _get_document_assignments_impl(self, data_matrix, original_documents):
        # BERTopic's fit_transform already provides this
        if self.topics is None or self.probs is None:
            raise RuntimeError("BERTopic model was not fitted to retrieve assignments.")
        return self.topics, self.probs  # Return topics and probabilities

