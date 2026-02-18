# Crew Forge: Mathematical Foundations

This document formalizes the logical and structural operations within the `crew_forge` module. While the module is primarily architectural, its core function—the composition of autonomous agents into a cohesive crew—can be modeled using Set Theory.

## 1. Set-Theoretic Construction of Multi-Agent Systems

The `CrewBuilderService` orchestrates the assembly of a Crew from discrete Agent and Task entities. This process is formally modeled as a constructive set operation.

### Code Verification
- **Source:** `src/nikhil/amsha/crew_forge/service/crew_builder_service.py`
- **Lines:** 35-51 (`add_agent`), 53-74 (`add_task`), 76-88 (`build`)

### Formalization

Let $\mathcal{A}$ be the universe of all possible Agents and $\mathcal{T}$ be the universe of all possible Tasks.

A **Crew** $\mathcal{C}$ is defined as a 3-tuple:

$$
\mathcal{C} = (A, T, P)
$$

Where:
- $A \subseteq \mathcal{A}$ is the ordered set of agents: $A = \{a_1, a_2, \dots, a_n\}$
- $T \subseteq \mathcal{T}$ is the ordered set of tasks: $T = \{t_1, t_2, \dots, t_m\}$
- $P$ is the execution process (Sequential or Hierarchical)

### Construction Algorithm

The construction function $Build$ is an accumulation process over the state $S_i = (A_i, T_i)$:

$$
S_{i+1} = \begin{cases}
(A_i \cup \{a\}, T_i) & \text{if operation is add\_agent}(a) \\
(A_i, T_i \cup \{t\}) & \text{if operation is add\_task}(t)
\end{cases}
$$

The final `build()` validation enforces:

$$
|A| \ge 1 \land |T| \ge 1
$$

### Complexity Analysis
- **Time Complexity:** $O(1)$ for each add operation (amortized). Total construction time is $O(|A| + |T|)$.
- **Space Complexity:** $O(|A| + |T|)$ to store the references.

### Variable Mapping

| LaTeX Symbol | Code Variable | Description |
| :--- | :--- | :--- |
| $A$ | `self._agents` | List of Agent objects |
| $T$ | `self._tasks` | List of Task objects |
| $P$ | `process` | Execution Process Enum |
| $a$ | `agent` | Single Agent instance |
| $t$ | `task` | Single Task instance |

---

## 2. Text Normalization for Configuration

The `CrewParser` implements a normalization algorithm to sanitise multi-line YAML inputs (goals and backstories) into single-line descriptors required for LLM context windows.

### Code Verification
- **Source:** `src/nikhil/amsha/crew_forge/seeding/parser/crew_parser.py`
- **Lines:** 11-14 (`clean_multiline_string`)

### Formalization

Let $S$ be the input string containing potential whitespace irregularities (newlines, tabs). We define a transformation function $f_{norm}: \Sigma^* \to \Sigma^*$:

$$
f_{norm}(S) = \text{trim}(R_2(R_1(S)))
$$

Where $R_1$ and $R_2$ are regular expression substitution operators:

$$
R_1(S) : S \xrightarrow{[\setminus n \setminus t]+} \text{" "} \quad \text{(Replace newlines/tabs with space)}
$$

$$
R_2(S) : S \xrightarrow{\setminus s\{2,\}} \text{" "} \quad \text{(Collapse multiple spaces)}
$$

### Complexity Analysis
- **Time Complexity:** $O(L)$ where $L$ is the length of the string, as regex pass is linear.
- **Space Complexity:** $O(L)$ to store the new string.

---

## 3. Database Indexing Logic

The `MongoRepository` enforces uniqueness through compound indexing, formally ensuring data integrity.

### Code Verification
- **Source:** `src/nikhil/amsha/crew_forge/repo/adapters/mongo/mongo_repository.py`
- **Lines:** 34-42 (`create_unique_compound_index`)

### Formalization

Let $K = \{k_1, k_2, \dots, k_r\}$ be the set of keys for the index. The database enforces a uniqueness constraint $Unq$ on the collection $D$:

$$
\forall d_i, d_j \in D, i \neq j \implies \pi_K(d_i) \neq \pi_K(d_j)
$$

Where $\pi_K(d)$ is the projection of document $d$ onto the keys $K$.

### Variable Mapping

| LaTeX Symbol | Code Variable | Description |
| :--- | :--- | :--- |
| $K$ | `keys` | List of field names for index |
| $D$ | `self.collection` | MongoDB Collection |
| $\pi_K(d)$ | Document fields | The values of the specified keys |
