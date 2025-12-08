"""
Sequence QC Utilities for v0.1.3

This module provides additional QC checks for primer sequences:
- GC Clamp: Ensures 3' end stability
- Poly-X Detection: Detects runs of consecutive identical bases
"""

import re
from typing import Dict, Any, List, Tuple
from primerlab.core.logger import get_logger

logger = get_logger()


def check_gc_clamp(sequence: str, window: int = 5, min_gc: int = 1, max_gc: int = 5) -> Tuple[bool, str, str]:
    """
    Check GC clamp at the 3' end of a primer.
    
    A GC clamp refers to having G or C bases at the 3' end which helps
    with primer annealing specificity. Optimal is 1-3 G/C in last 5 bases.
    
    Args:
        sequence: Primer sequence (5' to 3')
        window: Number of bases to check from 3' end (default: 5)
        min_gc: Minimum G/C count for good clamp (default: 1)
        max_gc: Maximum G/C count to avoid over-stability (default: 5)
    
    Returns:
        Tuple of (passes_check, message, explanation)
    """
    if len(sequence) < window:
        window = len(sequence)
    
    three_prime = sequence[-window:].upper()
    gc_count = three_prime.count('G') + three_prime.count('C')
    
    if gc_count < min_gc:
        msg = f"Weak 3' GC clamp ({gc_count} G/C in last {window} bases)"
        explanation = ("Too few G/C at 3'-end may cause poor annealing and extension. "
                      "G-C bonds are stronger than A-T bonds. Consider redesigning primer.")
        return False, msg, explanation
    elif gc_count > 3:  # Warning threshold (but not failure)
        msg = f"Strong 3' GC clamp ({gc_count} G/C in last {window} bases)"
        explanation = ("High G/C content at 3'-end may increase non-specific binding. "
                      "Optimal is 1-3 G/C in last 5 bases, but primer may still work well.")
        # Return True (PASS) with warning - strong is acceptable, just not optimal
        return True, msg, explanation
    else:
        msg = f"Good 3' GC clamp ({gc_count} G/C in last {window} bases)"
        explanation = "Optimal G/C content at 3'-end for stable annealing."
        return True, msg, explanation


def check_poly_x(sequence: str, max_run: int = 4) -> Tuple[bool, str]:
    """
    Check for poly-nucleotide runs (e.g., AAAA, GGGG).
    
    Long runs of identical bases can cause mispriming and
    reduce amplification efficiency.
    
    Args:
        sequence: Primer sequence
        max_run: Maximum allowed consecutive identical bases (default: 4)
    
    Returns:
        Tuple of (passes_check, message)
    """
    sequence = sequence.upper()
    
    # Find all runs of identical bases
    pattern = r'(.)\1+'
    matches = re.finditer(pattern, sequence)
    
    longest_run = 0
    longest_base = ""
    
    for match in matches:
        run_length = len(match.group())
        if run_length > longest_run:
            longest_run = run_length
            longest_base = match.group()[0]
    
    if longest_run > max_run:
        return False, f"Poly-{longest_base} run detected ({longest_run} consecutive, max: {max_run})"
    elif longest_run > 0:
        return True, f"Max poly-run: {longest_run} ({longest_base})"
    else:
        return True, "No poly-nucleotide runs detected"


def check_3prime_stability(sequence: str) -> Tuple[bool, str]:
    """
    Check last base at 3' end.
    
    G or C at 3' end is preferred for better annealing.
    A or T at 3' is acceptable but suboptimal.
    
    Returns:
        Tuple of (passes_check, message)
    """
    last_base = sequence[-1].upper()
    
    if last_base in ['G', 'C']:
        return True, f"3'-end {last_base} (optimal)"
    else:
        return True, f"3'-end {last_base} (acceptable, G/C preferred)"


def run_sequence_qc(sequence: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Run all sequence QC checks on a primer.
    
    Args:
        sequence: Primer sequence
        config: Optional QC configuration
        
    Returns:
        Dict with check results and overall status
    """
    config = config or {}
    
    results = {
        "sequence": sequence,
        "length": len(sequence),
        "checks": {},
        "passes_all": True,
        "warnings": [],
        "errors": []
    }
    
    # GC Clamp check - now returns (passed, message, explanation)
    gc_window = config.get("gc_clamp_window", 5)
    gc_min = config.get("gc_clamp_min", 1)
    gc_max = config.get("gc_clamp_max", 5)
    
    gc_ok, gc_msg, gc_explain = check_gc_clamp(sequence, gc_window, gc_min, gc_max)
    results["checks"]["gc_clamp"] = {"passed": gc_ok, "message": gc_msg, "explanation": gc_explain}
    if not gc_ok:
        results["warnings"].append(f"{gc_msg} - {gc_explain}")
    elif "Strong" in gc_msg:
        results["warnings"].append(f"{gc_msg} - {gc_explain}")
    
    # Poly-X check
    max_run = config.get("poly_x_max", 4)
    poly_ok, poly_msg = check_poly_x(sequence, max_run)
    results["checks"]["poly_x"] = {"passed": poly_ok, "message": poly_msg}
    if not poly_ok:
        results["warnings"].append(poly_msg)
    
    # 3' stability check
    stability_ok, stability_msg = check_3prime_stability(sequence)
    results["checks"]["3prime_stability"] = {"passed": stability_ok, "message": stability_msg}
    
    # Overall status - only fail on actual failures, not warnings
    results["passes_all"] = gc_ok and poly_ok and stability_ok
    
    return results
