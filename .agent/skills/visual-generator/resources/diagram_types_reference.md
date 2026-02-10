# Mermaid.js Diagram Type Reference

Complete reference of all Mermaid.js diagram types with use cases and syntax.

---

## 1. Flowchart (Process & Logic)

**Use For:** Workflows, decision trees, process flows, algorithms

**Syntax:**
```mermaid
flowchart TD
    Start([Start]) --> Input[/Input Data/]
    Input --> Process[Process Step]
    Process --> Decision{Valid?}
    Decision -->|Yes| Output[/Output/]
    Decision -->|No| Error[Error Handler]
    Output --> End([End])
    Error --> End
```

**Best For Research Papers:**
- Algorithm flowcharts
- System workflows
- Decision logic
- Pipeline architectures

**Directions:** `TD`, `TB`, `LR`, `RL`, `BT`

---

## 2. Sequence Diagram (Interactions)

**Use For:** Message flows, API calls, multi-component interactions, temporal sequences

**Syntax:**
```mermaid
sequenceDiagram
    autonumber
    participant A as Client
    participant B as Server
    participant C as Database
    
    A->>B: POST /api/data
    activate B
    B->>C: INSERT query
    activate C
    C-->>B: Success
    deactivate C
    B-->>A: 200 OK
    deactivate B
```

**Best For Research Papers:**
- Module interaction workflows
- Message passing protocols
- Temporal execution order
- Multi-agent communication

**Features:**
- `autonumber` - Auto-index messages
- `activate`/`deactivate` - Lifelines
- `-->>` - Dashed reply
- `->>` - Solid request
- `Note over A,B` - Annotations

---

## 3. Class Diagram (OOP Structure)

**Use For:** Object-oriented design, data models, architectural patterns

**Syntax:**
```mermaid
classDiagram
    class Animal {
        <<abstract>>
        +String name
        +int age
        +makeSound()* void
    }
    
    class Dog {
        +String breed
        +makeSound() void
        +fetch() void
    }
    
    class Cat {
        +int livesLeft
        +makeSound() void
        +scratch() void
    }
    
    Animal <|-- Dog : inherits
    Animal <|-- Cat : inherits
```

**Relationships:**
- `<|--` - Inheritance
- `*--` - Composition
- `o--` - Aggregation
- `-->` - Association
- `..>` - Dependency
- `..|>` - Realization/Implementation

**Visibility:**
- `+` Public
- `-` Private
- `#` Protected
- `~` Package/Internal

**Best For Research Papers:**
- Domain models
- Clean architecture layers
- Protocol/interface hierarchies

---

## 4. State Diagram (Finite State Machines)

**Use For:** State transitions, lifecycle models, status workflows

**Syntax:**
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : start_task
    Processing --> Completed : success
    Processing --> Failed : error
    Failed --> Idle : retry
    Completed --> [*]
    
    Processing --> Paused : pause
    Paused --> Processing : resume
```

**Best For Research Papers:**
- Task lifecycle models
- Agent states
- Processing pipelines
- System modes

---

## 5. Entity Relationship Diagram (Database Schema)

**Use For:** Database design, data relationships, schema documentation

**Syntax:**
```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
    PRODUCT ||--o{ LINE_ITEM : "ordered in"
    
    USER {
        int id PK
        string email UK
        string name
        datetime created_at
    }
    
    ORDER {
        int id PK
        int user_id FK
        decimal total
        string status
    }
```

**Cardinality:**
- `||--||` - One to one
- `||--o{` - One to many
- `}o--o{` - Many to many

**Best For Research Papers:**
- Repository pattern schemas
- Data persistence design
- Domain model persistence

---

## 6. Gantt Chart (Project Timeline)

**Use For:** Project schedules, task dependencies, timeline visualization

**Syntax:**
```mermaid
gantt
    title Development Timeline
    dateFormat YYYY-MM-DD
    section Planning
        Requirements    :a1, 2024-01-01, 7d
        Design         :a2, after a1, 5d
    section Implementation
        Module A       :b1, after a2, 10d
        Module B       :b2, after a2, 8d
    section Testing
        Unit Tests     :c1, after b1, 3d
        Integration    :c2, after b2, 5d
```

**Best For Research Papers:**
- Development timeline
- Experimental schedule
- Milestone tracking

---

## 7. Pie Chart (Proportions)

**Use For:** Distribution visualization, percentage breakdown

**Syntax:**
```mermaid
pie title Module Code Distribution
    "Crew Forge" : 450
    "Output Process" : 320
    "Crew Monitor" : 280
    "Crew Gen" : 210
    "LLM Factory" : 150
    "Utils" : 95
```

**Best For Research Papers:**
- Code distribution
- Resource allocation
- Performance breakdown

---

## 8. Architecture Diagram (System Infrastructure)

**Use For:** System architecture, infrastructure layout, service deployment

**Syntax:**
```mermaid
architecture-beta
    service web(server)[Web Server]
    service api(server)[API Gateway]
    service db[(database)][Database]
    
    web:R --> L:api
    api:R --> L:db
```

**Best For Research Papers:**
- System deployment
- Multi-tier architecture
- Cloud infrastructure

---

## 9. Block Diagram (High-Level Components)

**Use For:** Component relationships, high-level system overview

**Syntax:**
```mermaid
block-beta
    columns 3
    Frontend:3
    block:group1:2
        API["API Layer"]
        Logic["Business Logic"]
    end
    Database
    
    Frontend --> API
    API --> Logic
    Logic --> Database
```

**Best For Research Papers:**
- System overview
- Component interaction
- Layer separation

---

## 10. C4 Context Diagram (System Context)

**Use For:** System boundaries, external actors, high-level context

**Syntax:**
```mermaid
C4Context
    title System Context for Amsha
    
    Person(user, "Developer", "Uses Amsha for agent orchestration")
    System(amsha, "Amsha System", "Multi-agent orchestration framework")
    System_Ext(llm, "LLM Provider", "OpenAI, Anthropic, etc.")
    System_Ext(db, "MongoDB", "Persistence layer")
    
    Rel(user, amsha, "Uses")
    Rel(amsha, llm, "Calls")
    Rel(amsha, db, "Reads/Writes")
```

**Best For Research Papers:**
- System context
- External dependencies
- Actor interactions

---

## 11. Mindmap (Hierarchical Concepts)

**Use For:** Brainstorming, concept hierarchies, topic breakdown

**Syntax:**
```mermaid
mindmap
    root((Amsha Project))
        Architecture
            Clean Arch
            3-Tier Design
            Repository Pattern
        Modules
            Crew Forge
            Output Process
            Crew Monitor
        Testing
            Unit Tests
            E2E Tests
            Integration
```

**Best For Research Papers:**
- Contribution breakdown
- Concept organization
- Research areas

---

## 12. Timeline (Event Sequence)

**Use For:** Historical events, milestone progression, chronological data

**Syntax:**
```mermaid
timeline
    title Project Development Timeline
    2024-Q1 : Requirements
            : Initial Design
    2024-Q2 : Core Implementation
            : Testing Framework
    2024-Q3 : Integration
            : Documentation
    2024-Q4 : Publication
            : Deployment
```

**Best For Research Papers:**
- Development history
- Experimental timeline
- Version milestones

---

## 13. Quadrant Chart (2D Categorization)

**Use For:** Priority matrices, categorization, comparative positioning

**Syntax:**
```mermaid
quadrantChart
    title Priority vs Complexity Matrix
    x-axis Low Complexity --> High Complexity
    y-axis Low Priority --> High Priority
    quadrant-1 Quick Wins
    quadrant-2 Major Projects
    quadrant-3 Fill-ins
    quadrant-4 Time Wasters
    
    Crew Forge: [0.8, 0.9]
    Output Process: [0.7, 0.8]
    Utils: [0.2, 0.3]
```

**Best For Research Papers:**
- Module prioritization
- Feature comparison
- Risk assessment

---

## 14. Requirements Diagram (System Requirements)

**Use For:** Requirements traceability, specification documentation

**Syntax:**
```mermaid
requirementDiagram
    requirement test_req {
        id: 1
        text: System shall support multiple LLM providers
        risk: high
        verifymethod: test
    }
    
    element crew_forge {
        type: module
    }
    
    crew_forge - satisfies -> test_req
```

**Best For Research Papers:**
- System requirements
- Design constraints
- Validation criteria

---

## 15. Sankey Diagram (Flow Quantities) [Beta]

**Use For:** Flow visualization, resource distribution, data movement

**Syntax:**
```mermaid
sankey-beta
    Input,Processing,100
    Processing,OutputA,60
    Processing,OutputB,40
```

**Best For Research Papers:**
- Data flow volumes
- Resource allocation
- Performance distribution

---

## Selection Guide

| Research Paper Need | Recommended Diagram Type |
|:-------------------|:------------------------|
| Show algorithm logic | **Flowchart** |
| Show module interactions | **Sequence Diagram** |
| Show class hierarchy | **Class Diagram** |
| Show 3-tier architecture | **Block** or **Architecture** |
| Show task lifecycle | **State Diagram** |
| Show database schema | **ER Diagram** |
| Show system context | **C4 Context** |
| Show code distribution | **Pie Chart** |
| Show development timeline | **Gantt** or **Timeline** |
| Show module priorities | **Quadrant Chart** |
| Show concept breakdown | **Mindmap** |

---

## Diagram Combination Strategy

For comprehensive research papers, use multiple diagram types:

1. **Section 3 (Architecture):**
   - Block Diagram (system overview)
   - C4 Context (external dependencies)
   - Class Diagram (domain models)

2. **Section 4 (Module Details):**
   - Flowchart (algorithm logic)
   - Sequence Diagram (interactions)
   - State Diagram (lifecycle)

3. **Section 6 (Evaluation):**
   - Pie Chart (distribution)
   - Gantt (timeline)

**Golden Rule:** Use 2-3 diagram types per module, 6-8 total for a full paper.
