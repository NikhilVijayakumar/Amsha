# LLM Factory Module - Mathematical Foundations

## Overview
The `llm_factory` module implements a multi-provider LLM instantiation system using the Factory Pattern. This document formalizes the configuration selection algorithm and model name extraction logic.

---

## 1. Factory Pattern - LLM Configuration Selection

### Algorithm: Get Model Config

**Source:** [`llm_settings.py:14-25`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/settings/llm_settings.py#L14-L25)

**Purpose:** Select the appropriate model configuration based on use case and optional model key.

**Logical Formalization:**

Let:
- $\mathcal{U} = \{\text{creative}, \text{evaluation}\}$ = set of use cases
- $\mathcal{M}_u$ = set of available models for use case $u \in \mathcal{U}$
- $d_u$ = default model key for use case $u$

**Function Definition:**

$$
\text{getModelConfig}: \mathcal{U} \times (\mathcal{M}_u \cup \{\emptyset\}) \rightarrow \text{ModelConfig}
$$

$$
\text{getModelConfig}(u, k) = \begin{cases}
\text{models}[u][k] & \text{if } k \neq \emptyset \\\\
\text{models}[u][d_u] & \text{if } k = \emptyset
\end{cases}
$$

**Implementation Logic:**
```python
def get_model_config(self, use_case: str, model_key: Optional[str] = None) -> LLMModelConfig:
    use_case_config = self.llm.get(use_case)
    if not use_case_config:
        raise ValueError(f"Use case '{use_case}' not found.")
    
    selected_model_key = model_key or use_case_config.default
    model_config = use_case_config.models.get(selected_model_key)
    
    if not model_config:
        raise ValueError(f"Model '{selected_model_key}' not found.")
    
    return model_config
```

**Variable Mapping:**

| LaTeX Symbol | Code Variable | Description |
|:-------------|:--------------|:------------|
| $\mathcal{U}$ | `use_case: str` | Use case identifier |
| $\mathcal{M}_u$ | `models: dict` | Available models |
| $k$ | `model_key: Optional[str]` | User-specified model |
| $d_u$ | `use_case_config.default` | Default model key |

**Complexity:** $O(1)$ - dictionary lookup

---

## 2. LLM Builder - Conditional Instantiation

### Algorithm: Build LLM Instance

**Source:** [`llm_builder.py:15-48`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/service/llm_builder.py#L15-L48)

**Purpose:** Instantiate LLM with conditional `base_url` configuration based on provider.

**Logical Formalization:**

Let $C$ be the configuration object with fields:
- $C.b$ = `base_url` (optional)
- $C.k$ = `api_key`
- $C.m$ = `model`
- $P$ = parameter object (temperature, top_p, etc.)

**Conditional Construction:**

$$
\text{LLM}(C, P) = \begin{cases}
\text{LLM}_{\text{cloud}}(C.k, C.m, P) & \text{if } C.b = \text{null} \\\\
\text{LLM}_{\text{local}}(C.b, C.k, C.m, P) & \text{if } C.b \neq \text{null}
\end{cases}
$$

**Implementation Logic:**
```python
def build(self, llm_type: LLMType, model_key: str = None) -> LLMBuildResult:
    model_config = self.settings.get_model_config(llm_type.value, model_key)
    params = self.settings.get_parameters(llm_type.value)
    
    clean_model_name = LLMUtils.extract_model_name(model_config.model)
    
    if model_config.base_url is None:
        llm_instance = LLM(
            api_key=model_config.api_key,
            model=model_config.model,
            temperature=params.temperature,
            # ... other params
        )
    else:
        llm_instance = LLM(
            base_url=model_config.base_url,  # Local server URL
            api_key=model_config.api_key,
            model=model_config.model,
            temperature=params.temperature,
            # ... other params
        )
    
    return LLMBuildResult(llm=llm_instance, model_name=clean_model_name)
```

**Rationale:** Cloud providers (OpenAI, Gemini) use default endpoints, while local servers (LM Studio) require explicit `base_url`.

**Variable Mapping:**

| LaTeX Symbol | Code Variable | Description |
|:-------------|:--------------|:------------|
| $C$ | `model_config` | Configuration object |
| $C.b$ | `model_config.base_url` | Optional custom URL |
| $P$ | `params` | LLM parameters |

**Complexity:** $O(1)$ - fixed parameter assignment

---

## 3. String Processing - Model Name Extraction

### Algorithm: Extract Model Name

**Source:** [`llm_utils.py:26-32`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/utils/llm_utils.py#L26-L32)

**Purpose:** Remove provider prefixes from model strings for clean naming.

**Logical Formalization:**

Let:
- $S$ = input model string
- $\mathcal{P} = \{\text{"lm\_studio/"}, \text{"gemini/"}, \text{"open\_ai/"}, \text{"azure"}\}$ = set of prefixes

**Function Definition:**

$$
\text{extractName}(S) = \begin{cases}
S[|p|:] & \text{if } \exists p \in \mathcal{P} : S \text{ starts with } p \\\\
S & \text{otherwise}
\end{cases}
$$

where $|p|$ denotes the length of prefix $p$.

**Implementation Logic:**
```python
def extract_model_name(model_string):
    prefixes = ["lm_studio/", "gemini/", "open_ai/", "azure"]
    for prefix in prefixes:
        if model_string.startswith(prefix):
            return model_string[len(prefix):]
    return model_string
```

**Examples:**

| Input | Output | Prefix Removed |
|:------|:-------|:---------------|
| `"gemini/gemini-1.5-pro"` | `"gemini-1.5-pro"` | `"gemini/"` |
| `"lm_studio/llama-3"` | `"llama-3"` | `"lm_studio/"` |
| `"gpt-4o"` | `"gpt-4o"` | None |

**Time Complexity:**

$$
T(n, m) = O(m \cdot n)
$$

where:
- $n$ = length of model string
- $m$ = number of prefixes (constant: $m = 4$)

Effective complexity: $O(n)$ since $m$ is fixed.

**Space Complexity:** $O(1)$ - no additional storage

---

## 4. Telemetry Disabling - Reflection-Based Patching

### Algorithm: Disable Telemetry

**Source:** [`llm_utils.py:15-24`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/utils/llm_utils.py#L15-L24)

**Purpose:** Dynamically replace telemetry methods with no-op functions.

**Logical Formalization:**

Let:
- $T$ = Telemetry class
- $\mathcal{A}(T) = \{a \mid a \text{ is a callable attribute of } T \land \neg a.\text{startswith}("\_\_")\}$
- $\text{noop}$ = no-operation function ($\lambda x: \emptyset$)

**Patching Operation:**

$$
\forall a \in \mathcal{A}(T): \quad T.a \leftarrow \text{noop}
$$

**Implementation Logic:**
```python
def disable_telemetry():
    os.environ["OTEL_SDK_DISABLED"] = "true"
    for attr in dir(Telemetry):
        if callable(getattr(Telemetry, attr)) and not attr.startswith("__"):
            setattr(Telemetry, attr, LLMUtils.noop)
```

**Reflection Steps:**
1. Enumerate all attributes: $\text{dir}(T)$
2. Filter callables: $\text{callable}(\text{getattr}(T, a))$
3. Exclude dunder methods: $\neg a.\text{startswith}("\_\_")$
4. Replace with noop: $\text{setattr}(T, a, \text{noop})$

**Complexity:** $O(|A(T)|)$ where $|A(T)|$ is the number of telemetry methods.

---

## 5. Parameter Retrieval with Defaults

### Algorithm: Get Parameters

**Source:** [`llm_settings.py:27-28`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/settings/llm_settings.py#L27-L28)

**Purpose:** Retrieve use-case-specific parameters or return defaults.

**Logical Formalization:**

$$
\text{getParameters}(u) = \begin{cases}
\text{params}[u] & \text{if } u \in \text{params} \\\\
\text{LLMParameters}_{\text{default}} & \text{otherwise}
\end{cases}
$$

**Implementation Logic:**
```python
def get_parameters(self, use_case: str) -> LLMParameters:
    return self.llm_parameters.get(use_case, LLMParameters())
```

**Default LLMParameters (assumed from Pydantic defaults):**
- `temperature` = 0.7
- `top_p` = 0.95
- `max_completion_tokens` = 8096
- `presence_penalty` = 0
- `frequency_penalty` = 0

**Complexity:** $O(1)$ - dictionary lookup

---

## Summary

| Algorithm | Time Complexity | Space Complexity | Source |
|:----------|:---------------:|:----------------:|:-------|
| Get Model Config | $O(1)$ | $O(1)$ | `llm_settings.py:14` |
| Build LLM Instance | $O(1)$ | $O(1)$ | `llm_builder.py:15` |
| Extract Model Name | $O(n)$ | $O(1)$ | `llm_utils.py:26` |
| Disable Telemetry | $O(\|A(T)\|)$ | $O(1)$ | `llm_utils.py:15` |
| Get Parameters | $O(1)$ | $O(1)$ | `llm_settings.py:27` |

**Total:** 5 algorithms formalized with strict code traceability.

---

## Design Decisions

### Why Conditional base_url?

**Cloud providers** (OpenAI, Gemini) have default endpoints built into the `crewai.LLM` class.  
**Local providers** (LM Studio) require explicit base URLs (e.g., `http://localhost:1234/v1`).

The conditional logic avoids passing `None` for `base_url`, which would override the provider defaults.

**Mathematical Justification:**

Define endpoint resolution:

$$
\text{endpoint}(C) = \begin{cases}
\text{provider\_default}(C.m) & \text{if } C.b = \text{null} \\\\
C.b & \text{if } C.b \neq \text{null}
\end{cases}
$$

This ensures maximum flexibility without code duplication.
