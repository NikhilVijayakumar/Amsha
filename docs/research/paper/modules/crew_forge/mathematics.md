# Crew Forge: Mathematical Foundations

This document formalizes the logical and structural operations within the `crew_forge` module. The module implements multi-layered compositional algorithms spanning set-theoretic crew construction, configuration synchronization with idempotent upsert logic, text normalization, document knowledge ingestion pipelines, and database integrity constraints.

---

## 1. Set-Theoretic Construction of Multi-Agent Systems

The `CrewBuilderService` orchestrates the assembly of a Crew from discrete Agent and Task entities using an incremental state-accumulation model.

### Code Verification
- **Source:** [crew_builder_service.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/service/crew_builder_service.py)
- **Lines:** L35–L51 (`add_agent`), L53–L74 (`add_task`), L76–L88 (`build`)

### Formalization

Let $\mathcal{A}$ be the universe of all possible Agents and $\mathcal{T}$ be the universe of all possible Tasks.

A **Crew** $\mathcal{C}$ is defined as a 4-tuple:

$$
\mathcal{C} = (A, T, P, K)
$$

Where:
- $A \subseteq \mathcal{A}$ is the ordered set of agents: $A = \{a_1, a_2, \dots, a_n\}$
- $T \subseteq \mathcal{T}$ is the ordered set of tasks: $T = \{t_1, t_2, \dots, t_m\}$
- $P \in \{\texttt{sequential}, \texttt{hierarchical}\}$ is the execution process
- $K$ is the optional set of knowledge sources attached at crew level

Each agent $a_i$ is itself a structured tuple drawn from a domain model:

$$
a_i = (\texttt{role}_i, \texttt{goal}_i, \texttt{backstory}_i, \texttt{llm}, \texttt{tools}_i, K_i^{agent})
$$

Each task $t_j$ associates to exactly one agent and an optional output file:

$$
t_j = (\texttt{name}_j, \texttt{desc}_j, \texttt{expected}_j, a_{k}, f_j^{out})
$$

### Construction Algorithm (State Machine)

The construction function $Build$ is an accumulation process over state $S_i = (A_i, T_i, F_i)$ where $F_i$ is the output-file registry:

$$
S_{i+1} = \begin{cases}
(A_i \cup \{a\}, T_i, F_i) & \text{if operation is } \texttt{add\_agent}(a) \\
(A_i, T_i \cup \{t\}, F_i \cup \{f_t\}) & \text{if operation is } \texttt{add\_task}(t, f_t)
\end{cases}
$$

The final `build()` enforces the precondition:

$$
\texttt{Valid}(S) \iff |A| \ge 1 \land |T| \ge 1
$$

### Output Path Generation

The output directory path is computed via a timestamped composition function:

$$
\texttt{out\_dir} = \texttt{base} \oplus \texttt{"/output/"} \oplus \texttt{module\_name} \oplus \texttt{"/output\_"} \oplus \tau(t)
$$

Where $\tau(t) = \texttt{strftime}(\texttt{"\%Y\%m\%d\%H\%M\%S"}, t)$ provides temporal uniqueness.

### Complexity Analysis
- **Time Complexity:** $O(1)$ per add operation (amortized). Total construction: $O(|A| + |T|)$.
- **Space Complexity:** $O(|A| + |T| + |F|)$ for agents, tasks, and output file references.

### Variable Mapping

| LaTeX Symbol | Code Variable | File | Line |
| :--- | :--- | :--- | :--- |
| $A$ | `self._agents` | `crew_builder_service.py` | L24 |
| $T$ | `self._tasks` | `crew_builder_service.py` | L25 |
| $F$ | `self.output_files` | `crew_builder_service.py` | L26 |
| $P$ | `process` | `crew_builder_service.py` | L76 |
| $K$ | `knowledge_sources` | `crew_builder_service.py` | L76 |
| $\tau(t)$ | `time.strftime(...)` | `crew_builder_service.py` | L19 |

---

## 2. Dual-Backend Facade Resolution (Strategy Pattern)

The module provides two interchangeable facades for crew construction: `AtomicDbBuilderService` (database-backed) and `AtomicYamlBuilderService` (file-backed). Both delegate to `CrewBuilderService`, implementing a Strategy-like pattern.

### Code Verification
- **DB:** [atomic_db_builder.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/service/atomic_db_builder.py) (L23–L29)
- **YAML:** [atomic_yaml_builder.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/service/atomic_yaml_builder.py) (L19–L23)

### Formalization

Define a **Resolution Function** $\rho$ that maps external identifiers to internal domain models:

$$
\rho_{DB}(id) = \texttt{repo.get\_by\_id}(id) \longrightarrow D_{\text{internal}}
$$

$$
\rho_{YAML}(file) = \texttt{parser.parse}(file) \longrightarrow D_{\text{internal}}
$$

Both resolution functions produce the same internal representation $D_{\text{internal}} \in \{\texttt{AgentRequest}, \texttt{TaskRequest}\}$, satisfying the Backend Invariant:

$$
\forall x_{DB}, x_{YAML} : \rho_{DB}(x_{DB}) \cong \rho_{YAML}(x_{YAML}) \implies \texttt{Build}(\rho_{DB}) \equiv \texttt{Build}(\rho_{YAML})
$$

This ensures **behavioral equivalence** regardless of the data source.

### Complexity Analysis
- **DB Backend:** $O(|A| + |T|)$ network round-trips to MongoDB.
- **YAML Backend:** $O(|A| + |T|)$ file I/O operations plus YAML parsing.

---

## 3. Blueprint-Driven Atomic Crew Assembly

The `AtomicCrewDBManager` and `AtomicCrewFileManager` implement a **Blueprint Pattern** — a master configuration document defines the full Crew topology, and individual atomic crews are materialized from subsets.

### Code Verification
- **DB Manager:** [atomic_crew_db_manager.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/orchestrator/db/atomic_crew_db_manager.py) (L43–L116)
- **File Manager:** [atomic_crew_file_manager.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/orchestrator/file/atomic_crew_file_manager.py) (L33–L100)

### Formalization

Let $\mathcal{B} = (name, usecase, \mathcal{M}_A, \mathcal{M}_T)$ be the master Blueprint, where:
- $\mathcal{M}_A : \texttt{key} \to \texttt{agent\_id}$ is the agent key-to-ID map
- $\mathcal{M}_T : \texttt{key} \to \texttt{task\_id}$ is the task key-to-ID map

A **Job Configuration** $J$ defines a set of atomic crew definitions:

$$
J = \{c_1, c_2, \dots, c_p\} \quad \text{where } c_i = (\texttt{name}_i, \texttt{steps}_i, K_i^{crew})
$$

Each step $s \in \texttt{steps}_i$ specifies:

$$
s = (\texttt{task\_key}, \texttt{agent\_key}, K_s^{agent})
$$

The **Materialization Function** $\mathcal{M}$ for DB-backed assembly:

$$
\mathcal{M}_{DB}(c_i, \mathcal{B}) = \texttt{Build}\left( \bigcup_{s \in \text{steps}_i} \rho_{DB}\left(\mathcal{M}_A[s.\texttt{agent\_key}]\right), \rho_{DB}\left(\mathcal{M}_T[s.\texttt{task\_key}]\right) \right)
$$

With knowledge augmentation:

$$
\mathcal{M}_{DB}^{+}(c_i, \mathcal{B}) = \mathcal{M}_{DB}(c_i, \mathcal{B}) \oplus \texttt{Docling}(K_s^{agent}) \oplus \texttt{Docling}(K_i^{crew})
$$

### Complexity Analysis
- **Time:** $O(|steps| \times (T_{lookup} + T_{agent\_create}))$ per crew.
- **Space:** $O(|steps|)$ for agent/task references plus $O(|K|)$ for knowledge chunks.

---

## 4. Idempotent Configuration Synchronization (DatabaseSeeder)

The `DatabaseSeeder` implements an idempotent synchronization algorithm that reconciles YAML-defined agent/task configurations with the MongoDB backend, following a three-phase UPSERT strategy.

### Code Verification
- **Source:** [database_seeder.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/seeding/database_seeder.py)
- **Lines:** L38–L63 (`_collect_configs_from_path`), L72–L94 (`_synchronize_agents`), L96–L119 (`_synchronize_tasks`), L121–L141 (`_synchronize_crew`)

### Formalization

**Phase 1 — Collection:** A recursive filesystem traversal $\mathcal{W}$ collects configurations:

$$
\mathcal{W}(root) = \bigcup_{d \in \text{walk}(root)} \begin{cases}
\texttt{usecase\_map}[u].\texttt{agents} \cup \{(k, \texttt{parse}(f))\} & \text{if } d = \texttt{agents/} \\
\texttt{usecase\_map}[u].\texttt{tasks} \cup \{(k, \texttt{parse}(f))\} & \text{if } d = \texttt{tasks/}
\end{cases}
$$

Where $u = \text{relpath}(d, root).\text{split}(\texttt{sep})[0]$ extracts the use-case identifier.

**Phase 2 — Upsert Decision:** For each entity $e$ with unique key $(role, usecase)$ or $(name, usecase)$:

$$
\delta(e) = \begin{cases}
\texttt{CREATE}(e) & \text{if } \nexists\, e' \in DB : \texttt{key}(e') = \texttt{key}(e) \\
\texttt{UPDATE}(e) & \text{if } \exists\, e' \in DB : \texttt{key}(e') = \texttt{key}(e) \land \texttt{fields}(e') \neq \texttt{fields}(e) \\
\texttt{SKIP} & \text{if } \exists\, e' \in DB : \texttt{key}(e') = \texttt{key}(e) \land \texttt{fields}(e') = \texttt{fields}(e)
\end{cases}
$$

**Phase 3 — Crew Assembly:** After agents and tasks are synchronized, a `CrewConfigRequest` is created from the resulting ID maps:

$$
\texttt{CrewConfig}(u) = \left(\texttt{name}(u), \bigcup_{a \in A_u} \texttt{id}(a), \bigcup_{t \in T_u} \texttt{id}(t)\right)
$$

### Idempotency Proof

The synchronization is **idempotent**: $\delta^n(e) = \delta^1(e)$ for $n \geq 1$, because:
1. If no changes exist, the SKIP branch is taken.
2. After an UPDATE, `fields(e') = fields(e)`, so subsequent calls yield SKIP.
3. After a CREATE, the entity exists, so subsequent calls yield UPDATE or SKIP.

### Complexity Analysis
- **Time:** $O(|F| \times T_{parse} + |E| \times T_{db\_lookup})$ where $|F|$ = files, $|E|$ = entities.
- **Space:** $O(|E|)$ for the use-case map plus ID maps.

---

## 5. Text Normalization for LLM Context Windows

The `CrewParser` implements a two-pass normalization algorithm to sanitize multi-line YAML strings into single-line descriptors optimized for LLM prompt injection.

### Code Verification
- **Source:** [crew_parser.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/seeding/parser/crew_parser.py) (L10–L14)

### Formalization

Let $S$ be the input string. The transformation $f_{norm}: \Sigma^* \to \Sigma^*$:

$$
f_{norm}(S) = \text{trim}(R_2(R_1(S)))
$$

Where:

$$
R_1(S) : S \xrightarrow{[\backslash n \backslash t]+} \text{" "} \quad \text{(Replace newlines/tabs with space)}
$$

$$
R_2(S) : S \xrightarrow{\backslash s\{2,\}} \text{" "} \quad \text{(Collapse multiple spaces)}
$$

### Properties
- **Idempotent:** $f_{norm}(f_{norm}(S)) = f_{norm}(S)$
- **Length-preserving bound:** $|f_{norm}(S)| \leq |S|$

### Complexity Analysis
- **Time:** $O(L)$ where $L = |S|$, as each regex pass is linear.
- **Space:** $O(L)$ for the new string.

---

## 6. Hierarchical Document Chunking (Knowledge Source Pipeline)

The `AmshaCrewDoclingSource` implements a multi-format document ingestion pipeline with hierarchical chunking for RAG (Retrieval-Augmented Generation) integration.

### Code Verification
- **Source:** [amsha_crew_docling_source.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/knowledge/amsha_crew_docling_source.py)
- **Lines:** L68–L77 (`_load_content`), L90–L92 (`_convert_source_to_docling_documents`), L94–L97 (`_chunk_doc`)

### Formalization

Let $\mathcal{F} = \{f_1, f_2, \dots, f_k\}$ be the set of validated input file paths supporting formats $\Phi = \{\texttt{MD}, \texttt{PDF}, \texttt{DOCX}, \texttt{HTML}, \texttt{IMAGE}, \texttt{XLSX}, \texttt{PPTX}\}$.

The ingestion pipeline is a three-stage composition:

**Stage 1 — Validation:** $V: \mathcal{F} \to \mathcal{F}_{safe}$

$$
V(f) = \begin{cases}
f & \text{if } f \text{ is local } \land \exists f \\
f & \text{if } f \text{ is URL } \land \texttt{valid\_url}(f) \\
\bot & \text{otherwise (raise error)}
\end{cases}
$$

**Stage 2 — Conversion:** $C: \mathcal{F}_{safe} \to \mathcal{D}$

$$
C(\mathcal{F}_{safe}) = \left\{ \texttt{DoclingDocument}(f) \mid f \in \mathcal{F}_{safe} \right\}
$$

**Stage 3 — Chunking:** $H: \mathcal{D} \to \mathcal{X}$

$$
H(d) = \bigoplus_{c \in \texttt{HierarchicalChunker}(d)} c.\texttt{text}
$$

The full pipeline:

$$
\texttt{Knowledge}(\mathcal{F}) = \bigcup_{d \in C(V(\mathcal{F}))} H(d)
$$

### URL Validation Predicate

$$
\texttt{valid\_url}(u) \iff \texttt{scheme}(u) \in \{http, https\} \land |\texttt{netloc}(u).\texttt{split}('.')| \geq 2
$$

### Complexity Analysis
- **Time:** $O(|\mathcal{F}| \times T_{convert} + |\mathcal{D}| \times T_{chunk})$. Conversion is document-size-dependent.
- **Space:** $O(\sum |C_i|)$ where $|C_i|$ is the chunk count per document.

---

## 7. Compound Index Integrity Constraint

The `MongoRepository` enforces uniqueness through compound database indexing.

### Code Verification
- **Source:** [mongo_repository.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/repo/adapters/mongo/mongo_repository.py) (L34–L42)

### Formalization

Let $K = \{k_1, k_2, \dots, k_r\}$ be the set of keys for the index. The uniqueness constraint $Unq$ on collection $D$:

$$
\forall d_i, d_j \in D, i \neq j \implies \pi_K(d_i) \neq \pi_K(d_j)
$$

Where $\pi_K(d)$ is the projection of document $d$ onto keys $K$.

Applied instances:
- `AgentRepository`: $K = \{\texttt{role}, \texttt{usecase}\}$
- `TaskRepository`: $K = \{\texttt{name}, \texttt{usecase}\}$
- `CrewConfigRepository`: $K = \{\texttt{name}, \texttt{usecase}\}$

### Variable Mapping

| LaTeX Symbol | Code Variable | File | Line |
| :--- | :--- | :--- | :--- |
| $K$ | `keys` parameter | `mongo_repository.py` | L34 |
| $D$ | `self.collection` | `mongo_repository.py` | L12 |
| $\pi_K(d)$ | Document fields | `agent_repo.py` | L15 |

---

## 8. Dependency Injection Graph (Container Composition)

The DI system uses a two-tier container hierarchy: `MongoRepoContainer` (infrastructure) nested inside `CrewForgeContainer` (application).

### Code Verification
- **Source:** [crew_forge_container.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/dependency/crew_forge_container.py) (L15–L75)
- **Source:** [mongo_container.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/dependency/mongo_container.py) (L11–L44)

### Formalization

The DI graph $G = (V, E)$ can be modeled as a Directed Acyclic Graph where:

$$
V = \{\texttt{Config}, \texttt{MongoContainer}, \texttt{AgentRepo}, \texttt{TaskRepo}, \texttt{CrewRepo}, \texttt{Parser}, \texttt{Builder}_{core}, \texttt{Builder}_{DB}, \texttt{Builder}_{YAML}, \texttt{Blueprint}, \texttt{SyncService}\}
$$

$$
E = \{(\texttt{Config} \to \texttt{MongoContainer}), (\texttt{MongoContainer} \to \texttt{AgentRepo}), \dots\}
$$

The container uses three provider strategies:
- **Factory:** Creates new instance per request (`AtomicDbBuilderService`)
- **Singleton:** Shared instance (`CrewParser`)
- **Callable:** Deferred construction with lazy resolution (`CrewBluePrintService`)

### Lifecycle Guarantees
- $\forall t_1, t_2 : \texttt{Singleton}(t_1) = \texttt{Singleton}(t_2)$ (identity guarantee)
- $\forall t_1 \neq t_2 : \texttt{Factory}(t_1) \neq \texttt{Factory}(t_2)$ (isolation guarantee)

---

## Algorithm Index

| # | Algorithm | Source File | Lines | Complexity |
|---|-----------|------------|-------|------------|
| 1 | Crew Construction (Builder) | `crew_builder_service.py` | L35–L88 | $O(|A|+|T|)$ |
| 2 | Dual-Backend Resolution | `atomic_db_builder.py`, `atomic_yaml_builder.py` | L23–L29 | $O(|A|+|T|)$ |
| 3 | Blueprint Materialization | `atomic_crew_db_manager.py` | L43–L116 | $O(|steps| \times T_{lookup})$ |
| 4 | Idempotent Config Sync | `database_seeder.py` | L23–L141 | $O(|F| + |E| \times T_{db})$ |
| 5 | Text Normalization | `crew_parser.py` | L10–L14 | $O(L)$ |
| 6 | Document Chunking Pipeline | `amsha_crew_docling_source.py` | L68–L97 | $O(|\mathcal{F}| \times T_{convert})$ |
| 7 | Compound Index Enforcement | `mongo_repository.py` | L34–L42 | $O(|K|)$ |
| 8 | DI Container Resolution | `crew_forge_container.py` | L15–L75 | $O(|V| + |E|)$ |
