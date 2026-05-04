"""
RAA Exo-Probe design logic module.
Handles post-processing of Primer3 internal oligos to annotate THF abasic sites.
"""

from typing import Dict, Any, Optional, List
from primerlab.core.models import Primer
from primerlab.core.logger import get_logger
from primerlab.core.tools.thermocalc_wrapper import ThermocalcWrapper

logger = get_logger()

def annotate_probe(probe_primer: Primer, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Annotates a probe based on the type specified in the config.
    Supports: exo, taqman, fpg.
    """
    probe_cfg = config.get("parameters", {}).get("probe", {})
    p_type = probe_cfg.get("type", "exo")
    labels = probe_cfg.get("labels", {})
    seq = probe_primer.sequence
    
    if p_type == "taqman":
        f = labels.get("fluorophore", "FAM")
        q = labels.get("quencher", "BHQ1")
        return {
            "type": "taqman",
            "annotated_sequence": f"[{f}]{seq}[{q}]",
            "metadata": {"fluorophore": f, "quencher": q}
        }
    
    elif p_type == "fpg":
        f = labels.get("fluorophore", "FAM")
        q = labels.get("quencher", "BHQ1")
        return {
            "type": "fpg",
            "annotated_sequence": f"[{f}]{seq}[{q}]",
            "metadata": {"fluorophore": f, "quencher": q}
        }

    # Default: 'exo'
    thf_up = probe_cfg.get("thf_upstream_min", 30)
    thf_down = probe_cfg.get("thf_downstream_min", 15)
    f = labels.get("fluorophore", "FAM")
    q = labels.get("quencher", "BHQ1")
    b = labels.get("blocker", "C3-spacer")
    a = labels.get("abasic", "THF")

    seq_len = len(seq)
    min_req = thf_up + 1 + thf_down
    if seq_len < min_req:
        return {"valid": False, "reason": "too_short", "annotated_sequence": seq}

    target_idx = thf_up
    search_window = seq[target_idx - 2 : target_idx + 3]
    if 'T' in search_window:
        offset = search_window.find('T') - 2
        thf_index = target_idx + offset
    else:
        thf_index = target_idx

    # Boundary check
    if (seq_len - thf_index - 1) < thf_down:
        thf_index = seq_len - thf_down - 1

    left = seq[:thf_index]
    right = seq[thf_index+1:]
    annotated = f"{left}[{f}-dT][{a}][{q}-dT]{right}[{b}]"
    
    return {
        "type": "exo",
        "thf_index": thf_index,
        "annotated_sequence": annotated,
        "metadata": {"fluorophore": f, "quencher": q, "abasic": a, "blocker": b}
    }

def find_exo_probe(amplicon_seq: str, fwd_len: int, rev_len: int, config: Dict[str, Any]) -> Optional[Primer]:
    """
    Manually scans the amplicon for a suitable Exo-probe.
    Used when Primer3's internal oligo engine hits size limits (>36nt).
    """
    probe_cfg = config.get("parameters", {}).get("probe", {})
    min_size = probe_cfg.get("size", {}).get("min", 46)
    max_size = probe_cfg.get("size", {}).get("max", 52)
    
    # Amplicon sequence is FWD ... (Target) ... REV_RC
    # We want probe between FWD and REV
    inner_seq = amplicon_seq[fwd_len : -rev_len]
    inner_len = len(inner_seq)
    
    if inner_len < min_size:
        return None
        
    # Pick a candidate window.
    # Try multiple sizes from max to min
    
    # Get buffer conditions for accurate Tm calculation
    thermo_cfg = config.get("parameters", {}).get("thermodynamics", {})
    ta = ThermocalcWrapper(
        mv_conc=thermo_cfg.get("salt_monovalent", 50.0),
        dv_conc=thermo_cfg.get("salt_divalent", 1.5),
        dntp_conc=thermo_cfg.get("dntp_conc", 0.6),
        dna_conc=thermo_cfg.get("dna_conc", 50.0),
        tm_method=thermo_cfg.get("tm_method", 'santalucia'),
        salt_corrections=thermo_cfg.get("salt_corrections", 'santalucia')
    )
    
    for size in range(max_size, min_size - 1, -1):
        if inner_len >= size:
            # Simple centering logic
            start_off = (inner_len - size) // 2
            probe_seq = inner_seq[start_off : start_off + size]
            
            # Calculate Tm
            tm = ta.calc_tm(probe_seq)
            
            # Check if Tm is acceptable (RAA 39C needs stable probes)
            tm_min = probe_cfg.get("tm", {}).get("min", 54.0)
            if tm >= tm_min:
                logger.debug(f"Found manual probe: {probe_seq[:10]}... Tm: {tm:.1f}")
                return Primer(
                    id="manual_probe",
                    sequence=probe_seq,
                    tm=tm,
                    gc=(probe_seq.count('G') + probe_seq.count('C')) / len(probe_seq) * 100,
                    length=size
                )
    
    logger.debug(f"No suitable probe found in {inner_len}bp inner region (min_size={min_size}, min_tm={probe_cfg.get('tm', {}).get('min', 54.0)})")
    return None

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
            
            # Apply Probe annotations
            candidate["probe_annotation"] = annotate_probe(probe, config)
        
        if "forward" in candidate and "reverse" in candidate:
            all_candidates.append(candidate)
                
    return all_candidates

def create_amplicon_map(amplicon_seq: str, fwd: Primer, rev: Primer, probe: Optional[Primer] = None) -> str:
    """
    Creates a visual text map of the amplicon.
    Example: (FWD)>>>-------------------(PRB)====-------------------<<<(REV)
    """
    f_len = len(fwd.sequence)
    r_len = len(rev.sequence)
    amp_len = len(amplicon_seq)
    
    # Fill with dashes
    map_list = ["-"] * amp_len
    
    # Mark FWD
    for i in range(min(f_len, amp_len)):
        map_list[i] = ">"
        
    # Mark REV (Reverse orientation)
    for i in range(max(0, amp_len - r_len), amp_len):
        map_list[i] = "<"
        
    # Mark Probe
    if probe:
        # Find probe position in amplicon
        p_seq = probe.sequence
        p_idx = amplicon_seq.find(p_seq)
        if p_idx != -1:
            for i in range(p_idx, min(p_idx + len(p_seq), amp_len)):
                map_list[i] = "="
                
    return "".join(map_list)
