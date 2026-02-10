# Mermaid Diagram Templates

Use these templates when creating architectural visualizations.

## Class Diagram Template

```mermaid
classDiagram
    class ClassName {
        +type attribute_name
        +method_name(params) return_type
    }
    
    class AnotherClass {
        -private_field type
        #protected_method()
    }
    
    ClassName --> AnotherClass : relationship
```

### Clean Architecture Example

```mermaid
classDiagram
    %% Domain Layer
    class TaskProtocol {
        <<interface>>
        +execute() Result
        +validate() bool
    }
    
    class TaskModel {
        <<dataclass>>
        +id: str
        +name: str
        +status: TaskStatus
    }
    
    %% Application Layer
    class TaskService {
        -repository: TaskRepository
        +create_task(data) Task
        +execute_task(id) Result
    }
    
    %% Infrastructure Layer
    class MongoTaskRepository {
        -client: MongoClient
        +save(task) void
        +find_by_id(id) Task
    }
    
    TaskService ..> TaskProtocol : uses
    TaskService --> TaskModel : manages
    MongoTaskRepository ..|> TaskProtocol : implements
```

## Sequence Diagram Template

```mermaid
sequenceDiagram
    actor User
    participant Service
    participant Repository
    participant Database
    
    User->>Service: request_action()
    Service->>Repository: fetch_data(id)
    Repository->>Database: SELECT * WHERE id=?
    Database-->>Repository: result_set
    Repository-->>Service: domain_object
    Service-->>User: response
```

### Multi-Module Workflow Example

```mermaid
sequenceDiagram
    participant CrewGen as Crew Generator
    participant CrewForge as Crew Forge
    participant LLMFactory as LLM Factory
    participant Monitor as Crew Monitor
    
    CrewGen->>CrewGen: Parse YAML template
    CrewGen->>LLMFactory: create_llm(provider, model)
    LLMFactory-->>CrewGen: llm_instance
    
    CrewGen->>CrewForge: create_crew(agents, tasks)
    CrewForge->>CrewForge: Validate dependencies
    CrewForge-->>CrewGen: crew_instance
    
    CrewGen->>Monitor: start_monitoring(crew)
    CrewGen->>CrewForge: execute_crew()
    
    loop Task Execution
        CrewForge->>Monitor: log_metrics(cpu, gpu, mem)
        CrewForge->>CrewForge: Execute task
    end
    
    CrewForge-->>CrewGen: execution_result
    Monitor-->>CrewGen: performance_report
```

## Component Diagram Template

```mermaid
graph TB
    subgraph "Domain Layer"
        Models[Domain Models]
        Protocols[Protocols/Interfaces]
    end
    
    subgraph "Application Layer"
        UseCases[Use Cases]
        Services[Services]
    end
    
    subgraph "Infrastructure Layer"
        Repositories[Repositories]
        Adapters[External Adapters]
    end
    
    UseCases --> Protocols
    Services --> Models
    Repositories -.-> Protocols
    Adapters --> Services
```

### 3-Tier Architecture Example

```mermaid
graph TB
    subgraph Amsha["Amsha - Mathematical Core"]
        A1[Calculation Engine]
        A2[Algorithm Library]
    end
    
    subgraph Bodha["Bodha - Business Logic"]
        B1[Crew Orchestrator]
        B2[Evaluation Service]
        B3[Monitoring Service]
    end
    
    subgraph Yantra["Yantra - Infrastructure"]
        Y1[MongoDB Repository]
        Y2[File System]
        Y3[LLM Providers]
    end
    
    B1 --> A1
    B2 --> A2
    B1 --> Y1
    B2 --> Y2
    B3 --> Y3
    
    style Amsha fill:#e1f5ff
    style Bodha fill:#fff3e0
    style Yantra fill:#f3e5f5
```

## Flowchart Template

```mermaid
flowchart TD
    Start([Start]) --> Input[/Input Data/]
    Input --> Validate{Valid?}
    Validate -->|No| Error[Error Handler]
    Validate -->|Yes| Process[Process Data]
    Process --> Check{Meets Criteria?}
    Check -->|Yes| Success[Success Path]
    Check -->|No| Retry{Retry?}
    Retry -->|Yes| Process
    Retry -->|No| Fail[Failure Path]
    Success --> End([End])
    Fail --> End
    Error --> End
```

## Performance Metrics Table Template

### Option 1: Comparison Table

| Operation | Time (ms) | Memory (MB) | Accuracy (%) |
|:----------|----------:|------------:|-------------:|
| Task Generation | 12.3 | 4.2 | 98.5 |
| Crew Execution | 234.7 | 156.3 | 95.2 |
| Result Evaluation | 8.1 | 2.7 | 99.1 |

### Option 2: Module Comparison

| Module | LOC | Complexity | Test Coverage (%) | Grade |
|:-------|----:|:-----------|------------------:|:-----:|
| crew_forge | 450 | Low | 95 | A |
| output_process | 320 | Medium | 92 | A |
| crew_monitor | 280 | Low | 88 | B |
| llm_factory | 150 | Low | 90 | A |

### Option 3: Performance Benchmarks

| Metric | Baseline | Optimized | Improvement |
|:-------|:---------|:----------|:------------|
| Response Time | 450ms | 120ms | **73% ↓** |
| Memory Usage | 250MB | 180MB | **28% ↓** |
| CPU Load | 85% | 45% | **47% ↓** |
| Throughput | 10 req/s | 35 req/s | **250% ↑** |

## Caption Format

Always include descriptive captions:

```markdown
```mermaid
graph ...
```

**Figure 3.1:** System architecture showing the three-tier design with clean separation between domain (Amsha), business logic (Bodha), and infrastructure (Yantra) layers.
```

## Best Practices

1. **Keep it simple** - Maximum 7-8 nodes per diagram
2. **Use subgraphs** - Group related components
3. **Consistent naming** - Match code variable/class names
4. **Add styling** - Use colors to distinguish layers
5. **Verify accuracy** - Every box must exist in code
6. **Reference source** - Link to actual files/classes
