"""
GC Clamp Analysis for Amplicons.

Analyzes G/C content at amplicon ends for PCR efficiency.
"""

from typing import Optional
from .models import GCClamp


def analyze_gc_clamp(
    sequence: str,
    region_size: int = 5,
    min_gc: int = 1,
    max_gc: int = 3
) -> GCClamp:
    """
    Analyze GC clamp at amplicon ends.
    
    A GC clamp (G or C at 3' end) helps primer binding and extension.
    Too many G/C can cause non-specific binding; too few can be weak.
    
    Args:
        sequence: DNA sequence (amplicon)
        region_size: Number of nucleotides to check at each end
        min_gc: Minimum G/C count for optimal
        max_gc: Maximum G/C count for optimal
        
    Returns:
        GCClamp result with counts and assessment
    """
    seq = sequence.upper()
    
    # 5' end (first N nucleotides)
    five_prime = seq[:region_size]
    five_prime_count = five_prime.count("G") + five_prime.count("C")
    
    # 3' end (last N nucleotides)
    three_prime = seq[-region_size:] if len(seq) >= region_size else seq
    three_prime_count = three_prime.count("G") + three_prime.count("C")
    
    # Assess optimality
    warning = None
    is_optimal = True
    
    # Check 3' end (more critical for PCR)
    if three_prime_count < min_gc:
        warning = f"Weak 3' end: only {three_prime_count} G/C in last {region_size}nt"
        is_optimal = False
    elif three_prime_count > max_gc:
        warning = f"Strong 3' end: {three_prime_count} G/C in last {region_size}nt (may cause non-specific binding)"
        is_optimal = False
    
    # Check 5' end
    if five_prime_count < min_gc and is_optimal:
        warning = f"Weak 5' end: only {five_prime_count} G/C in first {region_size}nt"
        # 5' is less critical, so don't mark as non-optimal
    elif five_prime_count > max_gc and is_optimal:
        warning = f"Strong 5' end: {five_prime_count} G/C in first {region_size}nt"
    
    return GCClamp(
        five_prime_count=five_prime_count,
        three_prime_count=three_prime_count,
        region_size=region_size,
        is_optimal=is_optimal,
        warning=warning
    )
