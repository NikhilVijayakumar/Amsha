# Crew Forge Module - Mathematical Foundations

## Overview
The `crew_forge` module implements the Repository Pattern for agent and task management   with clean separation between domain logic and persistence adapters. This document formalizes the core algorithms and data flow patterns.

---

## 1. Repository Pattern - Generic CRUD Operations

### Algorithm: Find One

**Source:** [`i_repository.py:13-15`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/repo/interfaces/i_repository.py#L13-L15)

**Purpose:** Retrieve a single document matching a query predicate.

**Logical Formalization:**

$$
\text{findOne}: \mathcal{Q} \rightarrow \mathcal{D} \cup \{\emptyset\}
$$

where:
- $\mathcal{Q}$ = set of all possible query predicates (dictionaries)
- $\mathcal{D}$ = set of all documents in the collection
- $\emptyset$ = null/not found

**Implementation Logic:**
```python
def find_one(self, query: dict) -> Optional[Any]:
    return self.collection.find_one(query)
```

**Variable Mapping:**

| LaTeX Symbol | Code Variable | Description |
|:-------------|:--------------|:------------|
| $\mathcal{Q}$ | `query: dict` | Query predicate |
| $\mathcal{D}$ | `Any` | Document type |
| $\emptyset$ | `None` | Not found |

**Complexity:** $O(n)$ where $n$ is the number of documents (worst case: linear scan without index)

---

### Algorithm: Find Many

**Source:** [`i_repository.py:17-19`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/repo/interfaces/i_repository.py#L17-L19)

**Purpose:** Retrieve all documents matching a query predicate.

**Logical Formalization:**

$$
\text{findMany}: \mathcal{Q} \rightarrow \mathcal{P}(\mathcal{D})
$$

where:
- $\mathcal{P}(\mathcal{D})$ = power set of documents (list of matching documents)

**Implementation Logic:**
```python
def find_many(self, query=None) -> List[Any]:
    if query is None:
        query = {}
    return list(self.collection.find(query))
```

**Variable Mapping:**

| LaTeX Symbol | Code Variable | Description |
|:-------------|:--------------|:------------|
| $\mathcal{Q}$ | `query: dict` | Query predicate |
| $\mathcal{P}(\mathcal{D})$ | `List[Any]` | Result set |

**Complexity:** $O(n + k)$ where $n$ is total documents and $k$ is the result size

---

### Algorithm: Insert One

**Source:** [`i_repository.py:21-23`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/repo/interfaces/i_repository.py#L21-L23)

**Purpose:** Insert a single document into the collection.

**Logical Formalization:**

$$
\text{insertOne}: \mathcal{D}' \rightarrow \mathcal{D} \cup \{\text{InsertResult}\}
$$

where:
- $\mathcal{D}'$ = document to insert (without ID)
- $\mathcal{D}$ = persisted document (with generated ID)

**Implementation Logic:**
```python
def insert_one(self, data: dict) -> Any:
    return self.collection.insert_one(data)
```

**Complexity:** $O(1)$ amortized (MongoDB index update is logarithmic)

---

### Algorithm: Update One

**Source:** [`i_repository.py:25-27`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/repo/interfaces/i_repository.py#L25-L27)

**Purpose:** Update a single document matching the query.

**Logical Formalization:**

$$
\text{updateOne}: \mathcal{Q} \times \mathcal{U} \rightarrow \{\text{UpdateResult}\}
$$

where:
- $\mathcal{U}$ = update specification (partial document)

**MongoDB Update Operator:**
```python
def update_one(self, query: dict, data: dict) -> Any:
    return self.collection.update_one(query, {"$set": data})
```

**$set Operator Semantics:**

$$
\mathcal{D}_{\text{new}} = \mathcal{D}_{\text{old}} \oplus \mathcal{U}
$$

where $\oplus$ denotes field-level merge (overwrite matching fields, preserve others).

**Complexity:** $O(\log n)$ with index on query field

---

### Algorithm: Delete One

**Source:** [`i_repository.py:29-31`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/repo/interfaces/i_repository.py#L29-L31)

**Purpose:** Remove a single document matching the query.

**Logical Formalization:**

$$
\text{deleteOne}: \mathcal{Q} \rightarrow \{\text{true}, \text{false}\}
$$

**Implementation Logic:**
```python
def delete_one(self, query: dict) -> bool:
    return self.collection.delete_one(query)
```

**Complexity:** $O(\log n)$ with index

---

## 2. Atomic Crew Builder - Incremental Construction

### Algorithm: Build Atomic Crew

**Source:** [`atomic_crew_db_manager.py:43-116`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/orchestrator/db/atomic_crew_db_manager.py#L43-L116)

**Purpose:** Incrementally construct a crew by fetching agents and tasks from the repository and assembling them into a CrewAI `Crew` object.

**Logical Formalization:**

Let:
- $A = \{a_1, a_2, \ldots, a_n\}$ = set of agent IDs
- $T = \{t_1, t_2, \ldots, t_m\}$ = set of task IDs
- $\text{Steps} = [(t_i, a_j, K_i)]$ = ordered list of (task_id, agent_id, knowledge_sources)

**Crew Construction:**

$$
\text{Crew} = \bigcup_{i=1}^{m} (\text{Agent}(a_i) \bowtie \text{Task}(t_i) \bowtie \text{Knowledge}(K_i))
$$

where $\bowtie$ denotes relational join (task assigned to agent with knowledge).

**Pseudo-Algorithm:**

```
FOR each step in crew_def['steps']:
    agent_id ← fetch from master_blueprint.agents[agent_key]
    task_id ← fetch from master_blueprint.tasks[task_key]
    knowledge_paths ← step.get('knowledge_sources', [])
    
    crew_builder.add_agent(agent_id, knowledge_sources)
    crew_builder.add_task(task_id, agent, output_filename)
END FOR

RETURN crew_builder.build(knowledge_sources=crew_level_knowledge)
```

**Variable Mapping:**

| LaTeX Symbol | Code Variable | Description |
|:-------------|:--------------|:------------|
| $A$ | `master_blueprint.agents` | Agent registry |
| $T$ | `master_blueprint.tasks` | Task registry |
| $\text{Steps}$ | `crew_def['steps']` | Job config steps |
| $K_i$ | `knowledge_sources` | Knowledge file paths |

**Time Complexity:**

$$
T(m, k) = O(m \cdot (L_a + L_t + k))
$$

where:
- $m$ = number of steps
- $L_a$ = agent lookup time (database query)
- $L_t$ = task lookup time (database query)
- $k$ = number of knowledge files to load

**Space Complexity:** $O(m \cdot k)$ for storing agents, tasks, and knowledge embeddings.

---

## 3. Unique Compound Index Creation

### Algorithm: Create Unique Compound Index

**Source:** [`mongo_repository.py:34-42`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/repo/adapters/mongo/mongo_repository.py#L34-L42)

**Purpose:** Enforce uniqueness constraint across multiple fields.

**Logical Formalization:**

Given a list of keys $K = [k_1, k_2, \ldots, k_n]$, create an index:

$$
\text{Index}(K) = \{(d[k_1], d[k_2], \ldots, d[k_n]) \mid d \in \mathcal{D}\}
$$

with uniqueness constraint:

$$
\forall d_i, d_j \in \mathcal{D}, \, i \neq j \implies \exists k \in K : d_i[k] \neq d_j[k]
$$

**Implementation Logic:**
```python
def create_unique_compound_index(self, keys: list[str]):
    if not keys:
        raise ValueError("List of keys cannot be empty.")
    index_keys = [(key, pymongo.ASCENDING) for key in keys]
    self.collection.create_index(index_keys, unique=True)
```

**Complexity:** $O(n \log n)$ for initial index build on $n$ documents.

---

## Summary

| Algorithm | Time Complexity | Space Complexity | Source |
|:----------|:---------------:|:----------------:|:-------|
| Find One | $O(n)$ | $O(1)$ | `i_repository.py:13` |
| Find Many | $O(n + k)$ | $O(k)$ | `i_repository.py:17` |
| Insert One | $O(1)$ | $O(1)$ | `i_repository.py:21` |
| Update One | $O(\log n)$ | $O(1)$ | `i_repository.py:25` |
| Delete One | $O(\log n)$ | $O(1)$ | `i_repository.py:29` |
| Build Atomic Crew | $O(m \cdot (L_a + L_t + k))$ | $O(m \cdot k)$ | `atomic_crew_db_manager.py:43` |
| Create Compound Index | $O(n \log n)$ | $O(n)$ | `mongo_repository.py:34` |

**Total:** 7 algorithms formalized with strict code traceability.
