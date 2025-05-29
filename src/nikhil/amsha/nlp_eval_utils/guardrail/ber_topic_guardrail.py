from typing import Optional

from bertopic import BERTopic

from nikhil.amsha.nlp_eval_utils.models.ber_topic_data import BERTopicInput, BERTopicResult


class BERTopicGuardrail:

    def __init__(self, data: BERTopicInput):
        self.data = data
        self.result:Optional[BERTopicResult] = None

    def check(self):
        model = BERTopic(n_gram_range=(1, 2), top_n_words=self.data.top_n_words)
        topics, probs = model.fit_transform(self.data.texts)
        topic_info = model.get_topic_info()

        # Generate topic labels if not set
        if not hasattr(model, 'topic_names'):
            model.generate_topic_labels()

        extracted_topics = {}
        for _, row in topic_info[topic_info.Topic != -1].iterrows():  # Skip outliers
            topic_num = row.Topic
            topic_words = model.get_topic(topic_num)
            if topic_words:
                topic_name = model.topic_labels_[topic_num] if hasattr(model, 'topic_labels_') else f"Topic {topic_num}"
                topic_words_list = [word for word, _ in topic_words]
                extracted_topics[topic_num] = (topic_name, topic_words_list)

        similarity_scores = []
        for topic_num, (_, words) in extracted_topics.items():
            overlap = len(set(words) & set([kw.lower() for kw in self.data.reference_topics]))
            score = overlap / len(self.data.reference_topics) if self.data.reference_topics else 0.0
            similarity_scores.append(score)

        overall_alignment = bool(similarity_scores) and all(score >= self.data.similarity_threshold for score in similarity_scores)

        self.result = BERTopicResult(
            extracted_topics=extracted_topics,
            topic_similarity_scores=similarity_scores,
            overall_alignment=overall_alignment
        )


