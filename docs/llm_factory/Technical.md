-   **Core Dependencies:**
    * **Pydantic:** Data validation and modeling.
    * **PyYAML:** Configuration parsing.
    * **Dependency Injector:** Dependency injection framework.
    * **CrewAI:** Target object type (`crewai.LLM`).

-----

### 3. Architectural Design

#### 3.1. Design Patterns

-   **Dependency Injection:** The core architecture uses `dependency-injector` containers to manage object lifecycles and configuration.
-   **Builder Pattern:** `LLMBuilder` encapsulates the logic of constructing complex `LLM` objects from configuration settings.

#### 3.2. Core Components

-   **`LLMContainer`:** The DI container.
    -   `config`: Configuration provider (YAML path).
    -   `llm_settings`: Singleton provider for parsed settings.
    -   `llm_builder`: Factory provider for `LLMBuilder`.
    -   `creative_llm` / `evaluation_llm`: Factory providers for specific LLM instances.
-   **`LLMBuilder`:** Service class that constructs `LLM` instances.
-   **`LLMSettings`:** Pydantic model representing the loaded configuration.

-----

### 4. Data Models

-   **`LLMModelConfig`:** Defines a single model (base_url, model, api_key).
-   **`LLMUseCaseConfig`:** Defines a use case (default model, map of models).
-   **`LLMParameters`:** Defines generation parameters (temperature, top_p, etc.).
-   **`LLMSettings`:** Root configuration model.

-----

### 5. Error Handling

-   **`ValueError`:** Raised for missing use cases or models.
-   **`pydantic.ValidationError`:** Raised for malformed YAML structure.