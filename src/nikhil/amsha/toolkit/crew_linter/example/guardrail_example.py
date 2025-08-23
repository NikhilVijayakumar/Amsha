import nltk
import yaml
from pathlib import Path

from nikhil.amsha.toolkit.crew_linter.containers.container import Container
from nikhil.amsha.toolkit.crew_linter.preprocessing.preparation.text_preprocessor import TextPreprocessor


def load_yaml(path):
    """Load a YAML file and return its contents as a dict."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# --- Load agent & task from YAML ---
agent_conf = load_yaml(Path("config/agent.yaml"))
task_conf = load_yaml(Path("config/task.yaml"))

print(f"[Agent Loaded] Role: {agent_conf['agent']['role']}")
print(f"[Task Loaded] Name: {task_conf['task']['name']}")
print("NLTK is searching for data in these directories:")
TextPreprocessor.download_required_data()
textPreprocessor = TextPreprocessor()

goal = agent_conf['agent']['goal']
description = task_conf['task']['description']

goal_keywords = textPreprocessor.extract_keywords(goal)
goal_topics = textPreprocessor.extract_topics(goal,num_topics=6)
description_keywords = textPreprocessor.extract_keywords(description)
description_topics = textPreprocessor.extract_topics(description,num_topics=6)

print(f"goal_keywords: {goal_keywords}\n")
print(f"goal_topics: {goal_topics}\n")
print(f"description_keywords: {description_keywords}\n")
print(f"description_topics: {description_topics}\n")


guardrail_conf = load_yaml(Path("config/job_config.yaml"))

# Create DI container and pass values from YAML
container = Container()
container.config.from_dict({
    "vectorizer_min_df": 1,
    "vectorizer_max_df": 0.9,
    "bertopic_top_n_words": 5,
    "bertopic_similarity_threshold": 0.75,
    "similarity_ratio": guardrail_conf["similarity_guardrail"]["ratio"],
    "similarity_partial_ratio": guardrail_conf["similarity_guardrail"]["partial_ratio"],
    "similarity_token_sort_ratio": guardrail_conf["similarity_guardrail"]["token_sort_ratio"],
    "similarity_threshold_cosine": guardrail_conf["similarity_guardrail"]["threshold_cosine"],
    "networkx_is_directed": True
})

# Example flashcard data to test guardrails
flashcard_data = {
    "topic": "Database Normalization",
    "keywords": ["2NF", "3NF", "partial dependency", "transitive dependency"],
    "graphs": """
        2NF eliminates partial dependencies where a non-key attribute depends on only part of a composite primary key.
        3NF eliminates transitive dependencies where non-key attributes depend on other non-key attributes.
    """
}

# --- Prepare inputs for guardrails ---
keyword_input = container.keyword_coverage_input_factory(
    text=goal,
    keywords=goal_keywords
)

similarity_input = container.similarity_input_factory(
    source=goal,
    target=description
)

bertopic_input = container.ber_topic_input_factory(
    texts=[goal, description],
    reference_topics=[]
)

# --- Create guardrail objects ---
keyword_guardrail = container.keyword_guardrail_factory(data=keyword_input)
similarity_guardrail = container.similarity_guardrail_factory(data=similarity_input)
bertopic_guardrail = container.ber_topic_guardrail_factory(data=bertopic_input)
networkx_guardrail = container.networkx_guardrail_factory()

# --- Run validations ---
results = [
    keyword_guardrail.check(),
    similarity_guardrail.check_fuzzy(),
    bertopic_guardrail.check(),
    networkx_guardrail.check([
        ("Breakdown Components", "Compare Approaches"),
        ("Compare Approaches", "Identify Flaws")
    ])
]

# --- Output results ---
if all(r.passed for r in results):
    print("✅ All guardrails passed. Proceed with agent task.")
else:
    print("❌ Guardrail failures detected:")
    for r in results:
        if not r.passed:
            print(f" - {r.name}: {r.message}")
