# Novelty Analyst

**Category:** Paper Publishing  
**Type:** Analysis Agent  
**Invoked By:** Journal Master (Lutapi)

---

## Purpose

Analyzes **academic and scientific novelty** of code modules to ensure research papers have clear, defensible contributions. Complements `research-gap-analyst` (which focuses on technical gaps) by evaluating scientific merit.

---

## Key Questions

1. What **novel insights** does this module contribute to the field?
2. What makes it **different** from existing frameworks/approaches?
3. What can be **learned** from this implementation that advances knowledge?

---

## Output

**File:** `docs/paper/modules/{module}/novelty.md`

**Contains:**
- Novelty classification (NOVEL/INCREMENTAL/STANDARD/NONE)
- Identified academic contributions
- Comparison with related work
- Novelty gaps
- Suggested research angles (if novelty is weak)

---

## Novelty Classification

| Status | Definition | Example |
|:-------|:-----------|:--------|
| **NOVEL** | New algorithm, original pattern, unsolved problem | O(log n) algorithm for distributed agent coordination |
| **INCREMENTAL** | Known technique in new context, measurable improvement | Repository pattern applied to multi-agent persistence |
| **STANDARD** | Textbook implementation, framework usage | Factory pattern for LLM instantiation |
| **NONE** | Utilities, boilerplate, configuration | JSON parsing helpers |

---

## Key Features

### 1. Honest Assessment
✅ Doesn't claim novelty where none exists  
✅ Identifies when implementation is STANDARD

### 2. Actionable Suggestions
✅ Proposes **empirical studies** to conduct  
✅ Suggests **methodological contributions** to extract  
✅ Recommends **comparative analyses** to perform

### 3. Publication Framing
✅ Provides publication-ready narrative templates  
✅ Recommends target venues (top-tier, workshops, tech reports)

---

## Example Output

### Module with INCREMENTAL Novelty

```markdown
## Identified Contributions

### Contribution 1: Conditional Instantiation for Cloud/Local Unification

**Type:** Architectural  
**Status:** INCREMENTAL  
**Confidence:** MEDIUM

**Claim:** Unifies cloud and local LLM providers through selective parameter injection.

**Evidence:** `llm_builder.py:20-46`

**Differentiation:**
- LangChain: Requires different classes for cloud vs. local
- AutoGen: Hardcodes provider-specific logic
- **Our approach:** Single interface, zero client-side changes

**Publication Angle:**
"Provider Abstraction for Multi-Environment LLM Deployment: A Conditional Factory Pattern"
```

### Module with STANDARD Classification + Suggestions

```markdown
## Novelty Classification

**Status:** STANDARD  
**Reason:** Textbook Repository pattern implementation

## Suggested Contributions

### Option 1: Empirical Study
"Performance Trade-offs: Repository Pattern Overhead in Multi-Agent Systems"
- Benchmark Repository vs. Direct DB access
- Measure query latency with 1K, 10K, 100K agents
- Identify optimal use cases based on scale

### Option 2: Methodological
"Protocol-Based Repository Design for Document Databases"
- Extract general pattern from implementation
- Create reusable template
- Document migration process from relational DBs

### Option 3: Comparative Analysis
"MongoDB Repository Patterns: Trade-off Analysis"
- Compare 3+ implementation approaches
- Measure coupling/cohesion metrics
- Provide decision framework for practitioners
```

---

## Integration with Paper Workflow

Runs as **Step 4 of 5** in Phase 1 (Module Analysis):

1. Math Extractor → algorithms
2. Visual Generator → diagrams
3. Research Gap Analyst → technical gaps
4. **Novelty Analyst** → academic contributions ⬅️
5. Summary Generator → synthesis

---

## Usage

**Not directly triggered.** Automatically invoked by Journal Master:

```
"Lutapi, analyze module crew_forge for the paper"
```

This command will:
- Run math-extractor
- Run visual-generator
- Run research-gap-analyst
- **Run novelty-analyst** (generates `novelty.md`)
- Generate summary

---

## Technical Details

**Skill Location:** `.agent/skills/novelty-analyst/SKILL.md`  
**Examples:** `.agent/skills/novelty-analyst/examples/novelty_examples.md`  
**Templates:** `.agent/skills/novelty-analyst/resources/related_work_template.md`

---

## Comparison: Technical vs. Academic Gaps

| Aspect | research-gap-analyst | novelty-analyst |
|:-------|:---------------------|:----------------|
| **Focus** | Technical completeness | Scientific contribution |
| **Checks** | Tests, benchmarks, docs | Algorithms, patterns, insights |
| **Output** | gaps.md | novelty.md |
| **Goal** | Make code production-ready | Make paper publication-worthy |
| **Example Gap** | "No unit tests (CRITICAL)" | "Novel contribution not identified" |
| **Example Fix** | Add pytest suite | Propose empirical comparison study |

**Both are essential** for Scopus-standard publication!

---

**Status:** ✅ Active  
**Added:** 2026-02-10  
**Version:** 1.0
