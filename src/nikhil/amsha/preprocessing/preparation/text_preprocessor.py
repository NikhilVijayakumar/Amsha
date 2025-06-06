import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import string

from nikhil.amsha.exception.missing_nltk_data_exception import MissingNLTKDataException


class TextPreprocessor:
    REQUIRED_NLTK_DATA = {
        'stopwords': 'corpora/stopwords',
        'wordnet': 'corpora/wordnet',
        'punkt': 'tokenizers/punkt'
    }

    def __init__(self, custom_stop_words=None):
        # Check for NLTK data before initializing components that rely on it
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
            if token.isalpha():
                if token not in self.stop_words:
                    lemmatized_token = self.lemmatizer.lemmatize(token)
                    cleaned_tokens.append(lemmatized_token)
        return cleaned_tokens

    def preprocess_documents(self, list_of_texts):
        processed_documents = [self.preprocess_text(text) for text in list_of_texts]
        return processed_documents
