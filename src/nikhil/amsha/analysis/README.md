# Architectural Alignment Assessment Tool

This tool analyzes the current Amsha codebase against the proposed 2.0 architecture specification and generates comprehensive alignment reports with specific code examples.

## Overview

The Architectural Alignment Assessment Tool provides:

- **Component Analysis**: Categorizes components as aligned/conflicting with proposed modules
- **Complexity Assessment**: Evaluates implementation complexity (low/medium/high)
- **Gap Identification**: Identifies specific gaps and required changes
- **Pattern Detection**: Detects current architectural patterns and compliance levels
- **Feasibility Scoring**: Provides quantitative feasibility assessment
- **Actionable Recommendations**: Generates specific implementation guidance

## Usage

### Basic Usage

```python
from nikhil.amsha.analysis import ArchitecturalAlignmentTool

# Initialize the tool
tool = ArchitecturalAlignmentTool()

# Print summary to console
tool.print_summary()

# Generate detailed JSON report
report = tool.generate_report_file("alignment_report.json")
```

### Advanced Usage

```python
# Initialize with custom codebase path
tool = ArchitecturalAlignmentTool(codebase_root="custom/path/to/amsha")

# Get raw analysis data
report_data = tool.analyze_codebase()

# Access specific analysis results
for analysis in tool.analysis_results:
    print(f"Component: {analysis.component_name}")
    print(f"Alignment: {analysis.alignment_level.value}")
    print(f"Complexity: {analysis.complexity_level.value}")
    print(f"Gaps: {analysis.gaps}")
```

## Report Structure

The generated report contains:

### Analysis Summary
- Total components analyzed
- Feasibility score (0.0 - 1.0)
- Feasibility level (Low/Medium/High)
- Alignment breakdown by category

### Detailed Analysis
For each component:
- Component name and file path
- Proposed 2.0 module mapping
- Alignment level assessment
- Implementation complexity
- Strengths and gaps
- Specific code examples
- Dependencies
- Required breaking changes

### Architectural Patterns
- Clean Architecture compliance
- Dependency Injection usage
- Repository Pattern implementation
- Dual-Mode Architecture detection

### Recommendations
- Prioritized implementation guidance
- Migration strategies
- Risk mitigation approaches

## Alignment Levels

- **Fully Aligned**: Component meets 2.0 specification requirements
- **Partially Aligned**: Component has good foundation but needs modifications
- **Conflicting**: Component conflicts with 2.0 architecture principles
- **Missing**: Required component doesn't exist in current codebase

## Complexity Levels

- **Low**: Minor interface additions or refactoring
- **Medium**: Significant refactoring with some breaking changes
- **High**: Major architectural changes or new module creation

## Example Output

```
============================================================
🏗️  ARCHITECTURAL ALIGNMENT SUMMARY
============================================================
📊 Feasibility Score: 0.33/1.0 (Low Feasibility)
🔍 Components Analyzed: 6

📋 Alignment Breakdown:
  Partially Aligned: 4 components
    - LLMBuilder (llm_factory) - medium complexity
    - DbCrewOrchestrator (crew_forge) - low complexity
    - FileCrewOrchestrator (crew_forge) - low complexity
    - CrewPerformanceMonitor (crew_monitor) - low complexity
  Missing: 2 components
    - ExecutionState (execution_state) - high complexity
    - ExecutionRuntime (execution_runtime) - high complexity

🏗️ Architectural Patterns:
  Clean Architecture: Partial
    Domain layer purity: ⚠️ (2 violations found)
  Dependency Injection: Good
    DI containers found: 3
  Repository Pattern: Good
    Interfaces: 5, Adapters: 6
  Dual-Mode Architecture: Good
    Parallel implementations found: 1 pairs

💡 Key Recommendations:
  1. Implement ExecutionMode enum and execution-aware APIs as foundation
  2. Create ExecutionState module as new infrastructure component
  3. Introduce ILLMProvider abstraction to decouple from CrewAI framework
  4. Refactor monitoring to use observer pattern for automatic instrumentation
  5. Maintain backward compatibility through adapter pattern during migration
  6. Implement changes incrementally, starting with least disruptive modules
============================================================
```

## Integration with Amsha 2.0 Feasibility Analysis

This tool directly supports the requirements from the Amsha 2.0 Architecture Feasibility Analysis:

- **Requirement 1.1**: Identifies all components that align with proposed architecture
- **Requirement 1.2**: Identifies all components that conflict with proposed architecture  
- **Requirement 1.5**: Provides specific code examples demonstrating alignment/misalignment

The tool generates the foundational analysis needed for all subsequent feasibility assessment tasks.

## Command Line Usage

```bash
# Run from project root using virtual environment
venv\Scripts\python -m src.nikhil.amsha.analysis.architectural_alignment_tool

# Or use the test script
venv\Scripts\python test_alignment_tool.py
```

## Dependencies

The tool uses only Python standard library modules:
- `ast` - For code parsing
- `pathlib` - For file system operations
- `json` - For report generation
- `re` - For pattern matching
- `dataclasses` - For data structures
- `enum` - For type definitions

No external dependencies are required, making it lightweight and easy to integrate.