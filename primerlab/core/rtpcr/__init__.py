"""
RT-qPCR Module (v0.6.0).

Provides RT-qPCR-specific primer validation including:
- Exon junction detection
- gDNA contamination risk assessment
- Transcript annotation loading
"""

from .exon_junction import (
    detect_exon_junction,
    find_junction_position,
    ExonJunctionResult,
)
from .gdna_check import (
    check_gdna_risk,
    GdnaRiskResult,
)
from .transcript_loader import (
    Exon,
    Transcript,
    parse_gtf_line,
    load_transcript_bed,
)

__all__ = [
    # Exon junction
    "detect_exon_junction",
    "find_junction_position",
    "ExonJunctionResult",
    # gDNA check
    "check_gdna_risk",
    "GdnaRiskResult",
    # Transcript loader
    "Exon",
    "Transcript",
    "parse_gtf_line",
    "load_transcript_bed",
]
