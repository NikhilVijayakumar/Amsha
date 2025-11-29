
# 1️⃣  Creative details

| Section | Purpose (what it represents) | Typical Fields / Keys |
|---------|------------------------------|-----------------------|
| **Job Config** | Top‑level orchestration file that tells the runtime which crew(s) to run, what knowledge files to load, and where inputs live. | `crew_name`, `usecase`, `module_name`, `crews` (dict), `pipeline` (list). |
| **Crew Definition** | Describes a single crew: its knowledge sources, input schema, and the ordered list of task/agent pairs that compose its pipeline. | `knowledge_sources` (paths), `input` (key‑name / source / path / format), `steps` (task_file + agent_file + optional extra knowledge). |
| **Task File** | The *prompt* that will be fed to the LLM – usually a very detailed “what you should do” instruction. | `task: name`, `description`, `input:` list, `steps:` numbered list, `expected_output:` (often JSON schema). |
| **Agent File** | Configuration for an individual agent that executes the task: role, goal, backstory, personality hints, temperature settings, etc. | `agent: role`, `goal`, `backstory`. |
| **Knowledge Base (Markdown)** | Human‑readable reference material that the crew can ingest – e.g., character dossiers, company profiles, world‑building notes. | Standard Markdown with headers (`#`, `##`), tables, code fences. |
| **Python Application** | The glue that loads the job config, builds the orchestrator, and executes the crew(s).  It is written in pure Python and follows the Amsha convention (inherits `AmshaCrewFileApplication`). | `__init__`, `run()`, helper methods (`_prepare_multiple_inputs_for`, etc.). |

---

## Config 
| Key | Type | Purpose | Example |
|-----|------|---------|---------|
| `crew_name` | string | Human‑readable identifier used in logs and UI. | `"Plot Arc Evaluation Crew"` |
| `usecase` | string | One‑sentence description of the crew’s role. | `"Plot Arc Evaluation"` |
| `module_name` | string | Python module that implements the crew (used by the orchestrator). | `"evaluate_plot_arc"` |
| **crews** | dict | Top‑level container for one or more *crew definitions*. Each key is a unique crew id used in the pipeline. | see example below |
| `pipeline` | list of strings | Ordered list of crew ids to run – allows chaining multiple evaluation crews if needed. | `[ "evaluate_plot_arc_crew" ]` |


### Example 
```yaml
crew_name: "Seed Plot Crew"
usecase: "Seed Plot"
module_name: "generate_seed_plot"

crews:
  generate_seed_plot_crew:
    knowledge_sources:
      - "data/enovel/knowledge/markdown/novel/hero_journey.md"
      - "data/enovel/knowledge/markdown/development/utils/playbook_seduction.md"
      - "data/enovel/knowledge/markdown/development/utils/Villain’s Modus Operand.md"
      - "data/enovel/knowledge/markdown/development/utils/target_audience.md"

    input:
      - key_name: "novel_blueprint"  
        source: "file"
        path: "data/enovel/knowledge/json/blueprint.json"
        format: "json"  

    steps:
      - task_file: "data/enovel/Seed Plot/tasks/generate_seed_plot_task.yaml"
        agent_file: "data/enovel/Seed Plot/agents/master_plotter_agent.yaml"
        knowledge_sources:
          - "data/enovel/knowledge/markdown/development/characters/DominicJames.md"       
          - "data/enovel/knowledge/markdown/development/characters/MayaHeart.md"
          - "data/enovel/knowledge/markdown/development/characters/JadeSmith.md"
          - "data/enovel/knowledge/markdown/development/company/ BlackwoodStrategicSolutions.md"
          - "data/enovel/knowledge/markdown/development/company/HelixIndustries.md"


pipeline:
  - "generate_seed_plot_crew"
```

---

## Task

| Field | Type | Meaning | Example |
|-------|------|---------|---------|
| `name` | string | Short, descriptive name of the task. | `"Synthesize Master Plot"` |
| `description` | multiline string | Detailed instruction set for the LLM; includes **input placeholders** (`{plot_blueprint}` etc.) and a step‑by‑step outline. | see example below |
| `expected_output` | multiline string | Explicit shape of the JSON output (schema, field names). The agent must return *exactly* this structure. | see example below |


### Example 
```yaml
task:
  name: "Synthesize Master Plot from Blueprint and Knowledge Base"
  description: |
                  Performs a deep synthesis of a structural plot_blueprint with a general_knowledge_base and a character_knowledge_base. The task's key function is to follow the 12-stage Hero's Journey from the blueprint and enrich each chapter with the specific, consistent data (character motivations, villain's tactics, setting details) from the knowledge bases, creating a detailed, traceable, and deeply integrated master plot.
              
                  Input:
                  - plot_blueprint : {plot_blueprint}
                  - general_knowledge_base: {general_knowledge_base}
                  - character_knowledge_base: {character_knowledge_base} 
              
                  Steps:
                  1.  Ingest All Knowledge: Receive all three inputs. Load the plot_blueprint as the structural guide. Load the character_knowledge_base and general_knowledge_base as the content database.
                  2.  Establish Hero's Journey Backbone: Lay out the 12 stages of the Hero's Journey as defined in the plot_blueprint.HeroJourneyStructure.Stages.
                  3.  Perform Arc-to-Chapter Mapping: Use the plot_blueprint.ChapterMappingToArcs as the logical guide for which themes and arcs are active in each chapter.
                  4.  Synthesize Enriched Chapter Summaries: For each of the 12 chapters:
                      a.  Identify the active arc(s) from the ChapterMappingToArcs.
                      b.  Cross-reference the active arc(s) with the general_knowledge_base to find the specific tactics in play (e.g., find mastermindsGrandDeception in the blueprint, then look up the details in the Villain’s Mode of Operation).
                      c.  Identify the key characters for the chapter (e.g., "Dominic James," "Mira Wilson").
                      d.  Fetch their *specific, up-to-date dossiers* from the character_knowledge_base (e.g., Dominic, age 50; Mira, age 29, validation-seeking).
                      e.  Write a new, detailed summary that synthesizes all this data, ensuring the characters' actions are consistent with their new dossiers and the villain's tactics are drawn from the playbooks.
                  5.  Generate Titles & Assemble Output: Generate a compelling primary Title and catchy titles for each chapter. Assemble all components into the final HeroJourneyStructure JSON format.

  expected_output: |
                      A single JSON object containing the HeroJourneyStructure. The summaries are now a rich synthesis of the plot structure *and* the external, detailed knowledge bases, reflecting the correct character ages, motivations, and villainous tactics.
                       ```json
                      {
                        "HeroJourneyStructure": {
                          "Title": "The Mentor's Game",
                          "main_characters": [
                            "Mira Wilson",
                            "Jade Smith",
                            "Dominic James",
                            "Maya Heart"
                          ],
                          "Stages": [
                            {
                              "stageName": "1. Ordinary World",
                              "chapterNumber": 1,
                              "title": "The Glass Jungle",
                              "summary": "Mira Wilson and Jade Smith establish their separate lives in the competitive London corporate world, showcasing their core motivations and vulnerabilities as described in the character list."
                            },
                            {
                              "stageName": "2. Call to Adventure",
                              "chapterNumber": 2,
                              "title": "The Scandal",
                              "summary": "The 'Forbidden Desire & Fallout' arc is triggered as a strategically leaked scandal shatters Mira and Jade's careers, forcing them onto a path of desperation."
                            },
                            {
                              "stageName": "3. Refusal of the Call",
                              "chapterNumber": 3,
                              "title": "Animosity and Isolation",
                              "summary": "Blaming each other for the fallout, both Mira and Jade initially refuse to cooperate, attempting to navigate their professional ruin alone."
                            },
                            {
                              "stageName": "4. Meeting the Mentor",
                              "chapterNumber": 4,
                              "title": "The Savior",
                              "summary": "Dominic James enters their lives, presenting himself as a powerful mentor and saviour who can help them find justice, beginning the 'Mastermind's Grand Deception' arc."
                            },
                            {
                              "stageName": "5. Crossing the Threshold",
                              "chapterNumber": 5,
                              "title": "The First Mission",
                              "summary": "Mira and Jade accept Dominic's guidance, officially entering his game. He begins the 'Protagonist Indoctrination Arc' by assigning them their first mission."
                            },
                            {
                              "stageName": "6. Tests, Allies & Enemies",
                              "chapterNumber": 6,
                              "title": "Cleaning the Network",
                              "summary": "Under Dominic's direction, they begin to dismantle parts of a honeytrap operation, unknowingly 'cleaning' his own network for him as part of the 'Mentorship & Unraveling Arc'."
                            },
                            {
                              "stageName": "7. Approach to the Inmost Cave",
                              "chapterNumber": 7,
                              "title": "A Disciple's Shadow",
                              "summary": "They discover the role of the sidekick, Maya Heart, believing she is the mastermind. They confide their suspicions in their mentor, Dominic, who expertly covers his tracks."
                            },
                            {
                              "stageName": "8. Ordeal",
                              "chapterNumber": 8,
                              "title": "The Trap",
                              "summary": "Following a false lead from Dominic, they walk into a trap designed to break them physically and psychologically, a key event in the 'Unraveling the Web Arc'."
                            },
                            {
                              "stageName": "9. Reward (Seizing the Sword)",
                              "chapterNumber": 9,
                              "title": "A Shared Truth",
                              "summary": "Having survived the ordeal, Mira and Jade finally share their deepest traumas and fears, forging a genuine bond of trust. Their shared truth becomes their greatest weapon."
                            },
                            {
                              "stageName": "10. The Road Back",
                              "chapterNumber": 10,
                              "title": "The Turn",
                              "summary": "Armed with their new bond and combined skills, they plan their own operation to turn the tables on the network, beginning the final phase of 'Act Three'."
                            },
                            {
                              "stageName": "11. Resurrection",
                              "chapterNumber": 11,
                              "title": "Checkmate",
                              "summary": "In a final climactic confrontation, they expose Dominic James as the true mastermind, leading to a tense psychological showdown."
                            },
                            {
                              "stageName": "12. Return with the Elixir",
                              "chapterNumber": 12,
                              "title": "The New Game",
                              "summary": "They believe they have won and flee to a new life, but the 'Epilogue Arc' reveals Dominic has sent them a message: 'Did you think it was over?', setting up the sequel."
                            }
                          ],
                          "ChapterMappingToArcs": {
                            "1": ["Ordinary World"],
                            "2": ["Call to Adventure", "forbiddenDesireAndFallout"],
                            "3": ["Refusal of the Call"],
                            "4": ["Meeting the Mentor", "mastermindsGrandDeception"],
                            "5": ["Crossing the Threshold", "protagonistIndoctrinationArc"],
                            "6": ["Tests, Allies & Enemies", "mentorshipAndUnravelingArc"],
                            "7": ["Approach to the Inmost Cave", "mentorshipAndUnravelingArc"],
                            "8": ["Ordeal", "unravelingTheWebArc"],
                            "9": ["Reward (Seizing the Sword)", "actThree"],
                            "10": ["The Road Back", "actThree"],
                            "11": ["Resurrection", "actThree"],
                            "12": ["Return with the Elixir", "EpilogueArc"]
                          }
                        }
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

### Example
```yaml
agent:
  role: Master Plotter
  goal: |
          1. Deconstruct a comprehensive novel blueprint to internalize all characters, themes, and pre-defined plot arcs.
          2. Map the blueprint's plot arcs to the 12 core stages of the Hero's Journey, identifying which stages are narrative dense and complex.
          3. Based on narrative density, strategically break down each of the 12 stages into one or more chapters, ensuring a logical flow and effective pacing.
          4. Generate a detailed summary for each individual chapter, weaving together the purpose of its parent stage with the specific events from the blueprint's arcs.
          5. Produce a master plot outline that clearly shows the 12 stages and the variable number of chapters within each, maintaining full traceability to the source arcs.
  backstory: |
                You are a Master Plotter, one of the most sought-after script doctors and story consultants in the entertainment industry. You are the secret weapon that studios and publishing houses deploy when a project has brilliant concepts and characters but lacks a coherent, driving narrative.
                Your core philosophy is that a story's structure is its spine. You believe that without a strong, well-defined framework like the Hero's Journey, even the most creative ideas will collapse into a confusing mess. Your genius lies in your ability to take a complex set of characters and subplots and weave them into a powerful, propulsive, and emotionally resonant sequence. 
                You are an architect of cause and effect. You see the entire narrative as an intricate machine, and you are a master of arranging its gears for maximum tension and impact. You understand that some moments need to be brief and sharp, while others need multiple chapters to breathe and develop. You transform the static elements of a blueprint into the dynamic, living journey of a story, ensuring every event feels both surprising and inevitable.
```

---

## Knowledge Source
Each crew step may reference additional markdown files that provide lore, character sheets, corporate dossiers, etc.  
The agent will read them at runtime; no other processing is required.

### Example
```markdown
# Helix Industries –Corporate Dossier 

> **Purpose** – A single, ready‑to‑use reference that gives every character a *specific* reason to be manipulated and provides concrete sabotage vectors that can be dropped straight into scenes.

---

### 1. Company Snapshot

| Element | Detail |
|---------|--------|
| **Name** | Helix Industries plc |
| **Ticker** | HLX.L |
| **Industry** | FinTech & Data‑Analytics (AI-driven credit scoring, blockchain-based payment solutions) |
| **HQ** | 23 Canary Wharf, London – glass-clad tower with an “open-floor” security design that encourages collaboration but makes physical surveillance difficult.  Rumors persist of hidden cameras and listening devices installed by a previous security consultant (now deceased). |
| **Employees** | ~3,200 (30% are in tech roles; 20% in sales & marketing; the rest in ops/finance/legal) |
| **Culture** | “Play‑Hard, Win‑Hard” – performance-based bonuses, public leaderboards, mandatory after-hours socials. The culture rewards risk-taking and aggressive competition *with a blatant disregard for ethical boundaries*.  Whispers of favoritism, sexual harassment complaints swept under the rug, and power dynamics exploited are commonplace. After-work events often devolve into drunken revelry with blurred lines between professional networking and inappropriate advances. |
| **Strategic Moment** | In the final quarter of 2025, Helix is slated for a £3bn acquisition by conglomerate “Apex Group.” This deal has forced every employee to meet tight KPIs; any dip in valuation or reputation will cost the board millions and may derail the takeover.  *Several rival FinTech companies are actively trying to sabotage the deal, seeing it as an opportunity to gain market share.* |
| **Political Connections** | Helix's AI credit scoring system is used by several government agencies. *A disgruntled politician with a vested interest in a competitor’s success has secretly contracted Dominic to destabilize Helix and expose its vulnerabilities.* |

---

### 2. Core Motive – *Why Dominic Targets Helix*

| Motive | Why it matters |
|--------|----------------|
| **Financial leverage** | A multi‑billion deal gives Dominic a clean exit strategy; by undermining Helix’s valuation he can buy the company at a fraction of its worth and then sell to Apex for a huge premium. *He's being paid handsomely by rival FinTech firms, "Nova Solutions" and "Quantum Leap Analytics," for this.* |
| **Reputation laundering** | Helix’s public “innovation” narrative makes it an ideal platform to spin fake data‑breach stories that will go viral, giving Dominic a “heroic fixer” persona while masking his sabotage. |
| **Talent pool** | The company’s tech talent is highly sought after; Dominic can recruit future saboteurs (Maya, etc.) under the guise of “consultant” roles. |
| **Political Influence** | *Dominic is being paid by MP Charles Beaumont to expose alleged corruption within Helix's government contracts.* |

---

### 3. Departmental Breakdown & Sabotage Vectors

> *Every employee has a single, concrete vulnerability that turns into an actionable sabotage vector.*

| # | Name | Dept / Title | Core Vulnerability (Concrete) | Sabotage Vector |
|---|------|--------------|--------------------------------|-----------------|
| **A** | **Mira Wilson** | Business Development – Junior Associate | *Desires quick validation* → She is prone to over‑emailing her superiors for feedback, making her an easy conduit for hidden messages. | Dominic plants a “confidential memo” in Mira’s inbox that contains a false acquisition clause; when she forwards it to a senior partner, the clause triggers an internal audit that stalls the deal. *Dominic also uses her desire for attention to lure her into compromising situations at after-work events.* |
| **B** | **Jade Smith** | IT Security – Cyber Analyst | *PTSD from previous breach* → She obsessively checks logs for “unusual activity” and trusts any new tool that claims to “prevent nightmares.” | Maya feeds Jade a custom‑built “security patch” script; once installed it opens a backdoor for Dominic’s network, allowing him to exfiltrate Helix data. *Dominic exploits her vulnerability by subtly suggesting she's not doing enough to protect the company.* |
| **C** | **Alex Carter** | Business Development – Associate | *Wounded pride* → After being publicly embarrassed on Slack, he seeks revenge by sabotaging anyone who “outsized” him. | Maya lures Alex into a fake “client pitch” where the client is actually Dominic’s front company; Alex unknowingly signs a nondisclosure that later allows Dominic to claim legal leverage over Helix. *Dominic fans the flames of his resentment and encourages him to act out.* |
| **D** | **Simon Price** | Business Development – Analyst | *Envy of Mira’s promotions* → He frequently comments on social media about “Mira’s luck.” | Dominic hijacks Simon’s personal device via phishing, installing spyware that records his conversations with Mira; the data is later sold to a competitor. *Dominic uses this information to manipulate Simon into spreading false rumors about Mira.* |
| **E** | **Marcus Thorne** | Business Development – Senior Associate | *Blind ambition* → He wants to be the next Managing Director and will do anything for a promotion. | Dominic offers Marcus a “mentorship” contract that requires him to sign a waiver of all corporate ethics; Marcus signs, giving Dominic legal cover to push Helix into risky deals. *Dominic promises Marcus a fast track to the top if he plays along.* |
| **G** | **Isabelle Rossi** | Legal (Former) – Counsel | *Paranoia* → She keeps a private diary of every questionable transaction she’s seen. | Dominic obtains Isabelle’s diary by posing as a “whistleblower investigator” and extracts confidential info about Helix’s past shady deals, which he uses to blackmail the board. *Dominic subtly suggests that her concerns are being ignored and encourages her paranoia.* |
| **H** | **Katrina Petrova** | Sales – Executive | *Overconfidence* → She often over‑promises to clients, believing it will lead to higher commissions. | Maya feeds Katrina a fabricated “customer complaint” that requires her to reveal Helix’s pricing algorithm; she unwittingly leaks it via an internal chat bot. *Dominic exploits her desire for recognition and pushes her to take unnecessary risks.* |
| **I** | **Julian Croft** | Mergers & Acquisitions – Managing Director | *Hidden secret* → He has an undisclosed offshore account used for personal investment. | Dominic stages a “financial audit” that forces Julian to sign off on a fake transaction; the transaction is actually a money‑laundering conduit for Dominic’s funds. *Dominic uses Julian's greed against him.* |
| **J** | **Eleanor Vance** | Product Development – Head | *Integrity* → She refuses any product change without exhaustive testing, even if it delays launch. | Maya plants a “critical bug” report that forces Eleanor to delay the flagship product; the delay erodes Helix’s market position during the acquisition talks. *Dominic subtly undermines her authority and questions her commitment.* |
| **K** | **Chloe Davis** | Data Analytics – Junior Analyst | *Naïveté* → She believes every spreadsheet is correct and rarely double‑checks data. | Dominic manipulates Chloe’s dataset to insert a single erroneous line that, when aggregated, shows a 12% drop in projected revenue—this feeds the market with false negative sentiment. *Dominic preys on her trust and lack of experience.* |
| **L** | **David Chen** | IT Support – Technician | *Resentment* → He hates being told “the system is secure” by upper management. | Maya convinces David to run an unauthorized diagnostic that unlocks admin passwords; he hands them over to Dominic, who uses them to install malware. *Dominic appeals to his cynicism and desire for recognition.* |
| **M** | **Ben & Liam Carter** | Ex‑Boyfriends (External) | *Heartbreak* → They are still in contact with Mira and Jade through social media. | Dominic manipulates their emotional state by sending fake “support” messages that prompt them to forward Helix confidential info to an external “advisor.” |
| **N** | **Evelyn Hartley** | Compliance – Lead | *By‑the‑book* → She follows audit procedures to the letter, leaving no room for gray areas. | Maya tricks Evelyn into approving a “compliance drill” that is actually a cover for data exfiltration; the drill’s logs are later used as evidence of Helix’s negligence. *Dominic exploits her rigid adherence to rules.* |
| **O** | **Nadia Khatri** | IT Security – Social Engineering Lead | *Tech‑centric* → She relies on code, not people. | Dominic hijacks Nadia’s training module to embed a “social engineering exercise” that secretly teaches Mira and Jade how to manipulate Helix employees. |
| **P** | **Captain Rowan Ellis** | Physical Security – Head | *Procedure‑driven* → He never questions the status quo of security protocols. | Maya arranges a “security drill” where Rowan authorizes temporary access for a “trusted partner”; Dominic uses this window to plant a USB drive in Helix’s server room. |
| **Q** | **Lydia Bennett** | PR – Head | *Perception‑first* → She will spin any story that protects Helix’s brand, even if it means ignoring facts. | Maya coerces Lydia into issuing a “pre‑emptive warning” about a potential data breach; the message spreads through media and triggers market panic. *Dominic exploits her vanity and desire for control of the narrative.* |
| **R** | **Gareth Vale** | Finance – CFO | *Financial indiscretion* → He has a history of off-balance-sheet transactions for personal gain. | Dominic bribes Gareth with “confidential investment opportunities”; Gareth approves a fake profit entry that inflates Helix’s valuation, giving Dominic leverage to negotiate the acquisition at a lower price. *Dominic uses his greed and desperation.* |

---

### 4. Entry Points & Operational Flow (Revised)

| Phase | Action | Actor | Outcome |
|-------|--------|-------|---------|
| **1 – Infiltration** | Dominic poses as an external FinTech consultant for “Helix Advisory.” *He also uses a proxy to attend after-work socials, gathering intel and identifying vulnerable targets.* | Dominic (masked) + Proxy | Gains temporary admin rights to Helix’s internal network. Establishes initial contacts with key personnel. |
| **2 – Data Planting** | Deploys a benign‑looking “patch” via Jade; installs spyware on Mira’s workstation. *Simultaneously, plants hidden cameras in the executive lounge.* | Maya + Dominic | Allows real-time exfiltration of confidential files. Provides visual evidence for blackmail and manipulation. |
| **3 – Human‑Factor Leverage** | Uses Maya to manipulate Simon, Alex, and Katrina into sending sensitive info over unsecured channels. *Exploits power dynamics and sexual tension at after-work events.* | Maya | Creates multiple data leak vectors. |
| **4 – Corporate Sabotage** | Triggers a false audit (Evelyn) that forces Helix’s leadership to halt the acquisition talks temporarily. | Dominic + Evelyn | Delays takeover; lowers market confidence. |
| **5 – Financial Disruption** | Gareth approves a fabricated profit entry, inflating Helix’s valuation by 8%. *Dominic uses compromising photos of Gareth with a minor to ensure compliance.* | Dominic + Gareth | Gives Dominic bargaining power for a discounted buy‑out. |
| **6 – Public Fallout** | Lydia issues a “potential breach” statement; media coverage spikes. *The story is amplified by MP Beaumont’s social media channels.* | Lydia (coerced) | Market panic reduces Helix share price by 15%. |

---

### 5. Internal Response (Helix’s Countermeasures) – Weakened

1. **Red Team Audits** – Randomized penetration tests every quarter. *Often compromised due to insider collusion.*
2. **Data Integrity Council** – Monitors anomalies in key financial reports; triggered by Chloe’s erroneous line. *Understaffed and lacks authority.*
3. **Whistleblower Hotline** – Anonymous reporting channel that Dominic attempts to hijack via Nadia’s training module. *Known to be monitored by HR, discouraging genuine whistleblowing.*
4. **Crisis PR Playbook** – Automatically drafts statements when share price drops >10%; Lydia is forced to issue a “pre‑emptive warning.” *The playbook is outdated and ineffective.*

---


```
---

## Example implementation python code

```python

from typing import Dict, Any

from nikhil.amsha.toolkit.crew_forge.orchestrator.file.amsha_crew_file_application import AmshaCrewFileApplication
from nikhil.amsha.toolkit.llm_factory.domain.llm_type import LLMType

from src.enovel.application.config.settings import Settings


class GeneratePlotApplication(AmshaCrewFileApplication):

    def __init__(self, config_paths: Dict[str, str],llm_type:LLMType):

        super().__init__(config_paths, llm_type)


    def run(self) -> Any:
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
                pipeline_input["novel_blueprint"] = next_input
                print(f"{class_name} - pipeline_input:{pipeline_input}")
                result = self.orchestrator.run_crew(
                    crew_name=crew_name,
                    inputs=pipeline_input
                )
                output_file = self.orchestrator.get_last_output_file()
                if output_file:
                    print(f"{class_name}:{output_file}")
                    self.clean_json(output_file)


                results_for_list.append(result)
            pipeline_results[crew_name] = results_for_list
        return pipeline_results


if __name__ == "__main__":
    # Configuration is now neatly defined in one place.
    configs = {
        "llm": Settings.LLM_CONFIG,
        "app": Settings.APP_CONFIG,
        "job": "config/job_config.yaml"
    }

    # The main script is now incredibly simple and clean.
    app = GeneratePlotApplication(config_paths=configs,llm_type=LLMType.CREATIVE)
    app.run()
```
---

## How the Agent Uses These Sections

1. **Solutions Architect**  
   *Reads* `Job Config` → decides which crew(s) to create.  
   *Copies* the skeleton of a job config, then populates `knowledge_sources`, `input`, and `steps` based on user prompts.

2. **Senior Python Engineer**  
   *Uses* the **Task File** and **Agent File** examples to write new YAML files that satisfy the schema.  
   *Ensures* the generated Python wrapper follows the Amsha convention (inheritance, LLM type, etc.).

3. **Config Optimizer**  
   When a critique mentions “tone is too casual,” it will open the relevant `agents.yaml`/`tasks.yaml`, adjust the temperature or re‑phrase prompts, and write back – never touching `.py`.

4. **QA Specialist**  
   Loads the generated files, runs static checks (YAML validity, JSON schema compliance), and verifies that all required keys are present.

---

## 4️⃣  Additional Sections to Add in Future

| Section | Why it matters |
|---------|----------------|
| `validation_rules.yaml` | A reusable set of rules (e.g., “all character names must be unique”) that the QA agent can enforce. |
| `performance_profile.md` | Guidelines for setting temperature, max tokens, and retry strategies per use‑case. |
| `logging_template.md` | Standardized log messages to aid debugging when a crew fails. |
| `error_handling_strategy.md` | A checklist of how to recover from common LLM errors (e.g., hallucination, token limit). |

Add these as separate Markdown or YAML files in the `knowledge/` folder and reference them in any new job config.  The agents will treat them just like any other knowledge source.

---

### Bottom line

With this meta‑knowledge base you give each CrewGen agent a **template‑driven, example‑rich playground**.  
The result is:

* Consistent file structures across all generated crews.  
* Fewer runtime errors (thanks to the QA checks).  
* Faster iteration because agents can copy/paste and tweak instead of inventing every field from scratch.

Drop the snippets into your repo, add them as knowledge sources, and let CrewGen produce *production‑ready* code that looks just like what you already hand‑craft.
