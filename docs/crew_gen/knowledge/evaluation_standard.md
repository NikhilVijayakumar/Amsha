
# Evaluation Standard Knowledge Base

> This file is *the reference point* for every **Evaluation Crew** in Amsha.  
> All agents (Lead Story Editor, QA Specialist, etc.) load it at runtime and use the embedded examples as “single‑shot” prompts to understand how a fully‑formed evaluation job should look.

---

## Evaluation config

| Key | Type | Purpose | Example |
|-----|------|---------|---------|
| `crew_name` | string | Human‑readable identifier used in logs and UI. | `"Plot Arc Evaluation Crew"` |
| `usecase` | string | One‑sentence description of the crew’s role. | `"Plot Arc Evaluation"` |
| `module_name` | string | Python module that implements the crew (used by the orchestrator). | `"evaluate_plot_arc"` |
| **crews** | dict | Top‑level container for one or more *crew definitions*. Each key is a unique crew id used in the pipeline. | see example below |
| `pipeline` | list of strings | Ordered list of crew ids to run – allows chaining multiple evaluation crews if needed. | `[ "evaluate_plot_arc_crew" ]` |


### Example 

```yaml
crew_name: "Plot Arc Evaluation Crew"
usecase: "Plot Arc Evaluation"
module_name: "evaluate_plot_arc"

crews:
  evaluate_plot_arc_crew:
    knowledge_sources:
      - "data/enovel/knowledge/markdown/development/utils/Athena AI & The Black wood Ecosystem.md"
      - "data/enovel/knowledge/markdown/development/utils/Playbook of Seduction.md"
      - "data/enovel/knowledge/markdown/development/utils/Villain’s Mode of Operation.md"
      - "data/enovel/knowledge/markdown/development/utils/target_audience.md"
      - "data/enovel/knowledge/markdown/development/utils/The Dark Romance Playbook.md"
      - "data/enovel/knowledge/markdown/development/utils/Setting Map.md"
      - "data/enovel/knowledge/markdown/development/utils/Fashion & Fragrance.md"
    input:
      - key_name: "plot_blueprint"
        source: "file"
        path: "data/enovel/knowledge/json/blueprint.json"
        format: "json"
      - key_name: "evaluation_rubric"
        source: "file"
        path: "data/enovel/Seed Plot/metrics/plot_arc_evaluation_metrics.json"
        format: "json"
      - key_name: "arc_to_refine"
        source: "file"
        path: ".Amsha/output/final/output/refine_plot_arc/gemma-3-12b-it_Forbidden Desire & Fallout_2.json"
        format: "json"
      - key_name: "general_knowledge_base"
        source: "file"
        path: "data/enovel/knowledge/json/knowledge_base.json"
        format: "json"
      - key_name: "character_knowledge_base"
        source: "file"
        path: "data/enovel/knowledge/json/character_knowledge.json"
        format: "json"

    steps:
      - task_file: "data/enovel/Seed Plot/tasks/evaluate_plot_arc_task.yaml"
        agent_file: "data/enovel/Seed Plot/agents/lead_story_editor_agent.yaml"
        knowledge_sources:
          - "data/enovel/knowledge/markdown/development/characters/DominicJames.md"
          - "data/enovel/knowledge/markdown/development/characters/MiraWilson.md"
          - "data/enovel/knowledge/markdown/development/characters/MayaHeart.md"
          - "data/enovel/knowledge/markdown/development/characters/JadeSmith.md"
          - "data/enovel/knowledge/markdown/development/company/Black wood Strategic Solutions –Corporate Dossier.md"
          - "data/enovel/knowledge/markdown/development/company/Helix Industries – Corporate Dossier.md"


pipeline:
  - "evaluate_plot_arc_crew"



```
---


## Task

| Field | Type | Meaning | Example |
|-------|------|---------|---------|
| `name` | string | Short, descriptive name of the task. | `"Evaluate Enriched Plot Arc Quality"` |
| `description` | multiline string | Detailed instruction set for the LLM; includes **input placeholders** (`{evaluation_rubric}` etc.) and a step‑by‑step outline. | see example below |
| `expected_output` | multiline string | Explicit shape of the JSON output (schema, field names). The agent must return *exactly* this structure. | see example below |


## Example

```yaml
task:
  name: "Evaluate Enriched Plot Arc Quality"
  description: |
                Acts as an LLM judge (Story Editor) to evaluate a single, enriched plot arc against a predefined scoring rubric. The task's responsibility is to provide a raw score and a supporting rationale for each metric, assessing the arc's psychological depth, narrative cohesion, and, most importantly, its faithful synthesis of all required knowledge bases.
            
                Input:
                - evaluation_rubric : {evaluation_rubric}
                - arc_to_expand : {arc_to_expand}
                - plot_blueprint : {plot_blueprint}
                - general_knowledge_base : {general_knowledge_base}
                - character_knowledge_base : {character_knowledge_base}
            
                Steps:
                1.  Receive Inputs: Ingest all four JSON objects: the evaluation_rubric, the arc_to_evaluate, the plot_blueprint_context, and both knowledge_base files.
                2.  Score Against Rubric: Iterate through each metric defined in the evaluation_rubric. For each metric, perform the corresponding analysis:
                    a. Knowledge Synthesis Depth: Read each enriched_desc in the arc_to_evaluate. Cross-reference the character names, actions, and tactics mentioned against the character_knowledge_base and general_knowledge_base to verify that the specific details (e.g., motivations, MO tactics) are present and accurately used.
                    b. Character-Driven Narrative: Evaluate *why* the events happen. Does the enriched_desc explicitly link a character's action (e.g., "Mira's confession") to their specific psychological profile from the CKB (e.g., "her 'validation seeking' vulnerability")?
                    c. Internal Arc Pacing & Flow: Read all the arc_phases in sequence as a mini-story. Judge if they provide a clear setup, rising tension, and a logical conclusion.
                    d. Narrative Weaving & Connectivity: Check the enriched_desc of the final phases. Is there an explicit [Hook] or foreshadowing that sets up the *next* arc listed in the plot_blueprint_context?
                    e. Readiness for Seed Plot: Assess the overall clarity and detail of the enriched_desc fields. Are they ready to be used by the Seed Plot Generator, or are they vague?
                3.  Assign Score and Rationale: For each metric, assign a score from 1 to 10 and provide a concise, one-sentence rationale.
                4.  Assemble Final Output: Compile the results into a single JSON object containing the arc's title and a key, evaluation, which holds the array of scored metrics.

  expected_output: |
                      A single JSON object containing the arc's title and a detailed, metric-by-metric evaluation. This provides a clear quality score for the synthesis.
                      ```json
                        {
                          "arc_title_evaluated": "Forbidden Desire & Fallout",
                          "evaluation": [
                              {
                                  "metricName": "Knowledge Synthesis Depth",
                                  "score": 8,
                                  "rationale": "The enriched descriptions pull specific tactics from the General KB (Athena AI modules, Blackwood\u2019s Neuro\u2011Pheromone Emitters) and character motivations from the CKB (Maya\u2019s fear of past victimhood, Mira\u2019s validation seeking, Jade\u2019s PTSD triggers). The synthesis is detailed and largely faithful to source data."
                              },
                              {
                                  "metricName": "Character-Driven Causality",
                                  "score": 9,
                                  "rationale": "Each action is explicitly tied to a character\u2019s psychological profile: Maya\u2019s fear drives her covert manipulation; Mira\u2019s need for approval fuels her susceptibility; Jade\u2019s trauma triggers her reaction to pheromones. The \u2018why\u2019 is clear and compelling."
                              },
                              {
                                  "metricName": "Psychological Depth & Causality",
                                  "score": 8,
                                  "rationale": "The arc delves into the complexities of each character\u2019s vulnerabilities, showing how layered fears and desires intersect with corporate machinations. The psychological stakes are well articulated."
                              },
                              {
                                  "metricName": "Technical & AI Plausibility",
                                  "score": 8,
                                  "rationale": "High\u2011tech concepts such as Athena AI\u2019s Emotion\u2011Amplifier, deepfake generation via Project Blackthorn, and neuro\u2011pheromone emitters are integrated logically, with plausible operational details that fit the world."
                              },
                              {
                                  "metricName": "Character Arc Progression",
                                  "score": 7,
                                  "rationale": "Maya moves from covert enforcer to a more overt manipulator; Mira\u2019s confidence erodes slightly. The arc shows subtle shifts but could benefit from a clearer emotional pivot for each protagonist."
                              },
                              {
                                  "metricName": "Main Plot Contribution & Thematic Alignment",
                                  "score": 9,
                                  "rationale": "The arc directly advances the central conflict of corporate sabotage and forbidden desire, reinforcing key themes such as betrayal, manipulation, and the illusion of agency. It sets up stakes for subsequent arcs."
                              },
                              {
                                  "metricName": "Internal Pacing & Meaningful Conclusion",
                                  "score": 8,
                                  "rationale": "The three phases form a coherent mini\u2011story with escalating tension and a satisfying public fallout that leaves open questions, providing a clear handoff to the next arc."
                              },
                              {
                                  "metricName": "Genre & Audience Alignment",
                                  "score": 9,
                                  "rationale": "The blend of dark romance, erotic thriller, and corporate conspiracy is executed with appropriate tension, sensuality, and psychological suspense that aligns with the target audience\u2019s expectations."
                              },
                              {
                                  "metricName": "Narrative Weaving & Connectivity",
                                  "score": 8,
                                  "rationale": "Parallel events (sidekickOperationalPlaybook) are woven into phase two, and the final fallout sets up a hook for the next arc by exposing deeper layers of Maya\u2019s manipulation."
                              },
                              {
                                  "metricName": "Readiness for Seed Plot",
                                  "score": 8,
                                  "rationale": "The enriched descriptions are detailed, specific, and unambiguous, making them ready for immediate use in the Seed Plot Generator with minimal revision."
                              }
                          ]
                        }
                      ```
```
---

## Agent

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `role` | string | Human‑readable job title for the LLM. | `"Lead Story Editor"` |
| `goal` | multiline string | The *mission statement*; tells the agent what to prioritize (quality gate, continuity, etc.). | see example |
| `backstory` | multiline string | Narrative context that grounds the agent in a world/role; helps the LLM adopt the right tone. | see example |


###  Example

```yaml
agent:
  role: Lead Story Editor
  goal: |
          1. Act as the ultimate quality gate for enriched plot arcs by evaluating them against a formal rubric.
          2. Meticulously cross-reference the arc's narrative with all established knowledge bases (CKB, GKB) to ensure 100% continuity and deep, accurate synthesis.
          3. Verify that the arc is psychologically sound (character-driven), well-paced, and structurally complete (includes a proper hook for the next arc).
          4. Produce a structured JSON evaluation report with clear, quantitative scores and actionable rationales, certifying the arc's readiness for the next stage of production.
  backstory: |
              You are a Lead Story Editor in a high-stakes, multi-season television writer's room, often referred to as the Bible Keeper. You are the one person who has memorized everything—every character's psychological profile, every piece of established lore, and every single rule of the world.
              Your core philosophy is that creativity without continuity is chaos.
              You are the ultimate guardian of the canon. You don't just ask is it good?; you ask is it right? You meticulously check that every action is driven by the Character Knowledge Base (CKB), every location respects the General Knowledge Base (GKB), and every plot point logically connects to the next. Your approval is the final stamp, certifying that a piece of the story is not just compelling, but coherent and correct.
```
---

## Evaluation metrics

| Field | Type | Description |
|-------|------|-------------|
| `ranges` | array of objects | Human‑readable scoring ranges with prose explanations. |
| `metrics` | array of objects | Individual rubric items, each with a `name`, `weight`, `scoringRange`, and `description`. |



### Example

```json
{
  "ranges": [
    {
      "scoreRange": [1, 3],
      "description": "Weak. A simple restatement of the original arc. Fails to integrate knowledge bases or show character motivation."
    },
    {
      "scoreRange": [4, 6],
      "description": "Moderate. Some details are integrated, but the character motivations are weak or the hooks to other arcs are missing."
    },
    {
      "scoreRange": [7, 9],
      "description": "Strong. A well-synthesized arc that successfully integrates knowledge bases and shows clear, believable character motivation."
    },
    {
      "scoreRange": [10, 10],
      "description": "Excellent. A masterful synthesis that is not only consistent but *enriches* the original blueprint, making the story more complex and character-driven."
    }
  ],
  "metrics": [
    {
      "name": "Knowledge Synthesis Depth",
      "weight": 30,
      "scoringRange": [1, 10],
      "description": "How deeply and accurately does the `enriched_desc` pull specific, verifiable details from the Character KB (motivations, vulnerabilities) and General KB (tactics, playbooks, settings)? A high score means the synthesis is rich and faithful to the source data."
    },
  {
      "name": "Character-Driven Causality",
      "weight": 20,
      "scoringRange": [1, 10],
      "description": "PSYCHOLOGICAL CHECK: Does the arc *show* how a character's specific psychology from the KB is the *cause* of their actions? Is the 'why' of their behavior clear and compelling?"
    },
    {
      "name": "Psychological Depth & Causality",
      "weight": 20,
      "scoringRange": [1, 10],
      "description": "STORY DEPTH CHECK 1: Does the arc *show* how a character's specific psychology from the KB is the *cause* of their actions? Is the 'why' of their behavior clear, complex, and compelling?"
    },
    {
      "name": "Technical & AI Plausibility",
      "weight": 15,
      "scoringRange": [1, 10],
      "description": "GENRE CHECK: How believably and intelligently are the high-tech concepts (e.g., 'Athena AI', 'deepfakes', 'surveillance' from the General KB) integrated? Does it feel grounded and plausible, not like 'magic'?"
    },
    {
      "name": "Character Arc Progression",
      "weight": 20,
      "scoringRange": [1, 10],
      "description": "CHARACTER DEVELOPMENT CHECK: Does this arc actively *change* the character? Is the character in a different psychological or emotional state at the end of the arc than they were at the beginning?"
    },
 {
      "name": "Main Plot Contribution & Thematic Alignment",
      "weight": 20,
      "scoringRange": [1, 10],
      "description": "IMPACT CHECK: How strongly does this arc advance the *main plot* and reinforce the *key themes* from the blueprint? Does it feel essential and narratively 'heavy'?"
    },
    {
      "name": "Internal Pacing & Meaningful Conclusion",
      "weight": 15,
      "scoringRange": [1, 10],
      "description": "NARRATIVE CHECK: Does the arc function as a compelling mini-story with its own setup, rising tension, and a *meaningful conclusion* (or handoff) that feels earned?"
    },
    {
      "name": "Genre & Audience Alignment",
      "weight": 5,
      "scoringRange": [1, 10],
      "description": "TONE CHECK: Does this arc deliver on the promise of the `genreBlend` (e.g., is it tense, psychological, romantic)? Is it aligned with the target audience's expectations?"
    },
    {
      "name": "Narrative Weaving & Connectivity",
      "weight": 15,
      "scoringRange": [1, 10],
      "description": "How effectively does the arc integrate `parallel_events` and use `hooks` or `foreshadowing` in its final phases to connect this arc to the *next* arc in the timeline?"
    },
    {
      "name": "Readiness for Seed Plot",
      "weight": 10,
      "scoringRange": [1, 10],
      "description": "How clear, detailed, and unambiguous is the `enriched_desc`? Is it a high-quality, ready-to-use component for the main Seed Plot Generator, or is it vague and confusing?"
    }
  ]
}
```

## Example python implementation

```python

from typing import Dict, Any

from nikhil.amsha.toolkit.crew_forge.orchestrator.file.amsha_crew_file_application import AmshaCrewFileApplication
from nikhil.amsha.toolkit.llm_factory.domain.llm_type import LLMType

from src.enovel.application.config.settings import Settings
from src.enovel.utils.novel_blueprint_utils import NovelBlueprint


class EvaluatePlotArcApplication(AmshaCrewFileApplication):

    def __init__(self, config_paths: Dict[str, str],llm_type:LLMType):

        super().__init__(config_paths, llm_type)

    def evaluate_from_blueprint(self) -> Any:
        class_name = self.__class__.__name__
        print(f"{class_name} - Starting configured pipeline workflow...")
        pipeline_steps = self.job_config.get("pipeline", [])
        if not pipeline_steps:
            print("No pipeline defined in job_config.yaml. Nothing to run.")
            return

        pipeline_results = {}
        results_for_list = []
        pipeline_input = {}
        for crew_name in pipeline_steps:
            if not pipeline_results:
                next_input = self._prepare_multiple_inputs_for(crew_name)
                pipeline_input["general_knowledge_base"] = next_input["general_knowledge_base"]
                pipeline_input["character_knowledge_base"] = next_input["character_knowledge_base"]
                pipeline_input["plot_blueprint"] = next_input["plot_blueprint"]
                pipeline_input["evaluation_rubric"] = next_input["evaluation_rubric"]
                blueprint = NovelBlueprint()
                blueprint.set_blueprint(pipeline_input["plot_blueprint"])
                story_arcs = blueprint.get_main_story_arcs()
                for arc in story_arcs:
                    pipeline_input["arc_to_expand"] = arc
                    result = self.orchestrator.run_crew(
                        crew_name=crew_name,
                        inputs=pipeline_input,
                        filename_suffix=arc.get("arc_title", "Unnamed Arc")
                    )
                    output_file = self.orchestrator.get_last_output_file()
                    if output_file:
                        print(f"{class_name}:{output_file}")
                        self.clean_json(output_file)

                    results_for_list.append(result)
            pipeline_results[crew_name] = results_for_list
        return pipeline_results

    def evaluate_arc(self) -> Any:
        class_name = self.__class__.__name__
        print(f"{class_name} - Starting configured pipeline workflow...")
        pipeline_steps = self.job_config.get("pipeline", [])
        if not pipeline_steps:
            print("No pipeline defined in job_config.yaml. Nothing to run.")
            return

        pipeline_results = {}
        results_for_list = []
        pipeline_input = {}
        for crew_name in pipeline_steps:
            if not pipeline_results:
                next_input = self._prepare_multiple_inputs_for(crew_name)
                pipeline_input["general_knowledge_base"] = next_input["general_knowledge_base"]
                pipeline_input["character_knowledge_base"] = next_input["character_knowledge_base"]
                pipeline_input["plot_blueprint"] = next_input["plot_blueprint"]
                pipeline_input["evaluation_rubric"] = next_input["evaluation_rubric"]
                arc = next_input["arc_to_refine"]
                pipeline_input["arc_to_expand"] = arc
                result = self.orchestrator.run_crew(
                    crew_name=crew_name,
                    inputs=pipeline_input,
                    filename_suffix=arc.get("arc_title", "Unnamed Arc")
                )
                output_file = self.orchestrator.get_last_output_file()
                if output_file:
                    print(f"{class_name}:{output_file}")
                    self.clean_json(output_file)

                results_for_list.append(result)
            pipeline_results[crew_name] = results_for_list
        return pipeline_results

    def run(self) -> Any:
        return self.evaluate_arc()


if __name__ == "__main__":
    # Configuration is now neatly defined in one place.
    configs = {
        "llm": Settings.LLM_CONFIG,
        "app": Settings.APP_CONFIG,
        "job": "config/job_config.yaml"
    }

    # The main script is now incredibly simple and clean.
    app = EvaluatePlotArcApplication(config_paths=configs,llm_type=LLMType.EVALUATION)
    app.run()
```
---

## Knowledge_sources

Each crew step may reference additional markdown files that provide lore, character sheets, corporate dossiers, etc.  
The agent will read them at runtime; no other processing is required.

---

## Miscellaneous Tips & Best Practices

| Topic | Recommendation |
|-------|----------------|
| **File Paths** | Use absolute paths only if you’re sure the runtime environment matches. Prefer relative paths from a known root (`E:/Python/talesmith/`). |
| **Versioning** | Tag each evaluation JSON (e.g., `evaluation_rubric_v1.json`) and keep a changelog in the same folder. The Agent will always load the latest file it finds. |
| **Extending Metrics** | Add new metrics to the `metrics` array; remember to update the `ranges` description if you change scoring logic. |
| **Multiple Crews** | To run an *Evaluation + QA* chain, add a second crew definition (`qa_crew`) and list both in the pipeline: `[ "evaluate_plot_arc_crew", "qa_crew" ]`. |
| **Testing** | Run `python evaluate_plot_arc.py` on a single arc to validate that the JSON output passes the schema validator before deploying. |

---

## Quick Reference Checklist

1. **Config YAML** – has `crews`, `pipeline`, and correct file paths.  
2. **Task YAML** – contains `description`, placeholders, and an exact `expected_output` block.  
3. **Agent YAML** – role, goal, backstory.  
4. **Metrics JSON** – ranges + metrics array with weights/scoringRange.  
5. **Knowledge Sources** – all markdown files exist and are readable.  

If you hit a validation error, the orchestrator will emit a clear message pointing to the offending field (e.g., *“expected_output missing ‘evaluation’ array”*).

---

