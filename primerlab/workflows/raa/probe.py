"""
RAA Exo-Probe design logic module.
Handles post-processing of Primer3 internal oligos to annotate THF abasic sites.
"""

from typing import Dict, Any, Optional
from primerlab.core.models import Primer
from primerlab.core.logger import get_logger

logger = get_logger()

def annotate_exo_probe(probe_primer: Primer, thf_upstream_min: int = 30, thf_downstream_min: int = 15) -> Dict[str, Any]:
    """
    Annotates an Exo-probe with THF, Fluorophore, and Quencher positions.
    
    Exo-probe requirements:
    - ~30nt upstream of THF
    - ~15nt downstream of THF
    - THF replaces a natural base (often 'T' or a purine depending on chemistry, here we just pick a valid index)
    
    Args:
        probe_primer: The Primer object representing the raw probe sequence
        thf_upstream_min: Minimum bases required 5' of the THF site
        thf_downstream_min: Minimum bases required 3' of the THF site
        
    Returns:
        Dict containing annotation metadata.
    """
    seq = probe_primer.sequence
    seq_len = len(seq)
    
    # Check if probe is long enough
    min_required = thf_upstream_min + 1 + thf_downstream_min
    if seq_len < min_required:
        logger.warning(f"Probe length ({seq_len}) is too short for Exo-probe constraints (min {min_required})")
        return {
            "valid_exo": False,
            "reason": "too_short",
            "thf_index": None,
            "annotated_sequence": seq
        }
        
    # Find optimal THF site. Usually we want it exactly at `thf_upstream_min` index.
    # In practice, scientists often look for a 'T' near this region to replace with THF.
    # We will search within a 5nt window around the target index for a 'T'.
    
    target_idx = thf_upstream_min
    search_window = seq[target_idx - 2 : target_idx + 3]
    
    if 'T' in search_window:
        offset = search_window.find('T') - 2
        thf_index = target_idx + offset
    else:
        # Fallback to exact index if no T found
        thf_index = target_idx
        
    # Ensure the found index still respects the downstream minimum
    if (seq_len - thf_index - 1) < thf_downstream_min:
        # Push it back if needed
        thf_index = seq_len - thf_downstream_min - 1
        
    # Create annotated sequence (e.g., [FAM]-ATG...GCA[THF]GCT...AGC-[C3])
    annotated = f"[FAM]-{seq[:thf_index]}[THF]{seq[thf_index+1:]}-[C3]"
    
    return {
        "valid_exo": True,
        "thf_index": thf_index,
        "replaced_base": seq[thf_index],
        "annotated_sequence": annotated,
        "fluorophore": "FAM",
        "quencher": "BHQ1 (internal, near THF)",
        "blocker": "C3-spacer"
    }

def parse_primer3_output(raw_results: Dict[str, Any], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parses Primer3 output and extracts multiple primer/probe triplets.
    Applies RAA-specific Probe annotations to each candidate.
    
    Returns:
        List of dicts, each containing 'forward', 'reverse', and optionally 'probe'.
    """
    all_candidates = []
    
    num_returned = raw_results.get('PRIMER_LEFT_NUM_RETURNED', 0)
    
    for i in range(num_returned):
        candidate = {}
        
        # Forward Primer
        fwd_key = f'PRIMER_LEFT_{i}'
        if fwd_key in raw_results:
            fwd_start, fwd_len = raw_results.get(fwd_key)
            candidate["forward"] = Primer(
                id=f"forward_{i}",
                sequence=raw_results.get(f'PRIMER_LEFT_{i}_SEQUENCE'),
                tm=raw_results.get(f'PRIMER_LEFT_{i}_TM'),
                gc=raw_results.get(f'PRIMER_LEFT_{i}_GC_PERCENT'),
                length=fwd_len,
                start=fwd_start,
                end=fwd_start + fwd_len - 1,
                hairpin_dg=raw_results.get(f'PRIMER_LEFT_{i}_HAIRPIN_TH', 0.0),
                homodimer_dg=raw_results.get(f'PRIMER_LEFT_{i}_HOMODIMER_TH', 0.0)
            )
            
        # Reverse Primer
        rev_key = f'PRIMER_RIGHT_{i}'
        if rev_key in raw_results:
            rev_start, rev_len = raw_results.get(rev_key)
            candidate["reverse"] = Primer(
                id=f"reverse_{i}",
                sequence=raw_results.get(f'PRIMER_RIGHT_{i}_SEQUENCE'),
                tm=raw_results.get(f'PRIMER_RIGHT_{i}_TM'),
                gc=raw_results.get(f'PRIMER_RIGHT_{i}_GC_PERCENT'),
                length=rev_len,
                start=rev_start - rev_len + 1,
                end=rev_start,
                hairpin_dg=raw_results.get(f'PRIMER_RIGHT_{i}_HAIRPIN_TH', 0.0),
                homodimer_dg=raw_results.get(f'PRIMER_RIGHT_{i}_HOMODIMER_TH', 0.0)
            )
            
        # Probe (if enabled)
        probe_seq_key = f'PRIMER_INTERNAL_{i}_SEQUENCE'
        probe_seq = raw_results.get(probe_seq_key)
        if probe_seq:
            probe_key = f'PRIMER_INTERNAL_{i}'
            probe_start, probe_len = raw_results.get(probe_key)
            probe = Primer(
                id=f"probe_{i}",
                sequence=probe_seq,
                tm=raw_results.get(f'PRIMER_INTERNAL_{i}_TM'),
                gc=raw_results.get(f'PRIMER_INTERNAL_{i}_GC_PERCENT'),
                length=probe_len,
                start=probe_start,
                end=probe_start + probe_len - 1,
                hairpin_dg=raw_results.get(f'PRIMER_INTERNAL_{i}_HAIRPIN_TH', 0.0),
                homodimer_dg=raw_results.get(f'PRIMER_INTERNAL_{i}_HOMODIMER_TH', 0.0)
            )
            candidate["probe"] = probe
            
            # Apply Exo-probe annotations
            probe_cfg = config.get("parameters", {}).get("probe", {})
            if probe_cfg.get("type") == "exo":
                candidate["probe_annotation"] = annotate_exo_probe(
                    probe,
                    thf_upstream_min=probe_cfg.get("thf_upstream_min", 30),
                    thf_downstream_min=probe_cfg.get("thf_downstream_min", 15)
                )
        
        if "forward" in candidate and "reverse" in candidate:
            all_candidates.append(candidate)
                
    return all_candidates
