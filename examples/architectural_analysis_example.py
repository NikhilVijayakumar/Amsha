#!/usr/bin/env python3
"""
Example: Using the Architectural Alignment Assessment Tool
for Amsha 2.0 Feasibility Analysis

This example demonstrates how to use the tool to analyze the current
codebase and generate actionable insights for the 2.0 architecture migration.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nikhil.amsha.analysis import (
    ArchitecturalAlignmentTool, 
    AlignmentLevel, 
    ComplexityLevel,
    ProposedModule
)

def main():
    """Demonstrate architectural alignment analysis"""
    
    print("🏗️ Amsha 2.0 Architectural Alignment Analysis")
    print("=" * 60)
    
    # Initialize the assessment tool
    tool = ArchitecturalAlignmentTool()
    
    # Run comprehensive analysis
    print("🔍 Running comprehensive codebase analysis...")
    report = tool.analyze_codebase()
    
    # Display high-level summary
    print(f"\n📊 Analysis Results:")
    print(f"   Feasibility Score: {report['analysis_summary']['feasibility_score']}/1.0")
    print(f"   Feasibility Level: {report['analysis_summary']['feasibility_level']}")
    print(f"   Components Analyzed: {report['analysis_summary']['total_components_analyzed']}")
    
    # Analyze by proposed module
    print(f"\n📦 Analysis by Proposed 2.0 Module:")
    
    module_analysis = {}
    for analysis in report['detailed_analysis']:
        module = analysis['proposed_module']
        if module not in module_analysis:
            module_analysis[module] = {
                'components': [],
                'total_gaps': 0,
                'total_strengths': 0,
                'max_complexity': 'low'
            }
        
        module_analysis[module]['components'].append(analysis)
        module_analysis[module]['total_gaps'] += len(analysis['gaps'])
        module_analysis[module]['total_strengths'] += len(analysis['strengths'])
        
        # Track highest complexity
        if analysis['complexity_level'] == 'high':
            module_analysis[module]['max_complexity'] = 'high'
        elif analysis['complexity_level'] == 'medium' and module_analysis[module]['max_complexity'] == 'low':
            module_analysis[module]['max_complexity'] = 'medium'
    
    for module, data in module_analysis.items():
        print(f"\n   🔧 {module.replace('_', ' ').title()}:")
        print(f"      Components: {len(data['components'])}")
        print(f"      Max Complexity: {data['max_complexity']}")
        print(f"      Total Gaps: {data['total_gaps']}")
        print(f"      Total Strengths: {data['total_strengths']}")
        
        # Show component details
        for comp in data['components']:
            alignment_emoji = {
                'fully_aligned': '✅',
                'partially_aligned': '⚠️',
                'conflicting': '❌',
                'missing': '🚫'
            }
            emoji = alignment_emoji.get(comp['alignment_level'], '❓')
            print(f"        {emoji} {comp['component_name']} ({comp['alignment_level']})")
    
    # Highlight critical gaps
    print(f"\n🚨 Critical Implementation Gaps:")
    
    missing_components = [
        analysis for analysis in report['detailed_analysis'] 
        if analysis['alignment_level'] == 'missing'
    ]
    
    for comp in missing_components:
        print(f"   🚫 {comp['component_name']} ({comp['proposed_module']})")
        print(f"      Complexity: {comp['complexity_level']}")
        for gap in comp['gaps'][:3]:  # Show first 3 gaps
            print(f"      - {gap}")
    
    # Show architectural pattern compliance
    print(f"\n🏛️ Architectural Pattern Compliance:")
    for pattern in report['architectural_patterns']:
        compliance_emoji = {
            'Good': '✅',
            'Partial': '⚠️',
            'Missing': '❌'
        }
        emoji = compliance_emoji.get(pattern['compliance_level'], '❓')
        print(f"   {emoji} {pattern['pattern_name']}: {pattern['compliance_level']}")
        print(f"      {pattern['description']}")
    
    # Implementation roadmap suggestions
    print(f"\n🗺️ Suggested Implementation Roadmap:")
    
    # Group by complexity and alignment
    low_complexity = [a for a in report['detailed_analysis'] if a['complexity_level'] == 'low']
    medium_complexity = [a for a in report['detailed_analysis'] if a['complexity_level'] == 'medium']
    high_complexity = [a for a in report['detailed_analysis'] if a['complexity_level'] == 'high']
    
    print(f"\n   Phase 1 (Low Risk): {len(low_complexity)} components")
    for comp in low_complexity:
        if comp['alignment_level'] == 'partially_aligned':
            print(f"      ⚡ Enhance {comp['component_name']} ({comp['proposed_module']})")
    
    print(f"\n   Phase 2 (Medium Risk): {len(medium_complexity)} components")
    for comp in medium_complexity:
        print(f"      🔧 Refactor {comp['component_name']} ({comp['proposed_module']})")
    
    print(f"\n   Phase 3 (High Risk): {len(high_complexity)} components")
    for comp in high_complexity:
        print(f"      🏗️ Build {comp['component_name']} ({comp['proposed_module']})")
    
    # Save detailed report
    output_file = "amsha_2.0_feasibility_analysis.json"
    tool.generate_report_file(output_file)
    print(f"\n📄 Detailed report saved to: {output_file}")
    
    # Final recommendations
    print(f"\n💡 Key Recommendations:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"   {i}. {rec}")
    
    print(f"\n✅ Analysis complete! Use the detailed report for implementation planning.")

if __name__ == "__main__":
    main()