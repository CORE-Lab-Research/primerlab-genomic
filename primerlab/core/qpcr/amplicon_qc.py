"""
qPCR-specific Amplicon Quality Control.

Validates amplicon properties for optimal qPCR performance.
Integrates with existing amplicon analysis module.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class QpcrAmpliconQC:
    """qPCR amplicon quality control result."""
    amplicon_length: int
    gc_content: float
    gc_ok: bool
    length_ok: bool
    secondary_structure_ok: bool
    tm_amplicon: float
    secondary_structure_dg: float
    quality_score: float
    grade: str
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "amplicon_length": self.amplicon_length,
            "gc_content": round(self.gc_content, 1),
            "gc_ok": self.gc_ok,
            "length_ok": self.length_ok,
            "secondary_structure_ok": self.secondary_structure_ok,
            "tm_amplicon": round(self.tm_amplicon, 1),
            "secondary_structure_dg": round(self.secondary_structure_dg, 2),
            "quality_score": round(self.quality_score, 1),
            "grade": self.grade,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
        }


# qPCR optimal ranges
QPCR_AMPLICON_MIN = 70
QPCR_AMPLICON_MAX = 150
QPCR_AMPLICON_OPTIMAL = 100
QPCR_GC_MIN = 40.0
QPCR_GC_MAX = 60.0
QPCR_GC_OPTIMAL = 50.0


def calculate_gc_content(sequence: str) -> float:
    """Calculate GC content percentage."""
    seq = sequence.upper()
    gc_count = seq.count('G') + seq.count('C')
    return (gc_count / len(seq)) * 100 if len(seq) > 0 else 0.0


def estimate_amplicon_tm(sequence: str) -> float:
    """
    Estimate amplicon melting temperature.
    
    Uses the basic Marmur-Doty formula for longer sequences:
    Tm = 81.5 + 16.6*log10([Na+]) + 0.41*(%GC) - 675/length
    
    Simplified for 50mM Na+.
    """
    if len(sequence) == 0:
        return 0.0
    
    gc_percent = calculate_gc_content(sequence)
    length = len(sequence)
    
    # Marmur-Doty with 50mM Na+ correction
    # log10(0.05) ≈ -1.3
    tm = 81.5 + 16.6 * (-1.3) + 0.41 * gc_percent - 675 / length
    
    return max(0.0, tm)


def estimate_secondary_structure_dg(sequence: str) -> float:
    """
    Estimate secondary structure stability (ΔG).
    
    Simple heuristic based on GC content and self-complementary regions.
    More negative = more stable structure = worse for qPCR.
    """
    if len(sequence) < 10:
        return 0.0
    
    gc_percent = calculate_gc_content(sequence)
    
    # Higher GC = more stable secondary structures
    base_dg = -0.5 * (gc_percent / 100) * len(sequence) * 0.1
    
    # Check for simple self-complementary patterns
    seq = sequence.upper()
    penalty = 0.0
    
    # Check for GC-rich regions (potential hairpins)
    for i in range(len(seq) - 5):
        window = seq[i:i+6]
        gc_in_window = window.count('G') + window.count('C')
        if gc_in_window >= 5:  # 5 or more GC in 6bp
            penalty -= 0.5
    
    return base_dg + penalty


def validate_qpcr_amplicon(
    amplicon_sequence: str,
    min_length: int = QPCR_AMPLICON_MIN,
    max_length: int = QPCR_AMPLICON_MAX,
    gc_min: float = QPCR_GC_MIN,
    gc_max: float = QPCR_GC_MAX,
) -> QpcrAmpliconQC:
    """
    Validate amplicon for qPCR.
    
    Args:
        amplicon_sequence: Amplicon DNA sequence
        min_length: Minimum acceptable length
        max_length: Maximum acceptable length
        gc_min: Minimum GC%
        gc_max: Maximum GC%
        
    Returns:
        QpcrAmpliconQC with validation results
    """
    warnings = []
    recommendations = []
    
    length = len(amplicon_sequence)
    gc_content = calculate_gc_content(amplicon_sequence)
    tm = estimate_amplicon_tm(amplicon_sequence)
    dg = estimate_secondary_structure_dg(amplicon_sequence)
    
    # Validate length
    length_ok = min_length <= length <= max_length
    if not length_ok:
        if length < min_length:
            warnings.append(f"Amplicon too short ({length} bp). Minimum {min_length} bp for qPCR.")
            recommendations.append("Extend amplicon by adjusting primer positions.")
        else:
            warnings.append(f"Amplicon too long ({length} bp). Maximum {max_length} bp for optimal qPCR.")
            recommendations.append("Use closer primer positions for shorter amplicon.")
    
    # Validate GC content
    gc_ok = gc_min <= gc_content <= gc_max
    if not gc_ok:
        if gc_content < gc_min:
            warnings.append(f"GC content too low ({gc_content:.1f}%). Minimum {gc_min}%.")
            recommendations.append("Shift amplicon to include more GC-rich regions.")
        else:
            warnings.append(f"GC content too high ({gc_content:.1f}%). Maximum {gc_max}%.")
            recommendations.append("Avoid GC-rich regions which may form secondary structures.")
    
    # Validate secondary structure
    # More negative ΔG = more stable = problematic
    secondary_structure_ok = dg > -5.0
    if not secondary_structure_ok:
        warnings.append(f"Potential stable secondary structure (ΔG = {dg:.1f} kcal/mol).")
        recommendations.append("Check for hairpin-forming sequences and consider alternative regions.")
    
    # Calculate quality score (0-100)
    score = 100.0
    
    # Length score
    if length_ok:
        # Bonus for optimal length (around 100bp)
        length_deviation = abs(length - QPCR_AMPLICON_OPTIMAL) / QPCR_AMPLICON_OPTIMAL
        score -= length_deviation * 10
    else:
        score -= 25
    
    # GC score
    if gc_ok:
        gc_deviation = abs(gc_content - QPCR_GC_OPTIMAL) / QPCR_GC_OPTIMAL
        score -= gc_deviation * 10
    else:
        score -= 20
    
    # Secondary structure score
    if secondary_structure_ok:
        score -= abs(dg) * 2
    else:
        score -= 20
    
    score = max(0.0, min(100.0, score))
    
    # Grade
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"
    
    return QpcrAmpliconQC(
        amplicon_length=length,
        gc_content=gc_content,
        gc_ok=gc_ok,
        length_ok=length_ok,
        secondary_structure_ok=secondary_structure_ok,
        tm_amplicon=tm,
        secondary_structure_dg=dg,
        quality_score=score,
        grade=grade,
        warnings=warnings,
        recommendations=recommendations,
    )


def score_qpcr_efficiency(
    amplicon_length: int,
    primer_tm_diff: float,
    probe_tm_diff: float = 0.0,
    hairpin_penalty: float = 0.0,
    dimer_penalty: float = 0.0,
) -> float:
    """
    Enhanced qPCR efficiency scoring.
    
    Args:
        amplicon_length: Length of amplicon in bp
        primer_tm_diff: Difference between forward and reverse Tm
        probe_tm_diff: Difference between probe Tm and primer average (TaqMan)
        hairpin_penalty: Penalty from hairpin analysis
        dimer_penalty: Penalty from dimer analysis
        
    Returns:
        Estimated efficiency (0-110%)
    """
    base = 100.0
    
    # Amplicon length factor
    # Optimal around 100bp, efficiency drops for longer amplicons
    if amplicon_length <= 100:
        length_factor = 0.0
    elif amplicon_length <= 150:
        length_factor = (amplicon_length - 100) * 0.1
    else:
        length_factor = 5.0 + (amplicon_length - 150) * 0.05
    
    # Primer Tm balance
    # Best if within 1°C
    tm_factor = min(abs(primer_tm_diff) * 2, 10.0)
    
    # Probe Tm (for TaqMan)
    # Should be 8-10°C higher than primers
    probe_factor = 0.0
    if probe_tm_diff > 0:
        if probe_tm_diff < 5:
            probe_factor = 5 - probe_tm_diff  # Too close
        elif probe_tm_diff > 12:
            probe_factor = probe_tm_diff - 12  # Too far
    
    # Calculate efficiency
    efficiency = base - length_factor - tm_factor - probe_factor - hairpin_penalty - dimer_penalty
    
    # Clamp to realistic range
    return max(70.0, min(110.0, efficiency))
