"""
Probe Position Analysis and Optimization.

Analyzes probe position within the amplicon and provides optimization
recommendations for TaqMan qPCR assays.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProbePositionResult:
    """Result of probe position analysis."""
    probe_start: int
    probe_end: int
    distance_from_fwd: int
    distance_from_rev: int
    amplicon_coverage: float  # percentage
    position_score: float
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "probe_start": self.probe_start,
            "probe_end": self.probe_end,
            "distance_from_fwd": self.distance_from_fwd,
            "distance_from_rev": self.distance_from_rev,
            "amplicon_coverage": round(self.amplicon_coverage, 1),
            "position_score": round(self.position_score, 1),
            "warnings": self.warnings,
            "recommendations": self.recommendations,
        }


def analyze_probe_position(
    probe_sequence: str,
    amplicon_sequence: str,
    fwd_primer_end: int = 0,
    rev_primer_start: Optional[int] = None,
) -> ProbePositionResult:
    """
    Analyze probe position within amplicon.
    
    Args:
        probe_sequence: Probe sequence (5' to 3')
        amplicon_sequence: Full amplicon sequence
        fwd_primer_end: Position where forward primer ends
        rev_primer_start: Position where reverse primer starts
        
    Returns:
        ProbePositionResult with analysis
    """
    warnings = []
    recommendations = []
    
    probe_upper = probe_sequence.upper()
    amplicon_upper = amplicon_sequence.upper()
    
    # Find probe in amplicon
    probe_start = amplicon_upper.find(probe_upper)
    
    if probe_start == -1:
        # Try reverse complement
        probe_rc = reverse_complement(probe_upper)
        probe_start = amplicon_upper.find(probe_rc)
        if probe_start != -1:
            recommendations.append("Probe binds to antisense strand")
    
    if probe_start == -1:
        return ProbePositionResult(
            probe_start=-1,
            probe_end=-1,
            distance_from_fwd=0,
            distance_from_rev=0,
            amplicon_coverage=0.0,
            position_score=0.0,
            warnings=["Probe not found in amplicon sequence"],
            recommendations=["Verify probe sequence matches template"],
        )
    
    probe_end = probe_start + len(probe_sequence) - 1
    amplicon_len = len(amplicon_sequence)
    
    if rev_primer_start is None:
        rev_primer_start = amplicon_len
    
    # Calculate distances
    distance_from_fwd = probe_start - fwd_primer_end
    distance_from_rev = rev_primer_start - probe_end
    
    # Coverage
    amplicon_coverage = (len(probe_sequence) / amplicon_len) * 100
    
    # Position scoring
    score = 100.0
    
    # Distance from primers (optimal: 5-50 bp)
    if distance_from_fwd < 5:
        score -= 20
        warnings.append(f"Probe too close to forward primer ({distance_from_fwd} bp)")
        recommendations.append("Move probe at least 5 bp from forward primer")
    elif distance_from_fwd > 50:
        score -= 5
        recommendations.append("Consider moving probe closer to forward primer")
    
    if distance_from_rev < 5:
        score -= 20
        warnings.append(f"Probe too close to reverse primer ({distance_from_rev} bp)")
        recommendations.append("Move probe at least 5 bp from reverse primer")
    elif distance_from_rev > 50:
        score -= 5
        recommendations.append("Consider moving probe closer to reverse primer")
    
    # Probe length check
    probe_len = len(probe_sequence)
    if probe_len < 18:
        score -= 15
        warnings.append(f"Probe too short ({probe_len} bp)")
    elif probe_len > 30:
        score -= 10
        warnings.append(f"Probe too long ({probe_len} bp)")
    
    # Check 5' nucleotide
    first_base = probe_sequence[0].upper()
    if first_base == 'G':
        score -= 10
        warnings.append("5' G may quench fluorescence")
        recommendations.append("Avoid G at 5' end of probe")
    
    score = max(0.0, min(100.0, score))
    
    return ProbePositionResult(
        probe_start=probe_start,
        probe_end=probe_end,
        distance_from_fwd=distance_from_fwd,
        distance_from_rev=distance_from_rev,
        amplicon_coverage=amplicon_coverage,
        position_score=score,
        warnings=warnings,
        recommendations=recommendations,
    )


def optimize_probe_position(
    amplicon_sequence: str,
    fwd_primer_end: int = 0,
    rev_primer_start: Optional[int] = None,
    probe_length: int = 20,
    min_distance: int = 5,
    avoid_5_g: bool = True,
) -> List[Dict[str, Any]]:
    """
    Find optimal probe positions within amplicon.
    
    Args:
        amplicon_sequence: Full amplicon sequence
        fwd_primer_end: Position where forward primer ends
        rev_primer_start: Position where reverse primer starts
        probe_length: Target probe length
        min_distance: Minimum distance from primers
        avoid_5_g: Avoid G at 5' end
        
    Returns:
        List of candidate positions with scores
    """
    amplicon_len = len(amplicon_sequence)
    if rev_primer_start is None:
        rev_primer_start = amplicon_len
    
    candidates = []
    
    # Search region between primers
    search_start = fwd_primer_end + min_distance
    search_end = rev_primer_start - min_distance - probe_length
    
    if search_end <= search_start:
        return []  # Amplicon too short
    
    for pos in range(search_start, search_end + 1):
        probe_seq = amplicon_sequence[pos:pos + probe_length]
        
        # Skip if 5' G
        if avoid_5_g and probe_seq[0].upper() == 'G':
            continue
        
        # Calculate GC content
        gc_count = probe_seq.upper().count('G') + probe_seq.upper().count('C')
        gc_percent = (gc_count / len(probe_seq)) * 100
        
        # Skip if GC outside range
        if gc_percent < 30 or gc_percent > 80:
            continue
        
        # Score based on position (prefer middle of amplicon)
        center_distance = abs((pos + probe_length / 2) - (amplicon_len / 2))
        position_score = 100 - (center_distance / amplicon_len * 50)
        
        # Adjust for GC (prefer 40-60%)
        if 40 <= gc_percent <= 60:
            position_score += 10
        
        candidates.append({
            "start": pos,
            "end": pos + probe_length - 1,
            "sequence": probe_seq,
            "gc_percent": round(gc_percent, 1),
            "score": round(position_score, 1),
        })
    
    # Sort by score
    candidates.sort(key=lambda x: x["score"], reverse=True)
    
    return candidates[:10]  # Return top 10


def reverse_complement(sequence: str) -> str:
    """Return reverse complement of DNA sequence."""
    complement = {"A": "T", "T": "A", "G": "C", "C": "G", "N": "N"}
    return "".join(complement.get(base, "N") for base in reversed(sequence.upper()))
