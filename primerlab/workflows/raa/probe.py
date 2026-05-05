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
        a = labels.get("abasic", "dR-Biotin")
        b = labels.get("blocker", "C3-spacer")
        # FPG probes are often shorter, but we use a similar internal site logic
        mid = len(seq) // 2
        left = seq[:mid]
        right = seq[mid+1:]
        return {
            "type": "fpg",
            "annotated_sequence": f"{left}[{f}-dT][{a}][{q}-dT]{right}[{b}]",
            "metadata": {"fluorophore": f, "quencher": q, "abasic": a}
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

def find_exo_probe(amplicon_seq: str, fwd_len: int, rev_len: int, config: Dict[str, Any], fwd_start: int = 0) -> Optional[Primer]:
    """
    Finds the best internal oligo (probe) within an amplicon for Exo-RAA.
    """
    import primer3
    p_cfg = config.get("parameters", {}).get("probe", {})
    p_len_min = p_cfg.get("min_size", 46)
    p_len_max = p_cfg.get("max_size", 52)
    p_tm_min = p_cfg.get("min_tm", 57.0)
    p_tm_max = p_cfg.get("max_tm", 80.0)
    
    # RAA specific: probe must be between primers with some gap
    # inner_seq = amplicon_seq[fwd_len + 1 : -rev_len - 1]
    # We use a bit more flexible search
    amp_len = len(amplicon_seq)
    
    candidates = []
    
    # Sliding window for probe selection
    for p_len in range(p_len_min, p_len_max + 1):
        for i in range(fwd_len + 1, amp_len - rev_len - p_len):
            p_seq = amplicon_seq[i : i + p_len]
            
            # Simple GC and Tm filter
            tm = primer3.calc_tm(p_seq)
            gc = sum(1 for b in p_seq if b in "GC") / p_len * 100
            
            if p_tm_min <= tm <= p_tm_max:
                # Basic Score: Higher Tm is better for RAA probes
                score = tm
                candidates.append({
                    "sequence": p_seq,
                    "tm": tm,
                    "gc": gc,
                    "score": score,
                    "local_start": i
                })
                
    if not candidates:
        return None
        
    # Sort by score descending
    candidates.sort(key=lambda x: x["score"], reverse=True)
    best = candidates[0]
    
    # Run full thermo QC for the best candidate (v1.2.0)
    hairpin = primer3.calc_hairpin(best["sequence"]).dg / 1000.0 # cal to kcal
    homodimer = primer3.calc_homodimer(best["sequence"]).dg / 1000.0

    # Calculate end stability (Delta G of last 5 bases)
    end_seq = best["sequence"][-5:]
    comp_end = "".join({"A":"T", "T":"A", "C":"G", "G":"C", "N":"N"}.get(b, b) for b in reversed(end_seq))
    end_stability = primer3.calc_heterodimer(end_seq, comp_end).dg / 1000.0

    # Calculate worst-case heterodimer against FWD and REV
    fwd_seq = amplicon_seq[:fwd_len]
    rev_seq = "".join({"A":"T", "T":"A", "C":"G", "G":"C", "N":"N"}.get(b, b) for b in reversed(amplicon_seq[-rev_len:]))
    het_fwd = primer3.calc_heterodimer(best["sequence"], fwd_seq).dg / 1000.0
    het_rev = primer3.calc_heterodimer(best["sequence"], rev_seq).dg / 1000.0
    heterodimer = min(het_fwd, het_rev) # Most negative Delta G is the most stable
    
    probe = Primer(
        id="manual_probe",
        sequence=best["sequence"],
        tm=best["tm"],
        gc=best["gc"],
        length=len(best["sequence"]),
        start=fwd_start + best["local_start"],
        end=fwd_start + best["local_start"] + len(best["sequence"]) - 1,
        hairpin_dg=hairpin,
        homodimer_dg=homodimer,
        heterodimer_dg=heterodimer,
        end_stability_dg=end_stability
    )
    
    return probe

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
    Refined to prevent overwriting and show true relative positions.
    """
    amp_len = len(amplicon_seq)
    map_list = ["-"] * amp_len
    
    f_len = len(fwd.sequence)
    r_len = len(rev.sequence)
    
    # 1. Mark FWD (always at start in our extracted amp_seq)
    for i in range(min(f_len, amp_len)):
        map_list[i] = ">"
        
    # 2. Mark REV (always at end in our extracted amp_seq)
    # We use rev_len and go from the back
    for i in range(amp_len - r_len, amp_len):
        if i >= 0:
            map_list[i] = "<"
            
    # 3. Mark Probe (Overlay with priority)
    if probe:
        p_seq = probe.sequence
        # Handle case where probe sequence might have labels in its object but we need raw
        p_idx = amplicon_seq.find(p_seq)
        if p_idx != -1:
            p_len = len(p_seq)
            for i in range(p_idx, min(p_idx + p_len, amp_len)):
                # If it hits a primer, it's an overlap! We mark it with 'X'
                if map_list[i] in [">", "<"]:
                    map_list[i] = "X" 
                else:
                    map_list[i] = "="
                
    return "".join(map_list)
