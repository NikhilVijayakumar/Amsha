# src/nikhil/amsha/toolkit/crew_linter/dependency/container.py
from dependency_injector import containers, providers

# Import all necessary domain models
from nikhil.amsha.toolkit.crew_linter.domain.models.ber_topic_data import BERTopicInput
from nikhil.amsha.toolkit.crew_linter.domain.models.keyword_coverage_data import KeywordCoverageInput
from nikhil.amsha.toolkit.crew_linter.domain.models.lda_topic_data import LdaTopicInput
from nikhil.amsha.toolkit.crew_linter.domain.models.networkx_data import GraphData
from nikhil.amsha.toolkit.crew_linter.domain.models.similarity_data import SimilarityInput

# Import all guardrail classes
from nikhil.amsha.toolkit.crew_linter.guardrails.ber_topic_guardrail import BERTopicGuardrail
from nikhil.amsha.toolkit.crew_linter.guardrails.keyword_coverage_guardrail import KeywordCoverageGuardrail
from nikhil.amsha.toolkit.crew_linter.guardrails.lda_topic_guardrail import LdaTopicGuardrail
from nikhil.amsha.toolkit.crew_linter.guardrails.networkx_guardrail import NetworkXGuardrail
from nikhil.amsha.toolkit.crew_linter.guardrails.similarity_guardrail import SimilarityGuardrail

# Import preprocessing utilities
from nikhil.amsha.toolkit.crew_linter.preprocessing.preparation.text_preprocessor import TextPreprocessor
from nikhil.amsha.toolkit.crew_linter.preprocessing.preparation.vectorizer import Vectorizer


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection container that acts as a factory for the
    Amsha Crew Linter's components (the "Toolbox").
    """


    # --- Configuration ---
    # Central place for all default settings. Can be overridden from a YAML/JSON file.
    config = providers.Configuration( )

    # --- Core Utilities ---
    # These are reusable components that guardrails might depend on.
    # Singleton, as we only need one instance.
    text_preprocessor = providers.Singleton(TextPreprocessor)


    vectorizer_factory = providers.Factory(
        Vectorizer,
        min_df=config.vectorizer_min_df,
        max_df=config.vectorizer_max_df
    )


    ber_topic_input_factory = providers.Factory(
        BERTopicInput,
        texts=providers.Object([]),
        reference_topics=providers.Object([]),
        top_n_words=config.bertopic_top_n_words,
        similarity_threshold=config.bertopic_similarity_threshold
    )

    keyword_coverage_input_factory = providers.Factory(
        KeywordCoverageInput,
        text=providers.Object(""),
        keywords=providers.Object([])
    )

    lda_topic_input_factory = providers.Factory(LdaTopicInput)

    graph_data_input_factory = providers.Factory(GraphData)

    similarity_input_factory = providers.Factory(
        SimilarityInput,
        source=providers.Object(""),
        target=providers.Object(""),
        ratio=config.similarity_ratio,
        partial_ratio=config.similarity_partial_ratio,
        token_sort_ratio=config.similarity_token_sort_ratio,
        threshold_cosine=config.similarity_threshold_cosine,
    )

    # --- Guardrail Factories ---
    # Provides factories to create configured instances of each guardrail tool.
    ber_topic_guardrail_factory = providers.Factory(
        BERTopicGuardrail,
        data=ber_topic_input_factory
    )

    keyword_guardrail_factory = providers.Factory(
        KeywordCoverageGuardrail,
        data=keyword_coverage_input_factory
    )

    # This guardrail has no __init__ dependencies.
    lda_topic_guardrail_factory = providers.Factory(
        LdaTopicGuardrail
    )

    # This guardrail takes its config directly.
    networkx_guardrail_factory = providers.Factory(
        NetworkXGuardrail,
        directed=config.networkx_is_directed
    )

    similarity_guardrail_factory = providers.Factory(
        SimilarityGuardrail,
        data=similarity_input_factory
    )