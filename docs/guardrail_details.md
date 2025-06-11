# Guardrail Documentation: Comprehensive Knowledge Base for Project Validation

This documentation provides an in-depth explanation of five distinct **guardrail classes** designed to validate and analyze different aspects of data processing pipelines. Each guardrail serves a specific purpose, leveraging algorithms from NLP (Natural Language Processing), graph theory, and topic modeling.

---

## 1. `SimilarityGuardrail`: Text Similarity Validation
### Purpose:
Verify the semantic and syntactic similarity between two pieces of text using multiple metrics to detect duplicates, paraphrasing, or misaligned content.

### Key Components:
- **Input (`SimilarityInput`)**: 
  - Two strings (`source`, `target`)
  - Threshold values for various similarity checks
- **Output (`SimilarityResult`)**:
  - Fuzzy matching scores and classifications
  - Cosine similarity for semantic analysis

### Workflow:
1. **Fuzzy String Matching**:
   - Uses the **Levenshtein ratio** to compare character-level differences between `source` and `target`.
   - A score ≥ threshold (`ratio`) classifies as "Similar", else "Not Similar".
   - **Partial Ratio**: Focuses on matching subsequences (e.g., "hello world" vs. "world hello").
   - **Token Sort Ratio**: Compares word-level similarity, ignoring order (anagrams).

2. **Semantic Analysis**:
   - Converts text into TF-IDF vectors using `TfidfVectorizer`.
   - Computes **cosine similarity** to measure semantic alignment.
   - Classifies as "Semantically Similar" if the score ≥ threshold (`threshold_cosine`).

### Use Cases:
- Duplicate detection in user inputs or documents
- Verifying paraphrased content (e.g., plagiarism checks)
- Ensuring consistency in data entries

### Limitations:
- Fuzzy metrics may not capture nuanced meaning
- Cosine similarity depends on TF-IDF's term weighting assumptions

---

## 2. `LdaTopicGuardrail`: Topic Alignment Validation with LDA
### Purpose:
Validate whether topics extracted from text data align with predefined reference topics using **Latent Dirichlet Allocation (LDA)**.

### Key Components:
- **Input (`LdaTopicInput`)**: 
  - List of texts to analyze
  - Reference topic keywords for comparison
  - Number of topics to extract (`num_topics`)
- **Output (`LdaTopicResult`)**:
  - Extracted topics with keyword weights
  - Alignment scores between extracted and reference topics

### Workflow:
1. **Text Preprocessing**:
   - Tokenizes and removes stopwords using NLTK.
   - Converts text into bag-of-words representations.

2. **Topic Modeling**:
   - Trains an LDA model to extract `num_topics` from the input texts.
   - Retrieves top keywords for each topic.

3. **Alignment Check**:
   - Compares extracted topic keywords with predefined reference topics.
   - Calculates overlap percentage as a similarity score.
   - Aggregates scores across all topics and flags whether all meet the threshold.

### Use Cases:
- Ensuring content adheres to specific themes (e.g., marketing campaigns)
- Validating domain-specific terminology in technical documents
- Monitoring topic consistency across datasets

### Limitations:
- LDA may struggle with ambiguous or highly varied texts
- Manual curation of reference topics is required

---

## 3. `BERTopicGuardrail`: Semantic Topic Analysis with BERT
### Purpose:
Perform advanced semantic topic modeling using **BERT embeddings**, comparing extracted topics against predefined reference concepts.

### Key Components:
- **Input (`BERTopicInput`)**: 
  - List of texts to analyze
  - Reference keywords for expected topics
  - `top_n_words`: Number of words per topic summary
- **Output (`BERTopicResult`)**:
  - Semantic topics with weighted keywords
  - Topic similarity scores and overall alignment

### Workflow:
1. **Model Initialization**:
   - Uses BERT-based embeddings to capture contextual meaning.
   - Extracts topics based on semantic clustering.

2. **Topic Comparison**:
   - Compares the most representative words of each extracted topic against reference keywords.
   - Calculates overlap percentage as similarity score.
   - Determines if all scores meet the threshold for alignment.

### Use Cases:
- Analyzing customer feedback for sentiment and theme detection
- Validating domain-specific knowledge in educational content
- Ensuring consistency across multilingual datasets

### Limitations:
- Requires access to pre-trained BERT models
- Computationally intensive for large text corpora

---

## 4. `KeywordCoverageGuardrail`: Keyword Presence Validation
### Purpose:
Ensure that a required set of keywords is fully or partially present in a given text.

### Key Components:
- **Input (`KeywordCoverageInput`)**: 
  - Target text to analyze
  - List of required keywords
- **Output (`KeywordCoverageResult`)**:
  - Boolean indicating if all keywords are present
  - Lists of missing and found keywords
  - Coverage ratio (percentage of keywords matched)

### Workflow:
1. **Case-insensitive Search**:
   - Converts text and keywords to lowercase for comparison.
   - Identifies which keywords appear in the text.

2. **Metrics Calculation**:
   - Computes how many keywords are present (`present_keywords`).
   - Calculates `coverage_ratio = (number of found keywords) / (total keywords)`.

### Use Cases:
- Validating compliance with required terminology (e.g., legal documents)
- Ensuring inclusion of brand-specific terms in marketing content
- Checking completeness of technical documentation

### Limitations:
- Does not account for context or intent, only presence
- Case sensitivity can be an issue if not handled explicitly

---

## 5. `NetworkXGuardrail`: Graph Structure Validation
### Purpose:
Analyze graph structures (directed/undirected) to validate connectivity, node isolation, and centrality metrics.

### Key Components:
- **Input (`GraphData`)**: 
  - List of edges defining relationships
  - Optional list of nodes
- **Output (`GraphAnalysisResult`)**:
  - Structural metrics like number of nodes/edges
  - Connectivity status (strongly/weakly connected)
  - Degree centrality for each node

### Workflow:
1. **Graph Construction**:
   - Creates a directed or undirected graph using NetworkX.
   - Adds nodes and edges from input data.

2. **Structural Analysis**:
   - Identifies isolated nodes (no connections).
   - Checks connectivity for directed graphs (strong/weak) vs undirected (connected/disconnected).
   - Computes degree centrality to identify key nodes.

### Use Cases:
- Validating network reliability in infrastructure systems
- Analyzing social networks for community detection
- Ensuring completeness of dependency graphs

### Limitations:
- Only works with simple graphs; complex relationships may require more advanced models
- Cannot detect semantic or logical issues in graph edges

---

## Summary Table: Guardrail Overview

| Guardrail Name        | Core Functionality                   | Primary Use Case                                      |
|----------------------|--------------------------------------|--------------------------------------------------------|
| SimilarityGuardrail  | Text similarity detection            | Duplicate/paraphrase checking, consistency validation  |
| LdaTopicGuardrail    | Topic alignment with LDA             | Content theme validation, domain-specific terminology  |
| BERTopicGuardrail    | Semantic topic modeling              | Advanced NLP analysis, multilingual content validation |
| KeywordCoverageGuardrail | Keyword presence check         | Compliance verification, documentation completeness   |
| NetworkXGuardrail    | Graph structure validation           | Network reliability, dependency graph analysis        |

---

## Best Practices for Implementation
- **Threshold Tuning**: Adjust similarity and coverage thresholds based on domain-specific requirements.
- **Error Handling**: Implement fallback logic for cases where no keywords are found or graphs are empty.
- **Model Caching**: Pre-load NLP models (e.g., BERT, LDA) to avoid repeated initialization overhead.
- **Logging**: Record detailed results for debugging and audit purposes.

These guardrails provide a robust framework for ensuring data integrity, semantic consistency, and structural validity across different stages of your project pipeline.