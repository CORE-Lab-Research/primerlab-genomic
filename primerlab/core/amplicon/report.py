"""
Amplicon Analysis Report Generation.

Generates Markdown and JSON reports for amplicon quality analysis.
"""

import json
from pathlib import Path
from typing import Dict, Any

from .models import AmpliconAnalysisResult
from .gc_profile import generate_ascii_plot


def generate_amplicon_json_report(result: AmpliconAnalysisResult, output_dir: str) -> str:
    """Generate JSON report for amplicon analysis."""
    output_path = Path(output_dir) / "amplicon_analysis.json"
    
    with open(output_path, "w") as f:
        json.dump(result.to_dict(), f, indent=2)
    
    return str(output_path)


def generate_amplicon_markdown_report(result: AmpliconAnalysisResult, output_dir: str) -> str:
    """Generate Markdown report for amplicon analysis."""
    output_path = Path(output_dir) / "amplicon_report.md"
    
    lines = [
        "# Amplicon Quality Report",
        "",
        f"**Length:** {result.length} bp",
        "",
    ]
    
    # Quality Score
    if result.quality:
        lines.extend([
            "## Quality Score",
            "",
            f"**Overall: {result.quality.score:.1f}/100 (Grade: {result.quality.grade})**",
            "",
            "| Component | Score |",
            "|-----------|-------|",
            f"| Secondary Structure | {result.quality.structure_score:.1f} |",
            f"| GC Uniformity | {result.quality.gc_uniformity_score:.1f} |",
            f"| GC Clamp | {result.quality.gc_clamp_score:.1f} |",
            f"| Length | {result.quality.length_score:.1f} |",
            f"| Tm Sharpness | {result.quality.tm_sharpness_score:.1f} |",
            "",
        ])
        
        if result.quality.warnings:
            lines.append("### Warnings")
            lines.append("")
            for w in result.quality.warnings:
                lines.append(f"- ⚠️ {w}")
            lines.append("")
    
    # Secondary Structure
    if result.secondary_structure:
        ss = result.secondary_structure
        status = "⚠️ Problematic" if ss.is_problematic else "✅ OK"
        lines.extend([
            "## Secondary Structure",
            "",
            f"**Status:** {status}",
            f"**ΔG:** {ss.delta_g:.2f} kcal/mol",
            "",
        ])
    
    # GC Profile
    if result.gc_profile:
        gp = result.gc_profile
        lines.extend([
            "## GC Profile",
            "",
            f"**Average GC:** {gp.avg_gc:.1f}%",
            f"**Range:** {gp.min_gc:.1f}% - {gp.max_gc:.1f}%",
            f"**Uniformity Score:** {gp.uniformity_score:.1f}/100",
            "",
            "```",
            generate_ascii_plot(gp),
            "```",
            "",
        ])
    
    # Melting Temperature
    if result.amplicon_tm:
        lines.extend([
            "## Melting Temperature",
            "",
            f"**Predicted Tm:** {result.amplicon_tm.tm}°C",
            f"**Method:** {result.amplicon_tm.method}",
            "",
        ])
    
    # Restriction Sites
    if result.restriction_sites:
        lines.append("## Restriction Sites")
        lines.append("")
        lines.append("| Enzyme | Position | Recognition |")
        lines.append("|--------|----------|-------------|")
        for rs in result.restriction_sites:
            lines.append(f"| {rs.enzyme} | {rs.position} | {rs.recognition_seq} |")
        lines.append("")
    
    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    
    return str(output_path)
