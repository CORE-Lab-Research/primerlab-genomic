"""
Binding Site Analysis Module (v0.2.0)

Advanced binding site analysis including:
- 3' end stability (ΔG)
- Mismatch tolerance
- Binding Tm calculation
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from primerlab.core.logger import get_logger
from primerlab.core.sequence import reverse_complement, bases_match

logger = get_logger()


@dataclass
class BindingSite:
    """
    Detailed binding site analysis.
    
    Extends basic binding info with thermodynamic analysis.
    """
    position: int                   # 0-indexed on template
    strand: str                     # '+' or '-'
    primer_seq: str                 # Original primer sequence
    target_seq: str                 # Target region on template
    
    # Match statistics
    match_count: int
    mismatch_count: int
    match_percent: float
    
    # 3' end analysis
    three_prime_match: int          # Perfect match bp at 3' end
    three_prime_dg: float           # ΔG at 3' end (kcal/mol)
    
    # 5' end analysis
    five_prime_mismatch: int        # Mismatches in 5' region
    
    # Thermodynamics
    binding_tm: float               # Tm at this binding site
    binding_dg: float               # Overall ΔG of binding
    
    # Validation
    is_valid: bool                  # Meets all requirements
    validation_notes: List[str]     # Why valid/invalid
    
    # Visualization
    alignment_str: str              # Visual alignment


def calculate_three_prime_dg(
    primer_3prime: str,
    target_3prime: str,
    na_conc: float = 50.0,
    mg_conc: float = 2.0
) -> float:
    """
    Calculate ΔG for the 3' end binding.
    
    Uses nearest-neighbor thermodynamics.
    
    Args:
        primer_3prime: 3' end of primer (5-8 bp)
        target_3prime: Corresponding target region
        na_conc: Na+ concentration (mM)
        mg_conc: Mg2+ concentration (mM)
        
    Returns:
        ΔG in kcal/mol (negative = stable)
    """
    # Simplified ΔG calculation using nearest-neighbor
    # Real implementation would use ViennaRNA or full NN tables
    
    # Base pair ΔG values (kcal/mol) - simplified
    nn_dg = {
        'AA': -1.0, 'TT': -1.0,
        'AT': -0.9, 'TA': -0.6,
        'CA': -1.3, 'TG': -1.3,
        'GT': -1.4, 'AC': -1.4,
        'CT': -1.5, 'AG': -1.5,
        'GA': -1.4, 'TC': -1.4,
        'CG': -2.1,
        'GC': -2.4,
        'GG': -1.5, 'CC': -1.5,
    }
    
    total_dg = 0.0
    mismatches = 0
    
    for i in range(len(primer_3prime) - 1):
        p1, p2 = primer_3prime[i:i+2].upper()
        t1, t2 = target_3prime[i:i+2].upper()
        
        # Check for match (IUPAC aware)
        if bases_match(p1, t1) and bases_match(p2, t2):
            dinuc = p1 + p2
            total_dg += nn_dg.get(dinuc, -1.0)
        else:
            # Mismatch penalty (IUPAC aware)
            # Penalize more if it's a true mismatch even after IUPAC resolution
            if not bases_match(p1, t1) or not bases_match(p2, t2):
                total_dg += 1.5  # Higher penalty for true mismatch
            else:
                total_dg += 0.5  # Slight penalty for degeneracy
            mismatches += 1
    
    # Salt correction (simplified)
    salt_factor = 1 + 0.02 * (na_conc / 50.0 - 1)
    total_dg *= salt_factor
    
    return round(total_dg, 2)


# v0.3.4: Tm Correction for Mismatches
def calculate_corrected_tm(
    primer_seq: str,
    target_seq: str,
    base_tm: float,
    mismatches: int,
    correction_per_mismatch: float = 1.0
) -> float:
    """
    Correct Tm based on number of mismatches.
    
    Rule: ~1°C reduction per mismatch (adjustable).
    
    Args:
        primer_seq: Original primer sequence
        target_seq: Target sequence on template
        base_tm: Original Tm (calculated for perfect match)
        mismatches: Number of mismatches detected
        correction_per_mismatch: Degrees to subtract per mismatch (default 1.0)
        
    Returns:
        Corrected Tm in °C (floor at 30°C)
    """
    correction = mismatches * correction_per_mismatch
    corrected_tm = base_tm - correction
    
    # Ensure Tm doesn't go below 30°C (unrealistic)
    return max(round(corrected_tm, 1), 30.0)


# v0.3.4: 3' Stability Warning
def check_three_prime_stability(
    three_prime_dg: float,
    threshold_strong: float = -9.0,
    threshold_weak: float = -3.0
) -> tuple:
    """
    Check if 3' end is too stable or too weak.
    
    A very stable 3' end (very negative ΔG) may reduce specificity.
    A weak 3' end may lead to poor amplification.
    
    Args:
        three_prime_dg: ΔG of 3' pentamer in kcal/mol
        threshold_strong: ΔG below this = too stable (default -9.0)
        threshold_weak: ΔG above this = too weak (default -3.0)
        
    Returns:
        Tuple of (status, warning_message)
        status: "ok", "strong", "weak"
    """
    if three_prime_dg < threshold_strong:
        return (
            "strong",
            f"3' end may be too stable (ΔG={three_prime_dg:.1f} kcal/mol). "
            "Consider redesign for better specificity."
        )
    elif three_prime_dg > threshold_weak:
        return (
            "weak", 
            f"3' end may be too weak (ΔG={three_prime_dg:.1f} kcal/mol). "
            "May result in poor amplification."
        )
    else:
        return ("ok", None)


# Note: check_gc_clamp already exists in primerlab.core.sequence_qc
# Use that for GC clamp checking to avoid duplication


def analyze_binding(
    primer_seq: str,
    target_seq: str,
    position: int,
    strand: str,
    params: Optional[Dict[str, Any]] = None
) -> BindingSite:
    """
    Perform detailed binding site analysis.
    
    Args:
        primer_seq: Primer sequence (5' to 3')
        target_seq: Target region on template
        position: Position on template
        strand: '+' or '-'
        params: Analysis parameters
        
    Returns:
        BindingSite with full analysis
    """
    params = params or {}
    
    # Ensure same length
    primer = primer_seq.upper()
    target = target_seq.upper()
    
    if len(primer) != len(target):
        raise ValueError(f"Primer ({len(primer)}bp) and target ({len(target)}bp) must be same length")
    
    # Count matches/mismatches (IUPAC aware)
    match_count = sum(1 for p, t in zip(primer, target) if bases_match(p, t))
    mismatch_count = len(primer) - match_count
    match_percent = (match_count / len(primer)) * 100
    
    # Analyze 3' end (last 5bp of primer)
    three_prime_len = min(5, len(primer))
    primer_3p = primer[-three_prime_len:]
    target_3p = target[-three_prime_len:]
    
    three_prime_match = 0
    for p, t in zip(reversed(primer), reversed(target)):
        if bases_match(p, t):
            three_prime_match += 1
        else:
            break
    
    # Calculate 3' ΔG
    three_prime_dg = calculate_three_prime_dg(
        primer_3p, target_3p,
        na_conc=params.get("na_conc", 50.0),
        mg_conc=params.get("mg_conc", 2.0)
    )
    
    # Analyze 5' end (first 5bp of primer)
    five_prime_len = min(5, len(primer))
    five_prime_mismatch = sum(
        1 for p, t in zip(primer[:five_prime_len], target[:five_prime_len])
        if not bases_match(p, t)
    )
    
    # Calculate overall binding Tm (simplified)
    # Real implementation would use ViennaRNA
    gc_count = sum(1 for b in primer if b in 'GC')
    gc_percent = (gc_count / len(primer)) * 100
    base_tm = 64.9 + 41 * (gc_count - 16.4) / len(primer)  # Simplified
    
    # v0.3.4: Use calculate_corrected_tm for mismatch correction
    # Calculate weighted mismatches (3' mismatches count more)
    weighted_mismatches = 0
    for i in range(len(primer)):
        if not bases_match(primer[i], target[i]):
            dist_from_3prime = len(primer) - 1 - i
            if dist_from_3prime < 5:
                weighted_mismatches += 2.0  # 3' mismatches count double
            else:
                weighted_mismatches += 1.0
    
    binding_tm = calculate_corrected_tm(
        primer, target, base_tm, 
        int(weighted_mismatches),
        correction_per_mismatch=params.get("tm_correction_per_mismatch", 2.5)
    )
    binding_tm = max(30, min(90, binding_tm))  # Clamp
    
    # Overall binding ΔG (simplified)
    binding_dg = -1.5 * match_count + 1.0 * mismatch_count
    
    # Validation
    validation_notes = []
    min_3p_match = params.get("min_3prime_match", 3)
    max_5p_mismatch = params.get("max_5prime_mismatch", 2)
    min_match_pct = params.get("min_total_match_percent", 80)
    max_3p_dg = params.get("three_prime_dg_max", -2.0)
    
    is_valid = True
    
    if three_prime_match < min_3p_match:
        is_valid = False
        validation_notes.append(f"3' match ({three_prime_match}bp) < required ({min_3p_match}bp)")
    
    if five_prime_mismatch > max_5p_mismatch:
        is_valid = False
        validation_notes.append(f"5' mismatches ({five_prime_mismatch}) > allowed ({max_5p_mismatch})")
    
    if match_percent < min_match_pct:
        is_valid = False
        validation_notes.append(f"Match ({match_percent:.1f}%) < required ({min_match_pct}%)")
    
    if three_prime_dg > max_3p_dg:
        is_valid = False
        validation_notes.append(f"3' ΔG ({three_prime_dg}) > max ({max_3p_dg})")
    
    # v0.3.4: Check 3' stability using new function
    stability_status, stability_warning = check_three_prime_stability(
        three_prime_dg,
        threshold_strong=params.get("three_prime_dg_strong", -9.0),
        threshold_weak=params.get("three_prime_dg_weak", -3.0)
    )
    if stability_warning:
        validation_notes.append(stability_warning)
    
    if is_valid:
        validation_notes.append("All requirements met")
    
    # Create alignment string
    alignment_str = ''.join('|' if bases_match(p, t) else 'x' for p, t in zip(primer, target))
    
    return BindingSite(
        position=position,
        strand=strand,
        primer_seq=primer_seq,
        target_seq=target_seq,
        match_count=match_count,
        mismatch_count=mismatch_count,
        match_percent=match_percent,
        three_prime_match=three_prime_match,
        three_prime_dg=three_prime_dg,
        five_prime_mismatch=five_prime_mismatch,
        binding_tm=round(binding_tm, 1),
        binding_dg=round(binding_dg, 2),
        is_valid=is_valid,
        validation_notes=validation_notes,
        alignment_str=alignment_str
    )


def find_all_binding_sites(
    primer_seq: str,
    template_seq: str,
    strand: str,
    params: Optional[Dict[str, Any]] = None
) -> List[BindingSite]:
    """
    Find all binding sites for a primer on a template.
    
    Args:
        primer_seq: Primer sequence
        template_seq: Template sequence
        strand: '+' or '-'
        params: Analysis parameters
        
    Returns:
        List of BindingSite objects, sorted by quality
    """
    params = params or {}
    sites = []
    primer_len = len(primer_seq)
    threshold = params.get("report_threshold", 70)
    
    # For reverse strand, search for reverse complement binding
    if strand == '-':
        search_primer = reverse_complement(primer_seq)
    else:
        search_primer = primer_seq
    
    template_upper = template_seq.upper()
    
    for i in range(len(template_upper) - primer_len + 1):
        target_region = template_upper[i:i + primer_len]
        
        # Quick check - count matches
        matches = sum(1 for p, t in zip(search_primer.upper(), target_region) if bases_match(p, t))
        match_pct = (matches / primer_len) * 100
        
        if match_pct >= threshold:
            site = analyze_binding(
                primer_seq=primer_seq,
                target_seq=target_region,
                position=i,
                strand=strand,
                params=params
            )
            sites.append(site)
    
    # Sort by quality (match%, 3' match, ΔG)
    sites.sort(key=lambda s: (-s.match_percent, -s.three_prime_match, s.three_prime_dg))
    
    return sites


def check_primer_dimer(
    forward_primer: str,
    reverse_primer: str,
    min_complementary: int = 4,
    check_3prime: bool = True
) -> Dict[str, Any]:
    """
    Check for primer-dimer formation between forward and reverse primers.
    
    v0.2.5: Detects complementarity that could lead to primer-dimer artifacts.
    
    Args:
        forward_primer: Forward primer sequence (5' to 3')
        reverse_primer: Reverse primer sequence (5' to 3')
        min_complementary: Minimum consecutive complementary bases to flag
        check_3prime: Give extra weight to 3' end complementarity
        
    Returns:
        Dictionary with dimer analysis:
        - has_dimer: bool
        - max_complementary: int
        - dimer_regions: list of tuples
        - severity: "none", "low", "medium", "high"
        - warning: str or None
    """
    fwd = forward_primer.upper()
    rev = reverse_primer.upper()
    rev_rc = reverse_complement(reverse_primer).upper()
    
    # Check Fwd 3' against Rev 5' (most problematic)
    # and Fwd against Rev reverse complement
    
    dimer_regions = []
    max_complementary = 0
    
    # Slide forward primer against reverse complement of reverse primer
    for offset in range(-len(fwd) + 1, len(rev_rc)):
        complementary = 0
        start_pos = None
        
        for i in range(len(fwd)):
            j = i + offset
            if 0 <= j < len(rev_rc):
                if bases_match(fwd[i], rev_rc[j]):
                    if start_pos is None:
                        start_pos = i
                    complementary += 1
                else:
                    if complementary >= min_complementary:
                        dimer_regions.append({
                            "fwd_start": start_pos,
                            "fwd_end": i,
                            "length": complementary,
                            "type": "internal"
                        })
                    max_complementary = max(max_complementary, complementary)
                    complementary = 0
                    start_pos = None
        
        # Check remaining
        if complementary >= min_complementary:
            dimer_regions.append({
                "fwd_start": start_pos,
                "fwd_end": start_pos + complementary,
                "length": complementary,
                "type": "internal"
            })
        max_complementary = max(max_complementary, complementary)
    
    # Check 3' end specifically (most critical for extension)
    three_prime_complementary = 0
    fwd_3prime = fwd[-6:]  # Last 6 bases
    rev_3prime = rev[-6:]
    rev_3prime_rc = reverse_complement(rev_3prime).upper()
    
    for i, (f, r) in enumerate(zip(fwd_3prime, rev_3prime_rc)):
        if bases_match(f, r):
            three_prime_complementary += 1
    
    # Determine severity
    has_dimer = max_complementary >= min_complementary
    severity = "none"
    warning = None
    
    if max_complementary >= 8 or three_prime_complementary >= 4:
        severity = "high"
        warning = f"High primer-dimer risk: {max_complementary} consecutive complementary bases"
    elif max_complementary >= 6 or three_prime_complementary >= 3:
        severity = "medium"
        warning = f"Moderate primer-dimer risk: {max_complementary} consecutive complementary bases"
    elif max_complementary >= 4:
        severity = "low"
        warning = f"Low primer-dimer risk: {max_complementary} consecutive complementary bases"
    
    return {
        "has_dimer": has_dimer,
        "max_complementary": max_complementary,
        "three_prime_complementary": three_prime_complementary,
        "dimer_regions": dimer_regions[:5],  # Top 5
        "severity": severity,
        "warning": warning
    }
