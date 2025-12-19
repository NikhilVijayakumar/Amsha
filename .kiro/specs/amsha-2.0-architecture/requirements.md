# Requirements Document: Amsha 2.0 Architecture Refactoring

## Introduction

This document analyzes the feasibility of implementing the Amsha 2.0 architecture specification against the current codebase (version 2.0.9). Amsha is a common library for CrewAI orchestration that aims to become a general agentic execution substrate. The proposed 2.0 architecture seeks to generalize execution, instrumentation, observability, and state handling while explicitly avoiding standardization of business workflows and domain logic.

## Glossary

- **Amsha**: A Python library providing orchestration capabilities for CrewAI-based agent systems
- **CrewAI**: An external framework for building AI agent crews
- **LLM**: Large Language Model
- **Execution Substrate**: Infrastructure layer that handles execution mechanics without imposing workflow logic
- **Domain Agnosticism**: The principle that infrastructure should not understand or interpret business meaning
- **Clean Architecture**: Architectural pattern where dependencies flow inward, with domain logic independent of external frameworks
- **Dependency Injection (DI)**: Design pattern where dependencies are provided to objects rather than created internally
- **Orchestrator**: Component responsible for building and executing agent crews
- **Repository**: Data access abstraction layer following the repository pattern
- **Protocol**: Python structural typing mechanism for defining interfaces without inheritance
- **ABC (Abstract Base Class)**: Python nominal typing mechanism for defining interfaces with inheritance
- **Execution Mode**: Classification of execution behavior (interactive vs background)
- **State Container**: Generic storage mechanism for execution state
- **Observability**: The ability to monitor and measure system behavior during execution

## Requirements

### Requirement 1: Architectural Feasibility Assessment

**User Story:** As an Amsha maintainer, I want to understand the feasibility of implementing the proposed 2.0 architecture, so that I can make informed decisions about refactoring priorities and risks.

#### Acceptance Criteria

1. WHEN analyzing the current codebase THEN the system SHALL identify all components that align with the proposed architecture
2. WHEN analyzing the current codebase THEN the system SHALL identify all components that conflict with the proposed architecture
3. WHEN evaluating each proposed module THEN the system SHALL assess implementation complexity as low, medium, or high
4. WHEN evaluating dependencies THEN the system SHALL identify breaking changes that would affect client code
5. WHEN assessing feasibility THEN the system SHALL provide specific code examples demonstrating alignment or misalignment

### Requirement 2: LLM Factory Module Analysis

**User Story:** As an Amsha developer, I want to understand how the current LLM Factory aligns with the proposed execution-aware design, so that I can plan necessary refactoring work.

#### Acceptance Criteria

1. WHEN examining the current LLMBuilder THEN the system SHALL identify its dependency on crewai.LLM framework
2. WHEN analyzing streaming support THEN the system SHALL determine whether streaming is currently capability-based or mandatory
3. WHEN evaluating execution modes THEN the system SHALL assess whether the current implementation supports both interactive and background execution
4. WHEN reviewing retry and observability THEN the system SHALL identify where these concerns are currently handled
5. WHEN assessing the ILLMProvider interface THEN the system SHALL determine whether it exists and meets the proposed minimal interface requirements

### Requirement 3: Crew Forge Module Analysis

**User Story:** As an Amsha developer, I want to understand how the current orchestration layer aligns with the proposed separation of execution from workflow logic, so that I can identify refactoring needs.

#### Acceptance Criteria

1. WHEN examining orchestrators THEN the system SHALL determine whether they contain workflow logic or only execution logic
2. WHEN analyzing the registry pattern THEN the system SHALL assess whether it is passive or contains execution logic
3. WHEN evaluating client interfaces THEN the system SHALL identify whether clients currently control flow or if Amsha imposes flow
4. WHEN reviewing the dual-mode architecture THEN the system SHALL verify that DB and File modes provide identical client interfaces
5. WHEN assessing ExecutionSession THEN the system SHALL determine whether this abstraction exists and what responsibilities it currently has

### Requirement 4: Execution State Module Analysis

**User Story:** As an Amsha developer, I want to understand the current state management approach, so that I can assess the effort required to implement the proposed ExecutionState module.

#### Acceptance Criteria

1. WHEN analyzing the current codebase THEN the system SHALL identify all locations where execution state is currently managed
2. WHEN evaluating state persistence THEN the system SHALL determine whether save/load mechanisms exist
3. WHEN reviewing state injection THEN the system SHALL assess whether state can be passed between executions
4. WHEN examining state interpretation THEN the system SHALL identify any locations where Amsha interprets state semantics
5. WHEN assessing snapshotting THEN the system SHALL determine whether execution snapshots are currently supported

### Requirement 5: Execution Runtime Module Analysis

**User Story:** As an Amsha developer, I want to understand how the current execution model aligns with the proposed execution modes and handles, so that I can plan the implementation of execution semantics.

#### Acceptance Criteria

1. WHEN examining current execution THEN the system SHALL determine whether execution is synchronous, asynchronous, or both
2. WHEN analyzing streaming THEN the system SHALL identify whether streaming is currently supported and how it is exposed
3. WHEN evaluating execution handles THEN the system SHALL assess whether the current API provides status, result, stream, and cancel operations
4. WHEN reviewing background execution THEN the system SHALL determine whether detached execution is currently supported
5. WHEN assessing execution modes THEN the system SHALL identify whether interactive and background modes are distinguished

### Requirement 6: Crew Monitor Module Analysis

**User Story:** As an Amsha developer, I want to understand how the current monitoring implementation aligns with the proposed observer-based instrumentation, so that I can assess compatibility with new execution modes.

#### Acceptance Criteria

1. WHEN examining CrewPerformanceMonitor THEN the system SHALL determine whether it uses an observer pattern
2. WHEN analyzing monitoring integration THEN the system SHALL assess whether monitoring is automatically applied or manually invoked
3. WHEN evaluating metric normalization THEN the system SHALL identify whether metrics are normalized into a standard format
4. WHEN reviewing streaming support THEN the system SHALL determine whether monitoring works with streaming execution
5. WHEN assessing background execution THEN the system SHALL determine whether monitoring works with background execution

### Requirement 7: Client Responsibility Analysis

**User Story:** As an Amsha maintainer, I want to understand the current division of responsibilities between Amsha and client code, so that I can assess alignment with the proposed "Client Owns Flow" principle.

#### Acceptance Criteria

1. WHEN examining client examples THEN the system SHALL identify all control flow logic (loops, branches, retries)
2. WHEN analyzing the application base classes THEN the system SHALL determine whether they impose workflow patterns
3. WHEN reviewing pipeline execution THEN the system SHALL assess whether pipelines are declarative or imperative
4. WHEN evaluating decision-making THEN the system SHALL identify whether Amsha makes execution decisions based on results
5. WHEN assessing client control THEN the system SHALL determine whether clients can fully control execution order and conditions

### Requirement 8: Breaking Changes Assessment

**User Story:** As an Amsha maintainer, I want to identify all breaking changes that would result from implementing the 2.0 architecture, so that I can plan migration strategies and version bumps.

#### Acceptance Criteria

1. WHEN analyzing public APIs THEN the system SHALL identify all method signature changes required
2. WHEN evaluating interfaces THEN the system SHALL identify all Protocol or ABC changes that would break existing implementations
3. WHEN reviewing configuration THEN the system SHALL identify all configuration structure changes
4. WHEN assessing dependencies THEN the system SHALL identify all dependency changes that would affect clients
5. WHEN evaluating backward compatibility THEN the system SHALL propose deprecation strategies for each breaking change

### Requirement 9: Implementation Roadmap

**User Story:** As an Amsha maintainer, I want a prioritized implementation roadmap, so that I can sequence refactoring work to minimize disruption and maximize value.

#### Acceptance Criteria

1. WHEN prioritizing modules THEN the system SHALL order them by dependency relationships
2. WHEN assessing risk THEN the system SHALL identify high-risk changes that require careful migration
3. WHEN evaluating value THEN the system SHALL identify which changes provide the most immediate benefit
4. WHEN planning phases THEN the system SHALL group related changes into coherent implementation phases
5. WHEN considering compatibility THEN the system SHALL identify opportunities for incremental adoption without breaking existing clients

### Requirement 10: Compliance with Architectural Laws

**User Story:** As an Amsha maintainer, I want to assess how well the current codebase complies with the proposed architectural laws, so that I can understand the cultural and structural changes required.

#### Acceptance Criteria

1. WHEN evaluating domain agnosticism THEN the system SHALL identify all locations where Amsha interprets business meaning
2. WHEN assessing the proxy rule THEN the system SHALL identify all direct dependencies on external frameworks
3. WHEN reviewing configuration-first THEN the system SHALL identify all behavior changes that require code modifications
4. WHEN evaluating client flow ownership THEN the system SHALL identify all locations where Amsha controls execution flow
5. WHEN assessing state infrastructure THEN the system SHALL identify all locations where Amsha implements state-driven decisions
