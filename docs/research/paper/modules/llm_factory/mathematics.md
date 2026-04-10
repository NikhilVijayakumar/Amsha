# LLM Factory: Mathematical Foundations

This document formalizes the algorithms within the `llm_factory` module, covering hierarchical configuration resolution, conditional provider instantiation, reflective telemetry interception, model name normalization, and the DI container's provider resolution graph.

---

## 1. Hierarchical Configuration Resolution

The `LLMSettings` class implements a two-level hierarchical lookup algorithm to resolve LLM configurations based on an abstract "Use Case" category and an optional model key override.

### Code Verification
- **Source:** [llm_settings.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/settings/llm_settings.py)
- **Lines:** L14–L28

### Formalization

Let $U = \{\texttt{creative}, \texttt{evaluation}\}$ be the set of use cases, and $M_u$ be the set of available model keys for each $u \in U$.

The complete configuration space is a nested dictionary:

$$
\mathcal{S} = \{ u \mapsto (\delta_u, \{ k \mapsto (m_k, b_k, a_k, v_k) \mid k \in M_u \}) \mid u \in U \}
$$

Where:
- $\delta_u$ = default model key for use case $u$
- $m_k$ = model identifier string (e.g., `"gemini/gemini-1.5-flash"`)
- $b_k$ = optional base URL ($\bot$ for cloud, URL for local)
- $a_k$ = API key
- $v_k$ = optional API version

The **resolution function** $\mathcal{R}: U \times M^? \to \texttt{LLMModelConfig}$:

$$
\mathcal{R}(u, k_{opt}) = \begin{cases}
\mathcal{S}[u].models[k_{opt}] & \text{if } k_{opt} \neq \bot \land k_{opt} \in M_u \\
\mathcal{S}[u].models[\delta_u] & \text{if } k_{opt} = \bot \\
\text{raise ValueError} & \text{if } u \notin U \lor k_{opt} \notin M_u
\end{cases}
$$

### Parameter Resolution

Independently, parameters are resolved per use case:

$$
\mathcal{P}(u) = \begin{cases}
\texttt{llm\_parameters}[u] & \text{if } u \in \texttt{llm\_parameters} \\
\texttt{LLMParameters}() & \text{otherwise (defaults)}
\end{cases}
$$

Default parameter values form the tuple:

$$
P_{default} = (\tau = 0.0,\; p_{top} = 1.0,\; T_{max} = 4096,\; \rho_{pres} = 0.0,\; \rho_{freq} = 0.0,\; \sigma = \bot)
$$

### Variable Mapping

| LaTeX Symbol | Code Variable | File | Line |
| :--- | :--- | :--- | :--- |
| $U$ | `self.llm` keys | `llm_settings.py` | L11 |
| $M_u$ | `use_case_config.models` | `llm_settings.py` | L20 |
| $\delta_u$ | `use_case_config.default` | `llm_settings.py` | L19 |
| $\mathcal{R}$ | `get_model_config()` | `llm_settings.py` | L14 |
| $\mathcal{P}$ | `get_parameters()` | `llm_settings.py` | L27 |
| $\tau$ | `temperature` | `state.py` | L11 |
| $p_{top}$ | `top_p` | `state.py` | L12 |
| $T_{max}$ | `max_completion_tokens` | `state.py` | L13 |
| $\rho_{pres}$ | `presence_penalty` | `state.py` | L14 |
| $\rho_{freq}$ | `frequency_penalty` | `state.py` | L15 |

### Complexity
- **Time:** $O(1)$ — Two hash-map lookups.
- **Space:** $O(|U| \times |M_{max}|)$ for configuration storage.

---

## 2. Conditional Provider Instantiation (Factory Method)

The `LLMBuilder.build()` method implements a conditional factory that produces LLM instances for either cloud-hosted or locally-served models based on the presence of a `base_url`.

### Code Verification
- **Source:** [llm_builder.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/service/llm_builder.py)
- **Lines:** L15–L48

### Formalization

The factory function $\mathcal{F}: \texttt{LLMType} \times M^? \to \texttt{LLMBuildResult}$:

$$
\mathcal{F}(u, k_{opt}) = \left( \mathcal{I}(\mathcal{R}(u, k_{opt}), \mathcal{P}(u)),\; \eta(\mathcal{R}(u, k_{opt}).model) \right)
$$

Where the instantiation function $\mathcal{I}$ branches on the base URL:

$$
\mathcal{I}(c, p) = \begin{cases}
\texttt{LLM}(api\_key=c.a,\; model=c.m,\; \tau=p.\tau,\; \dots) & \text{if } c.b = \bot \text{ (Cloud)} \\
\texttt{LLM}(base\_url=c.b,\; api\_key=c.a,\; model=c.m,\; \tau=p.\tau,\; \dots) & \text{if } c.b \neq \bot \text{ (Local)}
\end{cases}
$$

And $\eta$ is the model name extraction function (see §4).

### Provider Classification

The conditional logic implicitly classifies providers:

| Provider | `base_url` | Classification |
|:---------|:-----------|:--------------|
| LM Studio (phi, llama) | `http://localhost:1234/v1` | Local |
| Azure OpenAI | `https://*.openai.azure.com/` | Cloud (with base URL) |
| Google Gemini | $\bot$ | Cloud (API-only) |

### Pre-Factory Privacy Guard

Both convenience methods `build_creative()` and `build_evaluation()` invoke telemetry disabling **before** instantiation:

$$
\texttt{build\_creative}(k) = \texttt{disable\_telemetry}() \circ \mathcal{F}(\texttt{CREATIVE}, k)
$$

This ensures privacy protection is applied even if the caller forgets.

### Complexity
- **Time:** $O(1)$ for configuration + $O(T_{LLM})$ for provider initialization (network-bound).
- **Space:** $O(1)$ — Single `LLM` instance.

---

## 3. Reflective Telemetry Interception

The `LLMUtils.disable_telemetry()` method employs runtime reflection to dynamically neutralize all callable methods on the external CrewAI `Telemetry` class, combined with environment variable override.

### Code Verification
- **Source:** [llm_utils.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/utils/llm_utils.py)
- **Lines:** L10–L24

### Formalization

Let $T$ be the `Telemetry` class object and $\texttt{Attr}(T)$ the set of all its attributes.

**Step 1 — Environment Override:**

$$
\texttt{env}[\texttt{OTEL\_SDK\_DISABLED}] \leftarrow \texttt{"true"}
$$

**Step 2 — Method Replacement:** For each attribute $a \in \texttt{Attr}(T)$:

$$
T'.a = \begin{cases}
\lambda \texttt{*args, **kwargs}: \bot & \text{if } \texttt{callable}(a) \land \neg\texttt{startswith}(a, \texttt{"\_\_"}) \\
T.a & \text{otherwise}
\end{cases}
$$

### Properties

- **Completeness:** All non-dunder callable attributes are neutralized — no telemetry method can execute.
- **Idempotent:** $\texttt{disable}^n(T) = \texttt{disable}^1(T)$ since replacing a noop with noop is identity.
- **Non-Invasive:** No source code modification of CrewAI library required.
- **Dual Layer:** Both OTEL environment variable AND method patching provide defense-in-depth.

### Complexity
- **Time:** $O(|\texttt{Attr}(T)|)$ — Linear scan of class attributes.
- **Space:** $O(1)$ — In-place replacement.

---

## 4. Model Name Extraction (Prefix Normalization)

The `LLMUtils.extract_model_name()` method implements a prefix-stripping algorithm to convert provider-qualified model strings into clean display names.

### Code Verification
- **Source:** [llm_utils.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/utils/llm_utils.py)
- **Lines:** L26–L32

### Formalization

Let $\Pi = \{\texttt{"lm\_studio/"}, \texttt{"gemini/"}, \texttt{"open\_ai/"}, \texttt{"azure"}\}$ be the set of known prefixes.

The extraction function $\eta: \Sigma^* \to \Sigma^*$:

$$
\eta(s) = \begin{cases}
s[|\pi|:] & \text{if } \exists \pi \in \Pi : s.\texttt{startswith}(\pi) \\
s & \text{otherwise}
\end{cases}
$$

### Examples

| Input | Output | Matched Prefix |
|:------|:-------|:--------------|
| `"lm_studio/phi-4-reasoning"` | `"phi-4-reasoning"` | `"lm_studio/"` |
| `"gemini/gemini-1.5-flash"` | `"gemini-1.5-flash"` | `"gemini/"` |
| `"azure/gpt-4o"` | `"/gpt-4o"` | `"azure"` |
| `"custom-model"` | `"custom-model"` | (none) |

### Complexity
- **Time:** $O(|\Pi|)$ — Linear scan of prefix list (constant, $|\Pi| = 4$).
- **Space:** $O(1)$.

---

## 5. Pydantic Domain Model Validation

The module defines a 4-model Pydantic schema hierarchy that enforces type safety and provides sensible defaults for all configuration values.

### Code Verification
- **Source:** [state.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/domain/state.py) (L10–L34)

### Formalization

The model hierarchy forms a compositional type system:

$$
\texttt{LLMSettings} : \{ u \mapsto \texttt{LLMUseCaseConfig} \mid u \in U \} \times \{ u \mapsto \texttt{LLMParameters} \mid u \in U \}
$$

$$
\texttt{LLMUseCaseConfig} : (\delta : str, \; models : \{ k \mapsto \texttt{LLMModelConfig} \})
$$

$$
\texttt{LLMModelConfig} : (model : str, \; base\_url : str^?, \; api\_key : str^?, \; api\_version : str^?)
$$

$$
\texttt{LLMParameters} : (\tau : \mathbb{R}_{[0,2]}, \; p : \mathbb{R}_{[0,1]}, \; T : \mathbb{Z}^+, \; \rho_p : \mathbb{R}, \; \rho_f : \mathbb{R}, \; \sigma : [str]^?)
$$

The `LLMBuildResult` is a `NamedTuple` — an immutable product type:

$$
\texttt{LLMBuildResult} = \texttt{LLM} \times \texttt{str}
$$

### Validation Guarantees
- **Type safety:** Pydantic enforces field types at construction time.
- **Default propagation:** Missing `LLMParameters` fields use sensible defaults ($\tau=0, p=1, T=4096$).
- **Immutability:** `LLMBuildResult` (NamedTuple) is immutable after construction.

---

## 6. DI Container Provider Graph

The `LLMContainer` implements a declarative DI container with three provider strategies and **pre-wired convenience providers**.

### Code Verification
- **Source:** [llm_container.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/dependency/llm_container.py) (L10–L33)

### Formalization

The container's resolution graph $G = (V, E)$:

$$
V = \{\texttt{Config}, \texttt{YamlData}, \texttt{Settings}, \texttt{Builder}, \texttt{Creative}, \texttt{Evaluation}\}
$$

$$
E = \{(\texttt{Config} \to \texttt{YamlData}), (\texttt{YamlData} \to \texttt{Settings}), (\texttt{Settings} \to \texttt{Builder}), (\texttt{Builder} \to \texttt{Creative}), (\texttt{Builder} \to \texttt{Evaluation})\}
$$

Provider strategies:
- **Singleton:** `yaml_data`, `llm_settings` — Parsed once, shared across all requests.
- **Factory:** `llm_builder` — New instance per request.
- **Pre-wired:** `creative_llm`, `evaluation_llm` — Façade providers calling `builder.build_creative()` / `builder.build_evaluation()` directly.

### Resolution Sequence

$$
\texttt{Config.path} \xrightarrow{\text{Singleton}} \texttt{YamlData} \xrightarrow{\text{Singleton}} \texttt{Settings} \xrightarrow{\text{Factory}} \texttt{Builder} \xrightarrow{\text{call}} \texttt{LLMBuildResult}
$$

### Complexity
- **Time:** $O(1)$ for provider resolution (first call includes YAML parse: $O(|F|)$).
- **Space:** $O(|config|)$ for cached settings.

---

## Algorithm Index

| # | Algorithm | Source File | Lines | Complexity |
|---|-----------|------------|-------|------------|
| 1 | Hierarchical Config Resolution | `llm_settings.py` | L14–L28 | $O(1)$ |
| 2 | Conditional Provider Instantiation | `llm_builder.py` | L15–L48 | $O(1) + O(T_{LLM})$ |
| 3 | Reflective Telemetry Interception | `llm_utils.py` | L10–L24 | $O(|\texttt{Attr}(T)|)$ |
| 4 | Model Name Prefix Extraction | `llm_utils.py` | L26–L32 | $O(|\Pi|)$ |
| 5 | Pydantic Schema Validation | `state.py` | L10–L34 | $O(|fields|)$ |
| 6 | DI Container Resolution | `llm_container.py` | L10–L33 | $O(1)$ |
