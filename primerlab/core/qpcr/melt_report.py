"""
Melt Curve Analysis Report Generation.

Generates reports for SYBR Green melt curve analysis.
"""

from typing import Dict, List, Any
from .melt_curve import MeltCurveResult


def generate_melt_markdown(result: MeltCurveResult) -> str:
    """
    Generate markdown report for melt curve analysis.
    
    Args:
        result: MeltCurveResult from predict_melt_curve()
        
    Returns:
        Markdown formatted report string
    """
    lines = [
        "# SYBR Green Melt Curve Analysis",
        "",
        "## Summary",
        "",
        f"| Property | Value |",
        f"|----------|-------|",
        f"| Amplicon Length | {len(result.amplicon_sequence)} bp |",
        f"| Predicted Tm | {result.predicted_tm:.1f}°C |",
        f"| Tm Range | {result.tm_range[0]:.1f} - {result.tm_range[1]:.1f}°C |",
        f"| Single Peak | {'Yes ✅' if result.is_single_peak else 'No ⚠️'} |",
        f"| Quality Score | {result.quality_score:.1f} |",
        f"| Grade | {result.grade} |",
        "",
    ]
    
    # Peaks section
    if len(result.peaks) > 0:
        lines.extend([
            "## Detected Peaks",
            "",
            "| Peak | Temperature | Height | Width | Type |",
            "|------|-------------|--------|-------|------|",
        ])
        for i, peak in enumerate(result.peaks, 1):
            peak_type = "Primary" if peak.is_primary else "Secondary"
            lines.append(
                f"| {i} | {peak.temperature:.1f}°C | {peak.height:.2f} | {peak.width:.1f}°C | {peak_type} |"
            )
        lines.append("")
    
    # Warnings
    if result.warnings:
        lines.extend([
            "## Warnings",
            "",
        ])
        for warning in result.warnings:
            lines.append(f"- ⚠️ {warning}")
        lines.append("")
    
    # Interpretation
    lines.extend([
        "## Interpretation",
        "",
    ])
    
    if result.is_single_peak and result.grade in ["A", "B"]:
        lines.append("✅ **Excellent**: Single clean melt peak indicates specific amplification.")
    elif result.is_single_peak:
        lines.append("👍 **Good**: Single peak detected. Check warnings for potential issues.")
    else:
        lines.append("⚠️ **Review Required**: Multiple peaks suggest non-specific products or primer-dimers.")
    
    lines.append("")
    
    return "\n".join(lines)


def generate_melt_csv(result: MeltCurveResult) -> str:
    """
    Generate CSV data for melt curve.
    
    Args:
        result: MeltCurveResult from predict_melt_curve()
        
    Returns:
        CSV formatted string
    """
    lines = ["Temperature (°C),-dF/dT"]
    
    for point in result.melt_curve:
        lines.append(f"{point['temperature']},{point['derivative']}")
    
    return "\n".join(lines)


def generate_melt_json(result: MeltCurveResult) -> Dict[str, Any]:
    """
    Generate JSON-compatible dict for melt curve.
    
    Args:
        result: MeltCurveResult from predict_melt_curve()
        
    Returns:
        Dictionary with all melt curve data
    """
    return result.to_dict()
