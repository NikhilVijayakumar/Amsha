# Topic Modelers Documentation: Discovering Themes in Text Data
This documentation provides a comprehensive overview of a modular framework for topic modeling, designed to uncover hidden thematic structures within collections of documents. It introduces an abstract base class `BaseTopicModeler` that defines a standardized interface for various topic modeling algorithms (LDA, NMF, BERTopic) and their concrete implementations.

---

## 1. BaseTopicModeler: Abstract Base Class for Topic Modeling

### **Purpose**
The `BaseTopicModeler` serves as an abstract base class (ABC) to establish a unified interface for different topic modeling algorithms. It defines common methods for fitting models, extracting topics, and assigning documents to topics, ensuring consistency across implementations like LDA, NMF, or BERTopic.

### **Key Components**
- `n_components`: (Default: 10) Specifies the number of topics to extract. For BERTopic, this is often handled via `nr_topics` or set to `'auto'`.
- `random_state`: (Default: 42) Ensures reproducibility for stochastic algorithms like LDA and NMF.
- `model`: Holds the underlying topic model instance (e.g., `LatentDirichletAllocation`, `NMF`, `BERTopic`). Initialized as `None` during initialization.
- `feature_names`: Stores the vocabulary of words corresponding to input features, crucial for interpreting topics in LDA/NMF.
- `kwargs`: A dictionary to pass model-specific parameters to the underlying algorithm.

### **Workflow**

#### 1. **Initialization (`__init__`)**
- Initializes common parameters like `n_components`, `random_state`.
- Sets `self.model = None` until explicitly fitted.
- Stores additional keyword arguments for passing to specific topic model constructors.

#### 2. **Fitting the Model (`fit`)**
- Accepts `data_matrix` (e.g., TF-IDF matrix) and/or `original_documents` (raw text strings for BERTopic).
- Stores `feature_names` if provided (essential for LDA/NMF topic interpretation).
- Calls `_fit_model`, an abstract method implemented by subclasses to train the specific model.

#### 3. **Extracting Topic Terms (`get_topics_terms`)**
- Checks that the model is fitted (`self.model is not None`).
- Invokes `_get_topics_terms_impl`, a subclass-specific implementation, to extract top words per topic using `top_n_words`.

#### 4. **Assigning Documents to Topics (`get_document_topic_assignments`)**
- Validates that the model is fitted.
- Calls `_get_document_assignments_impl`, implemented by subclasses, to determine document-topic assignments.

### **Abstract Methods (Must Be Implemented by Subclasses)**
- `_fit_model(self, data_matrix, original_documents)`: Trains the specific topic model (e.g., `LDA.fit()`, `NMF.fit()`, `BERTopic.fit_transform()`).
- `_get_topics_terms_impl(self, top_n_words)`: Extracts and formats top terms for each topic.
- `_get_document_assignments_impl(self, data_matrix, original_documents)`: Assigns topics to documents based on the model's output.

### **Use Cases**
- Provides a blueprint for developing various topic modeling solutions under a unified API.
- Facilitates experimentation with different algorithms (LDA, NMF, BERTopic) without altering core logic.

---

## 2. LDATopicModeler: Topic Modeling with Latent Dirichlet Allocation

### **Purpose**
The `LDATopicModeler` implements topic modeling using **Latent Dirichlet Allocation (LDA)**, a probabilistic model that assumes documents are mixtures of topics, and each topic is a mixture of words. It excels at identifying broad themes in text corpora.

### **Key Components**
- **`LatentDirichletAllocation`**: Core LDA implementation from `sklearn.decomposition`.

### **Workflow**

#### 1. **Initialization (`__init__`)**
- Initializes `self.model` as a `LatentDirichletAllocation` instance with parameters like `n_components`, `random_state`, and any additional keyword arguments.

#### 2. **Fitting (`_fit_model`)**
- Requires a `data_matrix` (e.g., TF-IDF or CountVectorizer matrix).
- Calls `self.model.fit(data_matrix)` to train the LDA model, inferring topics and their word distributions.

#### 3. **Extracting Topics (`_get_topics_terms_impl`)**
- Uses `feature_names` to map word indices back to actual terms.
- Iterates through `self.model.components_`, extracting top `top_n_words` for each topic based on probabilities.
- Returns a dictionary: `{topic_id: [(word, score)]}`.

#### 4. **Document Assignments (`_get_document_assignments_impl`)**
- Uses `self.model.transform(data_matrix)` to compute document-topic probabilities.
- Returns the topic with the highest probability for each document (e.g., `[topic_id]`).

### **Use Cases**
- Discovering hidden themes in large text collections (news articles, research papers).
- Categorizing documents based on dominant topics.
- Building content recommendation systems.

### **Limitations**
- Requires bag-of-words or TF-IDF input (ignores word order).
- Topic coherence can be suboptimal with sparse/noisy data.
- `n_components` must be predefined, making optimal topic count selection challenging.

---

## 3. NMFTopicModeler: Topic Modeling with Non-Negative Matrix Factorization

### **Purpose**
The `NMFTopicModeler` implements topic modeling using **Non-Negative Matrix Factorization (NMF)**, a linear-algebraic technique that decomposes a document-term matrix into two matrices: one for document-topic distributions and another for topic-word weights. NMF is praised for producing more interpretable topics than LDA.

### **Key Components**
- **`NMF`**: Core implementation from `sklearn.decomposition`.

### **Workflow**

#### 1. **Initialization (`__init__`)**
- Initializes `self.model` as an `NMF` instance with parameters like `n_components`, `random_state`, and additional keyword arguments.

#### 2. **Fitting (`_fit_model`)**
- Requires a `data_matrix` (e.g., TF-IDF or CountVectorizer matrix).
- Calls `self.model.fit(data_matrix)` to train the NMF model.

#### 3. **Extracting Topics (`_get_topics_terms_impl`)**
- Uses `feature_names` to map word indices back to terms.
- Iterates through `self.model.components_`, extracting top `top_n_words` for each topic based on weights.
- Returns a dictionary: `{topic_id: [(word, score)]}`.

#### 4. **Document Assignments (`_get_document_assignments_impl`)**
- Uses `self.model.transform(data_matrix)` to compute document-topic weights.
- Returns the topic with the highest weight for each document (e.g., `[topic_id]`).

### **Use Cases**
- Interpretable topic discovery in text collections.
- Dimensionality reduction for text data.
- Applications requiring non-negative component analysis.

### **Limitations**
- Requires non-negative input (like TF-IDF or CountVectorizer).
- `n_components` must be predefined, making optimal selection challenging.
- Sensitive to sparse matrices; TF-IDF is typically used to mitigate this.

---

## 4. BERTopicModeler: Semantic Topic Modeling with BERT Embeddings

### **Purpose**
The `BERTopicModeler` implements topic modeling using **BERTopic**, a state-of-the-art technique leveraging Transformer-based models (like BERT) for semantic topic extraction. It clusters document embeddings and uses c-TF-IDF to generate coherent topics.

### **Key Components**
- **`BERTopic`**: Core implementation from the `bertopic` library.
- **`embedding_model`**: Pre-trained sentence transformer model (default: `'all-MiniLM-L6-v2'`).
- **`nr_topics`**: Specifies the number of topics or allows automatic reduction (`auto`).

### **Workflow**

#### 1. **Initialization (`__init__`)**
- Initializes `self.model` as a `BERTopic` instance with parameters like `nr_topics`, `embedding_model`, and language.
- Sets `self.topics` and `self.probs` to `None` for post-fitting storage.

#### 2. **Fitting (`_fit_model`)**
- Requires raw text documents (`original_documents`).
- Calls `self.model.fit_transform(original_documents)`:
  - Embeds documents using the specified model.
  - Clusters embeddings and computes c-TF-IDF for topic terms.
- Stores discovered topics in `self.topics` and their probabilities in `self.probs`.

#### 3. **Extracting Topics (`_get_topics_terms_impl`)**
- Uses `self.model.get_topics(full=True)` to retrieve semantic topic representations.
- Filters out outlier topics (ID `-1`) and truncates terms to `top_n_words`.
- Returns a dictionary: `{topic_id: [(term, score)]}`.

#### 4. **Document Assignments (`_get_document_assignments_impl`)**
- Returns precomputed `self.topics` and `self.probs` from the fitting process.
- Raises an error if the model is not yet fitted.

### **Use Cases**
- Coherent topic discovery in short texts (e.g., social media, reviews).
- Semantic clustering of documents with contextual relevance.
- Cross-lingual analysis using multilingual embedding models.

### **Limitations**
- Computationally intensive and memory-heavy due to embedding models.
- Performance depends on the quality of the embedding model for domain-specific data.
- Outlier topic (`-1`) may require manual filtering or interpretation.

---

## Summary Table: Topic Modeler Overview

| Method Name                        | Base Class       | Core Functionality                                      | Input (Expected Format)                     | Output Type                                  | Primary Use Case                                   |
|------------------------------------|------------------|---------------------------------------------------------|----------------------------------------------|-----------------------------------------------|----------------------------------------------------|
| `__init__`                         | `BaseTopicModeler` | Initializes model parameters and sets up internal model | `n_components`, `random_state`, `kwargs`     | None (configuration)                          | Setup and dependency management                    |
| `fit`                              | `BaseTopicModeler` | Orchestrates model training                             | `data_matrix` / `original_documents`         | `self` (fitted model instance)                | Training the topic model on a corpus               |
| `_fit_model`                       | Abstract         | Concrete model training logic                           | Varies by subclass                           | None                                          | Core model-specific fitting                        |
| `get_topics_terms`                 | `BaseTopicModeler` | Retrieves top terms for each topic                      | `top_n_words`                                | Dictionary: `{topic_id: [(term, score)]}`    | Interpreting discovered topics                     |
| `_get_topics_terms_impl`           | Abstract         | Concrete topic term extraction logic                    | `top_n_words`                                | Dictionary: `{topic_id: [(term, score)]}`    | Model-specific topic interpretation                |
| `get_document_topic_assignments`   | `BaseTopicModeler` | Retrieves document-topic assignments                     | `data_matrix` / `original_documents`         | List of topic IDs/probabilities               | Understanding document-topic relationships         |
| `_get_document_assignments_impl`   | Abstract         | Concrete document assignment logic                      | Varies by subclass                           | List of topic IDs/probabilities               | Model-specific document-topic mapping              |

---

## Export to Sheets

For exporting topic models or results to sheets:
- Use libraries like `pandas` to convert output dictionaries (e.g., topics, assignments) into structured tables.
- Ensure compatibility with tools like Google Sheets or Excel by handling sparse matrices and semantic terms appropriately.

---

## Best Practices for Implementation (Across All Topic Modelers)

### **1. Preprocessing**
- Always preprocess text using `TextPreprocessor` before vectorization (for LDA/NMF) or inputting into BERTopic.
- Clean raw data to improve model performance and topic coherence.

### **2. Vectorization Consistency (LDA/NMF)**
- Use the same `Vectorizer` instance that was fit on training data for consistent transformations.
- Pass `feature_names` from the vectorizer to the topic modeler during fitting for accurate term mapping.

### **3. Parameter Tuning**
- **`n_components / nr_topics`**: Critical parameter; experiment with values. Use metrics like perplexity or topic coherence (via libraries like `gensim`) to evaluate quality. For BERTopic, `'auto'` is often preferred.
- **`random_state`**: Always set for reproducibility, especially in stochastic algorithms (LDA/NMF).
- **`kwargs`**: Use to pass model-specific parameters (e.g., `max_iter`, `hdbscan_model` for BERTopic).

### **4. Topic Coherence Evaluation**
- After topic discovery, evaluate coherence using tools like `gensim.models.coherencemodel`.
- Human-in-the-loop review is essential for assigning meaningful names to topics.

### **5. Model Comparison**
- Experiment with LDA, NMF, and BERTopic to determine which model yields the most interpretable and useful results for your dataset and use case.

### **6. BERTopic Input Handling**
- Ensure `original_documents` (raw text strings) are passed directly to `_fit_model` for BERTopic. Avoid using a `data_matrix` for this model, as it operates on raw input.

---
