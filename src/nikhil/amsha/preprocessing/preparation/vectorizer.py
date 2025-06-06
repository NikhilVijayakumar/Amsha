from sklearn.feature_extraction.text import TfidfVectorizer


class Vectorizer:

    def __init__(self, min_df=2, max_df=0.9, max_features=1000):
        self.tfidf_vectorizer = TfidfVectorizer(
            min_df=min_df,
            max_df=max_df,
            max_features=max_features
        )
        self.feature_names = None  # To store the vocabulary words after fitting

    def fit(self, preprocessed_documents_tokens):
        joined_texts = [" ".join(tokens) for tokens in preprocessed_documents_tokens]

        self.tfidf_vectorizer.fit(joined_texts)
        self.feature_names = self.tfidf_vectorizer.get_feature_names_out()

        print(f"Vectorizer fitted. Vocabulary size: {len(self.feature_names)}")
        return self

    def transform(self, preprocessed_documents_tokens):
        if self.feature_names is None:
            raise RuntimeError("Vectorizer not fitted. Call .fit() before .transform().")

        joined_texts = [" ".join(tokens) for tokens in preprocessed_documents_tokens]
        tfidf_matrix = self.tfidf_vectorizer.transform(joined_texts)

        print(f"Documents transformed. TF-IDF matrix shape: {tfidf_matrix.shape}")
        return tfidf_matrix

    def fit_transform(self, preprocessed_documents_tokens):
        joined_texts = [" ".join(tokens) for tokens in preprocessed_documents_tokens]
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(joined_texts)
        self.feature_names = self.tfidf_vectorizer.get_feature_names_out()

        print(f"Vectorizer fitted and transformed. Vocabulary size: {len(self.feature_names)}")
        print(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
        return tfidf_matrix

    def get_feature_names(self):
        if self.feature_names is None:
            raise RuntimeError("Vectorizer not fitted. Call .fit() or .fit_transform() first.")
        return self.feature_names


