"""
Architectural Alignment Assessment Tool for Amsha 2.0 Architecture Analysis

This tool analyzes the current Amsha codebase against the proposed 2.0 architecture
specification and generates alignment reports with specific code examples.
"""

import ast
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
import json
import re


class AlignmentLevel(Enum):
    """Alignment levels for components against 2.0 architecture"""
    FULLY_ALIGNED = "fully_aligned"
    PARTIALLY_ALIGNED = "partially_aligned"
    CONFLICTING = "conflicting"
    MISSING = "missing"


class ComplexityLevel(Enum):
    """Implementation complexity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ProposedModule(Enum):
    """Proposed 2.0 architecture modules"""
    LLM_FACTORY = "llm_factory"
    CREW_FORGE = "crew_forge"
    EXECUTION_STATE = "execution_state"
    EXECUTION_RUNTIME = "execution_runtime"
    CREW_MONITOR = "crew_monitor"


@dataclass
class ComponentAnalysis:
    """Analysis result for a single component"""
    component_path: str
    component_name: str
    proposed_module: ProposedModule
    alignment_level: AlignmentLevel
    complexity_level: ComplexityLevel
    strengths: List[str]
    gaps: List[str]
    code_examples: List[str]
    dependencies: List[str]
    breaking_changes: List[str]


@dataclass
class ArchitecturalPattern:
    """Detected architectural pattern"""
    pattern_name: str
    locations: List[str]
    compliance_level: str
    description: str


class ArchitecturalAlignmentTool:
    """
    Tool for analyzing architectural alignment between current codebase 
    and proposed 2.0 architecture specification.
    """
    
    def __init__(self, codebase_root: str = "src/nikhil/amsha"):
        self.codebase_root = Path(codebase_root)
        self.analysis_results: List[ComponentAnalysis] = []
        self.architectural_patterns: List[ArchitecturalPattern] = []
        
    def analyze_codebase(self) -> Dict[str, Any]:
        """
        Conducts comprehensive codebase analysis against 2.0 specification.
        
        Returns:
            Complete analysis report with alignment assessments
        """
        print("🔍 Starting comprehensive codebase analysis...")
        
        # Analyze each proposed module
        self._analyze_llm_factory_module()
        self._analyze_crew_forge_module()
        self._analyze_execution_state_module()
        self._analyze_execution_runtime_module()
        self._analyze_crew_monitor_module()
        
        # Detect architectural patterns
        self._detect_architectural_patterns()
        
        # Generate comprehensive report
        return self._generate_alignment_report()
    
    def _analyze_llm_factory_module(self):
        """Analyze LLM Factory module alignment"""
        print("  📦 Analyzing LLM Factory module...")
        
        llm_builder_path = self.codebase_root / "llm_factory/service/llm_builder.py"
        
        if llm_builder_path.exists():
            code_content = llm_builder_path.read_text(encoding='utf-8')
            
            # Analyze strengths and gaps
            strengths = []
            gaps = []
            code_examples = []
            
            # Check for clean factory pattern
            if "class LLMBuilder:" in code_content:
                strengths.append("Clean factory pattern implementation")
                code_examples.append("class LLMBuilder with proper build methods")
            
            # Check for DI integration
            if "LLMSettings" in code_content and "__init__" in code_content:
                strengths.append("Proper dependency injection integration")
            
            # Check for framework coupling
            if "from crewai import LLM" in code_content:
                gaps.append("Direct crewai.LLM dependency - needs abstraction")
                code_examples.append("Direct import: from crewai import LLM")
            
            # Check for execution mode awareness
            if "stream=True" in code_content and "ExecutionMode" not in code_content:
                gaps.append("No execution mode awareness - hardcoded streaming")
                code_examples.append("Hardcoded: stream=True")
            
            # Check for retry/observability decorators
            if "@" not in code_content or "retry" not in code_content.lower():
                gaps.append("No retry/observability decorators")
            
            analysis = ComponentAnalysis(
                component_path=str(llm_builder_path),
                component_name="LLMBuilder",
                proposed_module=ProposedModule.LLM_FACTORY,
                alignment_level=AlignmentLevel.PARTIALLY_ALIGNED,
                complexity_level=ComplexityLevel.MEDIUM,
                strengths=strengths,
                gaps=gaps,
                code_examples=code_examples,
                dependencies=["crewai.LLM", "LLMSettings"],
                breaking_changes=["ILLMProvider protocol introduction", "Execution mode parameter addition"]
            )
            
            self.analysis_results.append(analysis)
        else:
            # Missing component
            analysis = ComponentAnalysis(
                component_path="",
                component_name="LLMBuilder",
                proposed_module=ProposedModule.LLM_FACTORY,
                alignment_level=AlignmentLevel.MISSING,
                complexity_level=ComplexityLevel.HIGH,
                strengths=[],
                gaps=["Component not found"],
                code_examples=[],
                dependencies=[],
                breaking_changes=[]
            )
            self.analysis_results.append(analysis)
    
    def _analyze_crew_forge_module(self):
        """Analyze Crew Forge module alignment"""
        print("  🔧 Analyzing Crew Forge module...")
        
        # Analyze orchestrators
        db_orchestrator_path = self.codebase_root / "crew_forge/orchestrator/db/db_crew_orchestrator.py"
        file_orchestrator_path = self.codebase_root / "crew_forge/orchestrator/file/file_crew_orchestrator.py"
        
        for orchestrator_path, orchestrator_name in [
            (db_orchestrator_path, "DbCrewOrchestrator"),
            (file_orchestrator_path, "FileCrewOrchestrator")
        ]:
            if orchestrator_path.exists():
                code_content = orchestrator_path.read_text(encoding='utf-8')
                
                strengths = []
                gaps = []
                code_examples = []
                
                # Check for clean orchestration pattern
                if "def run_crew(" in code_content:
                    strengths.append("Clean orchestration pattern")
                    code_examples.append("def run_crew(self, crew_name: str, inputs: Dict[str, Any])")
                
                # Check for proper separation of concerns
                if "manager.build_atomic_crew" in code_content:
                    strengths.append("Proper separation - delegates to manager")
                    code_examples.append("crew_to_run = self.manager.build_atomic_crew(crew_name)")
                
                # Check for monitoring integration
                if "CrewPerformanceMonitor" in code_content:
                    strengths.append("Monitoring integration present")
                
                # Check for ExecutionSession abstraction
                if "ExecutionSession" not in code_content:
                    gaps.append("No ExecutionSession abstraction")
                
                # Check for execution mode support
                if "ExecutionMode" not in code_content:
                    gaps.append("No execution mode support")
                
                analysis = ComponentAnalysis(
                    component_path=str(orchestrator_path),
                    component_name=orchestrator_name,
                    proposed_module=ProposedModule.CREW_FORGE,
                    alignment_level=AlignmentLevel.PARTIALLY_ALIGNED,
                    complexity_level=ComplexityLevel.LOW,
                    strengths=strengths,
                    gaps=gaps,
                    code_examples=code_examples,
                    dependencies=["AtomicCrewManager", "CrewPerformanceMonitor"],
                    breaking_changes=["ExecutionSession API introduction", "Execution mode parameters"]
                )
                
                self.analysis_results.append(analysis)
    
    def _analyze_execution_state_module(self):
        """Analyze Execution State module alignment"""
        print("  💾 Analyzing Execution State module...")
        
        state_path = self.codebase_root / "execution_state/service/execution_state.py"
        
        if state_path.exists():
            analysis = ComponentAnalysis(
                component_path=str(state_path),
                component_name="ExecutionState",
                proposed_module=ProposedModule.EXECUTION_STATE,
                alignment_level=AlignmentLevel.FULLY_ALIGNED,
                complexity_level=ComplexityLevel.MEDIUM,
                strengths=["ExecutionState component exists"],
                gaps=[],
                code_examples=["class ExecutionState:"],
                dependencies=[],
                breaking_changes=[]
            )
            self.analysis_results.append(analysis)
        else:
            # This module doesn't exist in current codebase
            analysis = ComponentAnalysis(
                component_path="",
                component_name="ExecutionState",
                proposed_module=ProposedModule.EXECUTION_STATE,
                alignment_level=AlignmentLevel.MISSING,
                complexity_level=ComplexityLevel.HIGH,
                strengths=[],
                gaps=[
                    "No state persistence mechanism",
                    "No execution resumption capability", 
                    "No state injection support",
                    "No state container abstraction"
                ],
                code_examples=[],
                dependencies=[],
                breaking_changes=[
                    "New ExecutionState class introduction",
                    "State parameter addition to execution APIs",
                    "Serialization/deserialization requirements"
                ]
            )
            
            self.analysis_results.append(analysis)
    
    def _analyze_execution_runtime_module(self):
        """Analyze Execution Runtime module alignment"""
        print("  ⚡ Analyzing Execution Runtime module...")
        
        # Check current execution patterns in orchestrators
        execution_patterns = []
        
        # Scan orchestrators for execution patterns
        orchestrator_files = [
            self.codebase_root / "crew_forge/orchestrator/db/db_crew_orchestrator.py",
            self.codebase_root / "crew_forge/orchestrator/file/file_crew_orchestrator.py"
        ]
        
        for file_path in orchestrator_files:
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                if "result = crew_to_run.kickoff(inputs=inputs)" in content:
                    execution_patterns.append("Synchronous execution only")
        
        analysis = ComponentAnalysis(
            component_path="crew_forge/orchestrator/",
            component_name="ExecutionRuntime",
            proposed_module=ProposedModule.EXECUTION_RUNTIME,
            alignment_level=AlignmentLevel.MISSING,
            complexity_level=ComplexityLevel.HIGH,
            strengths=["Basic synchronous execution present"],
            gaps=[
                "No execution modes (interactive vs background)",
                "No execution handles",
                "No streaming abstraction",
                "No asynchronous execution support",
                "No execution cancellation"
            ],
            code_examples=execution_patterns,
            dependencies=["Current orchestrators"],
            breaking_changes=[
                "ExecutionHandle class introduction",
                "ExecutionMode enum addition",
                "Async execution API changes",
                "Streaming interface changes"
            ]
        )
        
        self.analysis_results.append(analysis)
    
    def _analyze_crew_monitor_module(self):
        """Analyze Crew Monitor module alignment"""
        print("  📊 Analyzing Crew Monitor module...")
        
        monitor_path = self.codebase_root / "crew_monitor/service/crew_performance_monitor.py"
        
        if monitor_path.exists():
            code_content = monitor_path.read_text(encoding='utf-8')
            
            strengths = []
            gaps = []
            code_examples = []
            
            # Check for comprehensive metrics
            if "get_metrics" in code_content:
                strengths.append("Comprehensive metrics collection")
                code_examples.append("def get_metrics(self) -> Dict[str, Any]")
            
            # Check for clean API
            if "start_monitoring" in code_content and "stop_monitoring" in code_content:
                strengths.append("Clean monitoring API")
            
            # Check for observer pattern
            if "observer" not in code_content.lower():
                gaps.append("No observer pattern - manual integration required")
            
            # Check for streaming support
            if "stream" not in code_content.lower():
                gaps.append("No streaming execution support")
            
            # Check for normalized metrics
            if "AmshaMetrics" not in code_content:
                gaps.append("No standardized metrics format")
            
            analysis = ComponentAnalysis(
                component_path=str(monitor_path),
                component_name="CrewPerformanceMonitor",
                proposed_module=ProposedModule.CREW_MONITOR,
                alignment_level=AlignmentLevel.PARTIALLY_ALIGNED,
                complexity_level=ComplexityLevel.LOW,
                strengths=strengths,
                gaps=gaps,
                code_examples=code_examples,
                dependencies=["psutil", "pynvml"],
                breaking_changes=["Observer pattern implementation", "AmshaMetrics standardization"]
            )
            
            self.analysis_results.append(analysis)
    
    def _detect_architectural_patterns(self):
        """Detect current architectural patterns"""
        print("  🏗️ Detecting architectural patterns...")
        
        # Detect Clean Architecture compliance
        self._detect_clean_architecture_pattern()
        
        # Detect Dependency Injection pattern
        self._detect_dependency_injection_pattern()
        
        # Detect Repository pattern
        self._detect_repository_pattern()
        
        # Detect Dual-mode architecture pattern
        self._detect_dual_mode_pattern()

        # Detect Client Responsibility pattern
        self._detect_client_responsibility_pattern()
    
    def _detect_client_responsibility_pattern(self):
        """Detect Client Responsibility pattern"""
        # Look for examples recursively in likely places
        example_files = list(self.codebase_root.glob("**/example/*.py"))
        
        client_loops = []
        for f in example_files:
            try:
                content = f.read_text(encoding='utf-8')
                if "while" in content or "for" in content or "try" in content:
                    client_loops.append(str(f))
            except Exception:
                pass
        
        pattern = ArchitecturalPattern(
            pattern_name="Client Flow Ownership",
            locations=client_loops,
            compliance_level="High" if len(client_loops) > 0 else "Low",
            description=f"Client-side control flow detected in {len(client_loops)} examples"
        )
        self.architectural_patterns.append(pattern)
    
    def _detect_clean_architecture_pattern(self):
        """Detect Clean Architecture pattern compliance"""
        domain_paths = list(self.codebase_root.glob("*/domain/**/*.py"))
        repo_interface_paths = list(self.codebase_root.glob("*/repo/interfaces/**/*.py"))
        
        compliance_issues = []
        
        # Check domain layer purity
        for domain_file in domain_paths:
            content = domain_file.read_text(encoding='utf-8')
            if "from crewai" in content or "import crewai" in content:
                compliance_issues.append(f"Domain layer has external dependency: {domain_file}")
        
        pattern = ArchitecturalPattern(
            pattern_name="Clean Architecture",
            locations=[str(p) for p in domain_paths + repo_interface_paths],
            compliance_level="Good" if len(compliance_issues) == 0 else "Partial",
            description=f"Domain layer purity: {'✅' if len(compliance_issues) == 0 else '⚠️'} ({len(compliance_issues)} violations found)"
        )
        
        self.architectural_patterns.append(pattern)
    
    def _detect_dependency_injection_pattern(self):
        """Detect Dependency Injection pattern usage"""
        di_files = []
        
        # Look for dependency injection containers
        container_files = list(self.codebase_root.glob("*/dependency/**/*.py"))
        
        for container_file in container_files:
            content = container_file.read_text(encoding='utf-8')
            if "dependency_injector" in content or "Container" in content:
                di_files.append(str(container_file))
        
        pattern = ArchitecturalPattern(
            pattern_name="Dependency Injection",
            locations=di_files,
            compliance_level="Good" if len(di_files) > 0 else "Missing",
            description=f"DI containers found: {len(di_files)}"
        )
        
        self.architectural_patterns.append(pattern)
    
    def _detect_repository_pattern(self):
        """Detect Repository pattern implementation"""
        interface_files = list(self.codebase_root.glob("*/repo/interfaces/**/*.py"))
        adapter_files = list(self.codebase_root.glob("*/repo/adapters/**/*.py"))
        
        pattern = ArchitecturalPattern(
            pattern_name="Repository Pattern",
            locations=[str(p) for p in interface_files + adapter_files],
            compliance_level="Good" if len(interface_files) > 0 and len(adapter_files) > 0 else "Partial",
            description=f"Interfaces: {len(interface_files)}, Adapters: {len(adapter_files)}"
        )
        
        self.architectural_patterns.append(pattern)
    
    def _detect_dual_mode_pattern(self):
        """Detect dual-mode architecture pattern"""
        db_files = list(self.codebase_root.glob("*/orchestrator/db/**/*.py"))
        file_files = list(self.codebase_root.glob("*/orchestrator/file/**/*.py"))
        
        # Check for parallel structure
        db_classes = set()
        file_classes = set()
        
        for db_file in db_files:
            content = db_file.read_text(encoding='utf-8')
            classes = re.findall(r'class (\w+):', content)
            db_classes.update(classes)
        
        for file_file in file_files:
            content = file_file.read_text(encoding='utf-8')
            classes = re.findall(r'class (\w+):', content)
            file_classes.update(classes)
        
        # Check for parallel naming (DbXxx vs FileXxx)
        parallel_classes = []
        for db_class in db_classes:
            if db_class.startswith('Db'):
                file_equivalent = db_class.replace('Db', 'File', 1)
                if file_equivalent in file_classes:
                    parallel_classes.append((db_class, file_equivalent))
        
        pattern = ArchitecturalPattern(
            pattern_name="Dual-Mode Architecture",
            locations=[str(p) for p in db_files + file_files],
            compliance_level="Good" if len(parallel_classes) > 0 else "Partial",
            description=f"Parallel implementations found: {len(parallel_classes)} pairs"
        )
        
        self.architectural_patterns.append(pattern)
    
    def _generate_alignment_report(self) -> Dict[str, Any]:
        """Generate comprehensive alignment report"""
        print("  📋 Generating alignment report...")
        
        # Categorize components by alignment level
        alignment_summary = {
            AlignmentLevel.FULLY_ALIGNED.value: [],
            AlignmentLevel.PARTIALLY_ALIGNED.value: [],
            AlignmentLevel.CONFLICTING.value: [],
            AlignmentLevel.MISSING.value: []
        }
        
        for analysis in self.analysis_results:
            alignment_summary[analysis.alignment_level.value].append({
                "component": analysis.component_name,
                "module": analysis.proposed_module.value,
                "complexity": analysis.complexity_level.value,
                "strengths_count": len(analysis.strengths),
                "gaps_count": len(analysis.gaps)
            })
        
        # Calculate overall feasibility score
        total_components = len(self.analysis_results)
        aligned_count = len(alignment_summary[AlignmentLevel.FULLY_ALIGNED.value])
        partial_count = len(alignment_summary[AlignmentLevel.PARTIALLY_ALIGNED.value])
        
        feasibility_score = (aligned_count * 1.0 + partial_count * 0.5) / total_components if total_components > 0 else 0
        
        report = {
            "analysis_summary": {
                "total_components_analyzed": total_components,
                "feasibility_score": round(feasibility_score, 2),
                "feasibility_level": self._get_feasibility_level(feasibility_score),
                "alignment_breakdown": alignment_summary
            },
            "detailed_analysis": [
                {
                    "component_name": analysis.component_name,
                    "component_path": analysis.component_path,
                    "proposed_module": analysis.proposed_module.value,
                    "alignment_level": analysis.alignment_level.value,
                    "complexity_level": analysis.complexity_level.value,
                    "strengths": analysis.strengths,
                    "gaps": analysis.gaps,
                    "code_examples": analysis.code_examples,
                    "dependencies": analysis.dependencies,
                    "breaking_changes": analysis.breaking_changes
                }
                for analysis in self.analysis_results
            ],
            "architectural_patterns": [
                {
                    "pattern_name": pattern.pattern_name,
                    "locations": pattern.locations,
                    "compliance_level": pattern.compliance_level,
                    "description": pattern.description
                }
                for pattern in self.architectural_patterns
            ],
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _get_feasibility_level(self, score: float) -> str:
        """Convert feasibility score to level"""
        if score >= 0.8:
            return "High Feasibility"
        elif score >= 0.5:
            return "Medium Feasibility"
        else:
            return "Low Feasibility"
    
    def _generate_recommendations(self) -> List[str]:
        """Generate implementation recommendations"""
        recommendations = []
        
        # Analyze gaps and generate recommendations
        all_gaps = []
        for analysis in self.analysis_results:
            all_gaps.extend(analysis.gaps)
        
        # Count common gaps
        gap_counts = {}
        for gap in all_gaps:
            gap_counts[gap] = gap_counts.get(gap, 0) + 1
        
        # Generate recommendations based on most common gaps
        if "No execution mode" in str(all_gaps):
            recommendations.append("Implement ExecutionMode enum and execution-aware APIs as foundation")
        
        if "No state" in str(all_gaps):
            recommendations.append("Create ExecutionState module as new infrastructure component")
        
        if "Direct crewai" in str(all_gaps):
            recommendations.append("Introduce ILLMProvider abstraction to decouple from CrewAI framework")
        
        if "No observer pattern" in str(all_gaps):
            recommendations.append("Refactor monitoring to use observer pattern for automatic instrumentation")
        
        recommendations.append("Maintain backward compatibility through adapter pattern during migration")
        recommendations.append("Implement changes incrementally, starting with least disruptive modules")
        
        return recommendations
    
    def generate_report_file(self, output_path: str = "architectural_alignment_report.json"):
        """Generate and save alignment report to file"""
        report = self.analyze_codebase()
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Alignment report saved to: {output_path}")
        return report
    
    def print_summary(self):
        """Print a summary of the alignment analysis"""
        report = self.analyze_codebase()
        
        print("\n" + "="*60)
        print("🏗️  ARCHITECTURAL ALIGNMENT SUMMARY")
        print("="*60)
        
        summary = report["analysis_summary"]
        print(f"📊 Feasibility Score: {summary['feasibility_score']}/1.0 ({summary['feasibility_level']})")
        print(f"🔍 Components Analyzed: {summary['total_components_analyzed']}")
        
        print("\n📋 Alignment Breakdown:")
        for level, components in summary["alignment_breakdown"].items():
            if components:
                print(f"  {level.replace('_', ' ').title()}: {len(components)} components")
                for comp in components:
                    print(f"    - {comp['component']} ({comp['module']}) - {comp['complexity']} complexity")
        
        print("\n🏗️ Architectural Patterns:")
        for pattern in report["architectural_patterns"]:
            print(f"  {pattern['pattern_name']}: {pattern['compliance_level']}")
            print(f"    {pattern['description']}")
        
        print("\n💡 Key Recommendations:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "="*60)


if __name__ == "__main__":
    # Example usage
    tool = ArchitecturalAlignmentTool()
    tool.print_summary()
    tool.generate_report_file()