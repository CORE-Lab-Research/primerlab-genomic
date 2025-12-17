"""
Binding Site Analysis Module (v0.2.0)

Advanced binding site analysis including:
- 3' end stability (ΔG)
- Mismatch tolerance
- Binding Tm calculation
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple

from primerlab.core.logger import get_logger

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
        
        # Check for match
        if p1 == t1 and p2 == t2:
            dinuc = p1 + p2
            total_dg += nn_dg.get(dinuc, -1.0)
        else:
            # Mismatch penalty
            total_dg += 1.0  # Destabilizing
            mismatches += 1
    
    # Salt correction (simplified)
    salt_factor = 1 + 0.02 * (na_conc / 50.0 - 1)
    total_dg *= salt_factor
    
    return round(total_dg, 2)


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
    
    # Count matches/mismatches
    match_count = sum(1 for p, t in zip(primer, target) if p == t)
    mismatch_count = len(primer) - match_count
    match_percent = (match_count / len(primer)) * 100
    
    # Analyze 3' end (last 5bp of primer)
    three_prime_len = min(5, len(primer))
    primer_3p = primer[-three_prime_len:]
    target_3p = target[-three_prime_len:]
    
    three_prime_match = 0
    for p, t in zip(reversed(primer), reversed(target)):
        if p == t:
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
        if p != t
    )
    
    # Calculate overall binding Tm (simplified)
    # Real implementation would use ViennaRNA
    gc_count = sum(1 for b in primer if b in 'GC')
    gc_percent = (gc_count / len(primer)) * 100
    binding_tm = 64.9 + 41 * (gc_count - 16.4) / len(primer)  # Simplified
    
    # Adjust for mismatches (roughly -5°C per mismatch)
    binding_tm -= mismatch_count * 5
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
    
    if is_valid:
        validation_notes.append("All requirements met")
    
    # Create alignment string
    alignment_str = ''.join('|' if p == t else 'x' for p, t in zip(primer, target))
    
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
        matches = sum(1 for p, t in zip(search_primer.upper(), target_region) if p == t)
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


def reverse_complement(seq: str) -> str:
    """Return reverse complement of DNA sequence."""
    complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 
                  'a': 't', 't': 'a', 'g': 'c', 'c': 'g',
                  'N': 'N', 'n': 'n'}
    return ''.join(complement.get(base, 'N') for base in reversed(seq))
