# LLM Factory: Mathematical Foundations

## 1. Hierarchical Configuration Resolution

The `LLMSettings` class implements a hierarchical lookup algorithm to resolve the specific LLM configuration (Model, API Key, Base URL) based on the abstract "Use Case" and optional overrides.

### Code Verification
- **Source:** `src/nikhil/amsha/llm_factory/settings/llm_settings.py`
- **Lines:** 14-25 (`get_model_config`)

### Formalization

Let $U$ be the set of Use Cases (e.g., $\{Creative, Evaluation\}$) and $M$ be the set of available Model Configurations.

The configuration function $C(u, k_{opt})$ maps a use case $u \in U$ and an optional model key $k_{opt}$ to a specific configuration $m \in M$:

$$
C(u, k_{opt}) = \begin{cases}
Config(u, k_{opt}) & \text{if } k_{opt} \neq \emptyset \\
Config(u, Default(u)) & \text{if } k_{opt} = \emptyset
\end{cases}
$$

Where:
- $Default(u)$ returns the default model key for use case $u$.
- $Config(u, k)$ retrieves the parameters (temperature, tokens) for the pair.

### Validated Logic
The algorithm enforces existence constraints:
1. $u \in U$
2. $k \in Models(u)$

### Complexity
- **Time:** $O(1)$ (Hash map lookup).
- **Space:** $O(1)$.

---

## 2. Reflective Telemetry Disabling

The `LLMUtils` class employs runtime reflection to dynamically modify the behavior of external dependencies (CrewAI Telemetry) without forking the source code.

### Code Verification
- **Source:** `src/nikhil/amsha/llm_factory/utils/llm_utils.py`
- **Lines:** 16-24 (`disable_telemetry`)

### Formalization

Let $T$ be the Telemetry class object. Let $Attr(T)$ be the set of all attributes of $T$.

The transformation $disable(T)$ allows strict privacy by replacing all public methods with a No-Operation ($noop$) function:

$$
\forall a \in Attr(T), \quad T'.a = \begin{cases}
noop & \text{if } is\_callable(a) \land \neg startswith(a, "\_\_") \\
T.a & \text{otherwise}
\end{cases}
$$

### Variable Mapping

| LaTeX Symbol | Code Variable | Description |
| :--- | :--- | :--- |
| $T$ | `Telemetry` | The external class to patch |
| $Attr(T)$ | `dir(Telemetry)` | List of attributes |
| $noop$ | `LLMUtils.noop` | Replacement function |

### Complexity
- **Time:** $O(|Attr(T)|)$ - Linear scan of attributes.
- **Space:** $O(1)$.
