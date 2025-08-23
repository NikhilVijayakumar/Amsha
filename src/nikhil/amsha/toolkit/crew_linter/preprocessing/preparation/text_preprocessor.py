# src/nikhil/amsha/toolkit/crew_linter/preprocessing/preparation/text_preprocessor.py
import nltk
import string
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

from nikhil.amsha.toolkit.crew_linter.exceptions.missing_nltk_data_exception import MissingNLTKDataException
from nikhil.amsha.toolkit.crew_linter.preprocessing.preparation.vectorizer import Vectorizer


class TextPreprocessor:
    REQUIRED_NLTK_DATA = {
        'stopwords': 'corpora/stopwords',
        'wordnet': 'corpora/wordnet',
        'punkt': 'tokenizers/punkt'
    }

    def __init__(self, custom_stop_words=None):
        self._check_nltk_data()

        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

        if custom_stop_words:
            self.stop_words.update(set(custom_stop_words))

        self.punctuation_table = str.maketrans('', '', string.punctuation)

    def _check_nltk_data(self):
        missing_resources = []
        for resource_name, path in self.REQUIRED_NLTK_DATA.items():
            try:
                nltk.data.find(path)
            except LookupError:
                missing_resources.append(resource_name)

        if missing_resources:
            raise MissingNLTKDataException(
                f"Missing NLTK data: {', '.join(missing_resources)}. "
                "Please download them using: TextPreprocessor.download_required_data()"
            )

    @staticmethod
    def download_required_data():
        print("Checking and downloading required NLTK data...")
        downloaded_any = False
        for resource_name, path in TextPreprocessor.REQUIRED_NLTK_DATA.items():
            try:
                nltk.data.find(path)
                print(f"'{resource_name}' data already present.")
            except LookupError:
                print(f"Downloading '{resource_name}' data...")
                nltk.download(resource_name)
                downloaded_any = True
        if not downloaded_any:
            print("All required NLTK data is already downloaded.")
        print("NLTK data check complete.")

    def preprocess_text(self, text):
        if not isinstance(text, str):
            text = str(text)

        text = text.lower()
        text = text.translate(self.punctuation_table)
        tokens = word_tokenize(text)

        cleaned_tokens = []
        for token in tokens:
            if token.isalpha() and token not in self.stop_words:
                lemmatized_token = self.lemmatizer.lemmatize(token)
                cleaned_tokens.append(lemmatized_token)
        return cleaned_tokens

    def preprocess_documents(self, list_of_texts):
        return [self.preprocess_text(text) for text in list_of_texts]

    def extract_keywords(self, text, top_n=5):
        """
        Cleans the text and extracts the top N keywords using the custom Vectorizer (TF-IDF).
        """
        tokens = self.preprocess_text(text)
        if not tokens:
            return []

        # Use our custom Vectorizer
        vectorizer = Vectorizer(min_df=1, max_df=1.0, max_features=None)
        tfidf_matrix = vectorizer.fit_transform([tokens])  # passing list of token lists

        feature_names = vectorizer.get_feature_names()
        scores = tfidf_matrix.toarray()[0]

        top_indices = np.argsort(scores)[-top_n:][::-1]
        return [feature_names[i] for i in top_indices if scores[i] > 0]

    def extract_topics(self, text, num_topics=2, num_words=4):
        """
        Cleans the text and extracts topics using LDA.
        """
        tokens = self.preprocess_text(text)
        if not tokens:
            return []

        doc = " ".join(tokens)

        count_vectorizer = CountVectorizer()
        count_matrix = count_vectorizer.fit_transform([doc])

        lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
        lda.fit(count_matrix)

        feature_names = count_vectorizer.get_feature_names_out()
        topics = []
        for topic_component in lda.components_:
            top_indices = topic_component.argsort()[:-num_words - 1:-1]
            topics.append([feature_names[i] for i in top_indices])

        return topics
