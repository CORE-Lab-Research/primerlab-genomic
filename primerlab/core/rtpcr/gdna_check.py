"""
gDNA Contamination Risk Checker (v0.6.0).

Assesses risk of genomic DNA amplification in RT-qPCR.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple


@dataclass
class GdnaRiskResult:
    """Result of gDNA contamination risk assessment."""
    
    # Primer positions (in transcript coordinates)
    fwd_start: int
    fwd_end: int
    rev_start: int
    rev_end: int
    
    # Risk assessment
    risk_level: str  # "None", "Low", "Medium", "High"
    risk_score: float  # 0-100 (higher = more risk)
    
    # Details
    fwd_spans_junction: bool
    rev_spans_junction: bool
    intron_between: bool
    intron_size: Optional[int]
    
    # Recommendations
    is_rt_specific: bool
    warnings: List[str]
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "fwd_start": self.fwd_start,
            "fwd_end": self.fwd_end,
            "rev_start": self.rev_start,
            "rev_end": self.rev_end,
            "risk_level": self.risk_level,
            "risk_score": self.risk_score,
            "fwd_spans_junction": self.fwd_spans_junction,
            "rev_spans_junction": self.rev_spans_junction,
            "intron_between": self.intron_between,
            "intron_size": self.intron_size,
            "is_rt_specific": self.is_rt_specific,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
        }


def check_gdna_risk(
    fwd_start: int,
    fwd_end: int,
    rev_start: int,
    rev_end: int,
    exon_boundaries: List[Tuple[int, int]],
    genomic_intron_sizes: Optional[List[int]] = None,
    min_intron_for_no_amplification: int = 1000,
) -> GdnaRiskResult:
    """
    Check gDNA contamination risk for RT-qPCR primer pair.
    
    Risk is LOW if:
    - At least one primer spans exon junction, OR
    - Large intron (>1kb) exists between primers in genomic coordinates
    
    Risk is HIGH if:
    - Both primers in same exon
    - No intron or small intron between
    
    Args:
        fwd_start: Forward primer start (transcript coordinates)
        fwd_end: Forward primer end
        rev_start: Reverse primer start
        rev_end: Reverse primer end
        exon_boundaries: List of (start, end) for each exon
        genomic_intron_sizes: Optional list of intron sizes between exons
        min_intron_for_no_amplification: Minimum intron size to prevent gDNA amp
        
    Returns:
        GdnaRiskResult with risk assessment
    """
    warnings = []
    recommendations = []
    
    # Determine which exons primers are in
    fwd_exons = set()
    rev_exons = set()
    
    for idx, (exon_start, exon_end) in enumerate(exon_boundaries):
        # Forward primer overlaps this exon?
        if fwd_start < exon_end and fwd_end > exon_start:
            fwd_exons.add(idx)
        # Reverse primer overlaps?
        if rev_start < exon_end and rev_end > exon_start:
            rev_exons.add(idx)
    
    # Check if primers span junctions
    fwd_spans_junction = len(fwd_exons) > 1
    rev_spans_junction = len(rev_exons) > 1
    
    # Check if intron exists between primers
    intron_between = False
    intron_size = None
    
    if fwd_exons and rev_exons:
        min_fwd_exon = min(fwd_exons)
        max_rev_exon = max(rev_exons)
        
        if max_rev_exon > min_fwd_exon:
            intron_between = True
            
            # Calculate intron size if available
            if genomic_intron_sizes:
                total_intron = 0
                for i in range(min_fwd_exon, min(max_rev_exon, len(genomic_intron_sizes))):
                    total_intron += genomic_intron_sizes[i]
                intron_size = total_intron
    
    # Calculate risk
    if fwd_spans_junction or rev_spans_junction:
        # Junction-spanning = RT-specific
        risk_level = "None"
        risk_score = 0.0
        is_rt_specific = True
    elif intron_between and intron_size and intron_size >= min_intron_for_no_amplification:
        # Large intron = unlikely to amplify gDNA
        risk_level = "Low"
        risk_score = 20.0
        is_rt_specific = True
        recommendations.append(f"Intron ({intron_size} bp) should prevent gDNA amplification")
    elif intron_between:
        # Small intron = might still amplify gDNA
        risk_level = "Medium"
        risk_score = 50.0
        is_rt_specific = False
        warnings.append("Small intron between primers - gDNA may amplify")
        recommendations.append("Consider designing primers that span exon junctions")
    else:
        # Same exon or no intron
        risk_level = "High"
        risk_score = 90.0
        is_rt_specific = False
        warnings.append("Both primers in same exon - will amplify gDNA")
        recommendations.append("Redesign primers to span exon-exon junction")
        recommendations.append("Or use DNase treatment before RT")
    
    return GdnaRiskResult(
        fwd_start=fwd_start,
        fwd_end=fwd_end,
        rev_start=rev_start,
        rev_end=rev_end,
        risk_level=risk_level,
        risk_score=risk_score,
        fwd_spans_junction=fwd_spans_junction,
        rev_spans_junction=rev_spans_junction,
        intron_between=intron_between,
        intron_size=intron_size,
        is_rt_specific=is_rt_specific,
        warnings=warnings,
        recommendations=recommendations,
    )
