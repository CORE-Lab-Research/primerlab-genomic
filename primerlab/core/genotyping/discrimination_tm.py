"""
Discrimination Tm Calculator (v0.6.0).

Calculates Tm difference between matched and mismatched primers
to assess allele-specific discrimination potential.
"""

from typing import Tuple, Dict, Optional


# Nearest-neighbor parameters (kcal/mol) for DNA/DNA
# Simplified from SantaLucia 1998
NN_PARAMS = {
    "AA": -1.0, "TT": -1.0,
    "AT": -0.88, "TA": -0.58,
    "CA": -1.45, "TG": -1.45,
    "GT": -1.44, "AC": -1.44,
    "CT": -1.28, "AG": -1.28,
    "GA": -1.30, "TC": -1.30,
    "CG": -2.17, "GC": -2.24,
    "GG": -1.84, "CC": -1.84,
}

# Mismatch destabilization (kcal/mol) - approximate
# Higher value = more destabilizing = better discrimination
MISMATCH_PENALTY = {
    # Transitions
    ("A", "G"): 0.5,
    ("G", "A"): 0.5,
    ("C", "T"): 0.4,
    ("T", "C"): 0.4,
    # Transversions (more destabilizing)
    ("A", "C"): 1.2,
    ("C", "A"): 1.2,
    ("A", "T"): 1.5,
    ("T", "A"): 1.5,
    ("G", "C"): 0.8,
    ("C", "G"): 0.8,
    ("G", "T"): 1.0,
    ("T", "G"): 1.0,
}


def _calculate_basic_tm(sequence: str, na_concentration: float = 50.0) -> float:
    """
    Calculate Tm using simplified nearest-neighbor method.
    
    Args:
        sequence: Primer sequence
        na_concentration: Na+ concentration in mM
        
    Returns:
        Tm in degrees Celsius
    """
    sequence = sequence.upper()
    
    if len(sequence) < 2:
        return 0.0
    
    # Sum NN parameters
    delta_h = 0.0
    delta_s = 0.0
    
    # Approximate enthalpy/entropy
    for i in range(len(sequence) - 1):
        dinuc = sequence[i:i+2]
        if dinuc in NN_PARAMS:
            delta_h += NN_PARAMS[dinuc] * 8  # Rough conversion to kcal/mol
            delta_s += NN_PARAMS[dinuc] * 22  # Rough conversion to cal/mol·K
    
    # Initiation
    delta_h += -0.2
    delta_s += -5.7
    
    # Salt correction
    salt_corr = 16.6 * (0.434 * (na_concentration / 1000) ** 0.5)
    
    # Calculate Tm
    if delta_s == 0:
        return 0.0
    
    tm = (delta_h * 1000) / (delta_s + 1.987 * 2.303 * (-4.26)) + salt_corr
    
    # Fallback to simple formula if result unreasonable
    gc_count = sequence.count("G") + sequence.count("C")
    at_count = sequence.count("A") + sequence.count("T")
    
    if tm < 30 or tm > 100:
        # Use Wallace rule as fallback
        tm = 2 * at_count + 4 * gc_count
    
    return tm


def calculate_discrimination_tm(
    primer_sequence: str,
    snp_position: int,
    ref_allele: str,
    alt_allele: str,
    na_concentration: float = 50.0,
) -> Tuple[float, float, float]:
    """
    Calculate Tm difference between matched and mismatched primers.
    
    Args:
        primer_sequence: Primer sequence with ref allele at SNP position
        snp_position: Position of SNP from 5' end (0-indexed)
        ref_allele: Reference allele (matched)
        alt_allele: Alternative allele (mismatched)
        na_concentration: Na+ concentration in mM
        
    Returns:
        Tuple of (Tm_matched, Tm_mismatched, delta_Tm)
    """
    primer_sequence = primer_sequence.upper()
    ref_allele = ref_allele.upper()
    alt_allele = alt_allele.upper()
    
    # Calculate Tm for matched primer
    tm_matched = _calculate_basic_tm(primer_sequence, na_concentration)
    
    # Create mismatched primer
    primer_list = list(primer_sequence)
    if 0 <= snp_position < len(primer_list):
        primer_list[snp_position] = alt_allele
    mismatched_primer = "".join(primer_list)
    
    # Calculate base Tm for mismatched
    tm_mismatched_base = _calculate_basic_tm(mismatched_primer, na_concentration)
    
    # Apply mismatch penalty based on position and type
    penalty = MISMATCH_PENALTY.get((ref_allele, alt_allele), 0.7)
    
    # Position effect: 3' mismatches are more destabilizing
    distance_from_3prime = len(primer_sequence) - 1 - snp_position
    if distance_from_3prime == 0:
        position_factor = 3.0  # 3' terminal - max effect
    elif distance_from_3prime == 1:
        position_factor = 2.0
    elif distance_from_3prime == 2:
        position_factor = 1.5
    else:
        position_factor = 1.0
    
    tm_reduction = penalty * position_factor * 2  # Convert to °C
    tm_mismatched = tm_mismatched_base - tm_reduction
    
    delta_tm = tm_matched - tm_mismatched
    
    return (round(tm_matched, 1), round(tm_mismatched, 1), round(delta_tm, 1))


def estimate_allele_specificity(
    delta_tm: float,
    annealing_temp: Optional[float] = None,
) -> Dict:
    """
    Estimate allele-specific PCR discrimination based on Tm difference.
    
    Args:
        delta_tm: Tm difference between matched and mismatched primers
        annealing_temp: Optional annealing temperature for context
        
    Returns:
        Dict with specificity assessment
    """
    # Classification
    if delta_tm >= 8.0:
        specificity = "Excellent"
        score = 100
    elif delta_tm >= 5.0:
        specificity = "Good"
        score = 85
    elif delta_tm >= 3.0:
        specificity = "Moderate"
        score = 70
    elif delta_tm >= 1.5:
        specificity = "Marginal"
        score = 55
    else:
        specificity = "Poor"
        score = 40
    
    recommendations = []
    
    if delta_tm < 3.0:
        recommendations.append("Consider using LNA or other modified bases for better discrimination")
    if delta_tm < 5.0:
        recommendations.append("Optimize annealing temperature near mismatched Tm")
    
    # Calculate optimal annealing if not provided
    if annealing_temp is None:
        # Suggest annealing between matched and mismatched Tm
        optimal_annealing = None
    else:
        optimal_annealing = annealing_temp
    
    return {
        "delta_tm": delta_tm,
        "specificity": specificity,
        "score": score,
        "recommendations": recommendations,
        "optimal_annealing": optimal_annealing,
    }
