"""
Amplicon Analysis Module.

Provides comprehensive amplicon quality analysis including:
- Secondary structure prediction
- GC profile visualization
- GC clamp analysis
- Melting temperature prediction
- Restriction site mapping
- Overall quality scoring
"""

from .models import (
    SecondaryStructure,
    GCProfile,
    GCClamp,
    AmpliconTm,
    RestrictionSite,
    AmpliconQuality,
    AmpliconAnalysisResult,
)
from .analyzer import AmpliconAnalyzer, analyze_amplicon
from .secondary_structure import SecondaryStructureAnalyzer
from .gc_profile import calculate_gc_profile, generate_ascii_plot
from .gc_clamp import analyze_gc_clamp
from .tm_prediction import predict_amplicon_tm
from .restriction_sites import find_restriction_sites, get_available_enzymes
from .quality_score import calculate_quality_score, score_to_grade
from .report import (
    generate_amplicon_json_report,
    generate_amplicon_markdown_report,
    generate_amplicon_excel_report,
)

__all__ = [
    # Models
    "SecondaryStructure",
    "GCProfile",
    "GCClamp",
    "AmpliconTm",
    "RestrictionSite",
    "AmpliconQuality",
    "AmpliconAnalysisResult",
    # Main analyzer
    "AmpliconAnalyzer",
    "analyze_amplicon",
    # Sub-analyzers
    "SecondaryStructureAnalyzer",
    "calculate_gc_profile",
    "generate_ascii_plot",
    "analyze_gc_clamp",
    "predict_amplicon_tm",
    "find_restriction_sites",
    "get_available_enzymes",
    "calculate_quality_score",
    "score_to_grade",
    # Reports (v0.4.1)
    "generate_amplicon_json_report",
    "generate_amplicon_markdown_report",
    "generate_amplicon_excel_report",
]
