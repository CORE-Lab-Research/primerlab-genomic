"""
RAA Exo-Probe design logic module.
Handles post-processing of Primer3 internal oligos to annotate THF abasic sites.
"""

from typing import Dict, Any, Optional, List
from primerlab.core.models import Primer
from primerlab.core.logger import get_logger
from primerlab.core.tools.thermocalc_wrapper import ThermocalcWrapper

logger = get_logger()

# Maximum nucleotides permitted between a dT-label and the abasic residue.
# TwistAmp Assay Design Manual §3.1.2: "The number of nucleotides between the
# dT-fluorophore, or the dT-quencher, and the THF can be 0, 1 or 2". This also
# satisfies the "<=5 bases between fluorophore and quencher" rule, since the
# widest legal sandwich is 2 + THF + 2 = 5.
FQ_GAP_MAX = 2

# Default THF placement window, measured as the number of probe bases lying 5' of
# the abasic residue. The manual states ">=30 bases 5' of THF" as a hard rule and
# illustrates "30-38" as the working range (the probe must still function as a
# primer once cleaved), and ">=15 bases 3' of THF ... if the exonuclease is going
# to cut it efficiently".
THF_UPSTREAM_MIN = 30
THF_UPSTREAM_MAX = 38
THF_DOWNSTREAM_MIN = 15


def find_thf_site(seq: str,
                  up_min: int = THF_UPSTREAM_MIN,
                  up_max: int = THF_UPSTREAM_MAX,
                  down_min: int = THF_DOWNSTREAM_MIN,
                  max_label_mismatches: int = 0):
    """Locate the best [dT-F][abasic][dT-Q] sandwich in `seq`.

    Returns (fluor_idx, thf_idx, quencher_idx, label_mismatches) or None if no
    position satisfies the rules. All indices are 0-based into `seq`.

    The constraint that actually drives the search is that the fluorophore and
    quencher reagents exist only as dT couplings, so both flanking positions
    should already be a T in the target sequence. There is no sequence requirement
    on the base replaced by the abasic residue itself — placing the abasic residue
    on a T (as this function's predecessor did) wastes the one base that could
    have carried a label.

    `max_label_mismatches` permits a label to sit on a non-T base, which the
    TwistAmp manual sanctions as a fallback; sites needing fewer such mismatches
    always win. Ties break toward the closest fluorophore/quencher pair, since
    greater separation degrades quenching, and then toward the smallest upstream
    distance.
    """
    n = len(seq)
    seq = seq.upper()
    hi = min(up_max, n - down_min - 1)
    lo = max(up_min, 1)
    best = None
    for t in range(lo, hi + 1):
        for f in range(t - 1, t - 2 - FQ_GAP_MAX, -1):
            if f < 0:
                continue
            for q in range(t + 1, t + 2 + FQ_GAP_MAX):
                if q >= n:
                    continue
                mismatches = (seq[f] != 'T') + (seq[q] != 'T')
                if mismatches > max_label_mismatches:
                    continue
                cand = (mismatches, q - f, t, f, q)
                if best is None or cand < best:
                    best = cand
    if best is None:
        return None
    mismatches, _, t, f, q = best
    return (f, t, q, mismatches)


def annotate_probe(probe_primer: Primer, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Annotates a probe based on the type specified in the config.
    Supports: exo, taqman, fpg.
    """
    probe_cfg = config.get("parameters", {}).get("probe", {})
    p_type = probe_cfg.get("type", "exo")
    labels = probe_cfg.get("labels", {})
    
    # Helper to get label with fallback to top-level probe_cfg
    def get_label(key, default):
        return labels.get(key, probe_cfg.get(key, default))
    
    seq = probe_primer.sequence
    
    if p_type == "taqman":
        f = get_label("fluorophore", "FAM")
        q = get_label("quencher", "BHQ1")
        return {
            "type": "taqman",
            "annotated_sequence": f"[{f}]{seq}[{q}]",
            "metadata": {"fluorophore": f, "quencher": q}
        }
    
    # Default RAA logic (for exo and fpg)
    thf_up = probe_cfg.get("thf_upstream_min", THF_UPSTREAM_MIN)
    thf_up_max = probe_cfg.get("thf_upstream_max", THF_UPSTREAM_MAX)
    thf_down = probe_cfg.get("thf_downstream_min", THF_DOWNSTREAM_MIN)
    f = get_label("fluorophore", "FAM")
    q = get_label("quencher", "BHQ1")
    b = get_label("blocker", "C3-spacer")
    a = get_label("abasic", "THF" if p_type == "exo" else "dR-Biotin")

    seq_len = len(seq)
    min_req = thf_up + 1 + thf_down
    if seq_len < min_req:
        # No THF could be placed — leave thf_index unset so consumers can tell
        # "not applicable" apart from "at position 0".
        return {"valid": False, "reason": "too_short", "type": p_type,
                "compliant": False,
                "warnings": [f"probe is {seq_len} nt; needs at least {min_req} nt "
                             f"({thf_up} 5' + abasic + {thf_down} 3')"],
                "annotated_sequence": seq}

    warnings: List[str] = []

    # Preferred: a site inside the 30-38 working window with real T's to carry the
    # dT-fluorophore and dT-quencher, so the labels introduce no mismatch at all.
    site = find_thf_site(seq, thf_up, thf_up_max, thf_down)
    if site is None:
        # Relax only the soft upper bound; ">=30 bases 5'" and ">=15 bases 3'"
        # remain hard rules that the manual lists as design errors when broken.
        site = find_thf_site(seq, thf_up, seq_len - thf_down - 1, thf_down)
        if site is not None:
            warnings.append(
                f"abasic site sits beyond the preferred {thf_up}-{thf_up_max} nt "
                f"upstream window; the cleaved probe is still primer-length but "
                f"further from the documented optimum")

    if site is None:
        # No pair of thymines is positioned legally. TwistAmp Assay Design Manual
        # §3.1.1 explicitly sanctions this case: "if two conveniently separated
        # thymines cannot be located one can simply ignore the mismatch of one of
        # the thymines in the probe with the target sequence. There may be a
        # reduction in the efficiency of the probe, the extent to which cannot be
        # predicted". Do it — but report it, because the resulting probe carries
        # deliberate mismatches that anything validating it against target
        # variants would otherwise misread as a design defect.
        #
        # Note the manual's wording: ONE of the thymines. Accepting a single
        # mismatch before falling back to two keeps the better design whenever the
        # sequence offers one.
        for allowed in (1, 2):
            site = find_thf_site(seq, thf_up, seq_len - thf_down - 1, thf_down,
                                 max_label_mismatches=allowed)
            if site is not None:
                break

    if site is None:
        return {"valid": False, "reason": "no_placeable_abasic_site",
                "type": p_type, "compliant": False,
                "warnings": [f"no position in this {seq_len} nt probe satisfies "
                             f">={thf_up} bases 5' and >={thf_down} bases 3' of the "
                             f"abasic residue"],
                "annotated_sequence": seq}

    fluor_index, thf_index, quencher_index, mismatched_labels = site
    if mismatched_labels:
        warnings.append(
            f"no legally spaced pair of thymines available; {mismatched_labels} "
            f"dT label(s) replace a non-T base and are therefore deliberate "
            f"probe-target mismatches (tolerated per TwistAmp manual §3.1.1, "
            f"but efficiency may drop)")

    # Assemble the annotation. Anything between a label and the abasic residue is
    # an ordinary base and is carried through unchanged.
    annotated = (
        f"{seq[:fluor_index]}[{f}-dT]{seq[fluor_index + 1:thf_index]}"
        f"[{a}]{seq[thf_index + 1:quencher_index]}[{q}-dT]"
        f"{seq[quencher_index + 1:]}[{b}]"
    )

    return {
        "type": p_type,
        "valid": True,
        "compliant": not warnings,
        "warnings": warnings,
        "thf_index": thf_index,
        "fluor_index": fluor_index,
        "quencher_index": quencher_index,
        "mismatched_labels": mismatched_labels,
        "bases_upstream": thf_index,
        "bases_downstream": seq_len - thf_index - 1,
        "annotated_sequence": annotated,
        "metadata": {"fluorophore": f, "quencher": q, "abasic": a, "blocker": b}
    }

def apply_annotation(probe: Primer, anno: Dict[str, Any]) -> None:
    """Copy an annotate_probe() result onto the Primer so it survives to_dict().

    Both probe construction paths (find_exo_probe and parse_primer3_output) must
    transfer the SAME set of fields; doing it in one place stops them drifting.
    `thf_index` in particular used to be computed and then discarded here, which
    left downstream validation unable to locate the cleavage site.
    """
    probe.labeled_sequence = anno.get("annotated_sequence")
    probe.probe_type = anno.get("type")
    probe.thf_index = anno.get("thf_index")
    probe.probe_label_mismatches = anno.get("mismatched_labels", 0)
    probe.probe_compliant = anno.get("compliant")
    for w in anno.get("warnings", []):
        if w not in probe.warnings:
            probe.warnings.append(w)


def find_exo_probe(amplicon_seq: str, fwd_len: int, rev_len: int, config: Dict[str, Any], fwd_start: int = 0) -> Optional[Primer]:
    """
    Finds the best internal oligo (probe) within an amplicon for Exo-RAA.
    
    Enforces a minimum physical gap between the probe and both the forward
    and reverse primers to prevent probe-primer overlap.
    """
    import primer3
    from primerlab.core.tools.thermocalc_wrapper import ThermocalcWrapper
    
    p_cfg = config.get("parameters", {}).get("probe", {})
    p_len_min = p_cfg.get("size", {}).get("min", p_cfg.get("min_size", 46))
    p_len_max = p_cfg.get("size", {}).get("max", p_cfg.get("max_size", 52))
    p_tm_min = p_cfg.get("tm", {}).get("min", p_cfg.get("min_tm", 57.0))
    p_tm_max = p_cfg.get("tm", {}).get("max", p_cfg.get("max_tm", 80.0))

    # Minimum physical gap (bp) between probe ends and primer ends.
    # Prevents probe from overlapping or sitting immediately adjacent to a primer.
    # TwistDx/Agdia recommend at least 3-5bp separation.
    min_gap_fwd = p_cfg.get("min_gap_fwd", 5)
    min_gap_rev = p_cfg.get("min_gap_rev", 5)
    
    # Initialize ThermocalcWrapper with RAA-specific thermodynamic conditions.
    # Be robust against flattened configs where params are directly under 'parameters'
    params = config.get("parameters", {})
    thermo_cfg = params.get("thermodynamics", {})
    
    thermo = ThermocalcWrapper(
        mv_conc=thermo_cfg.get("salt_monovalent", params.get("salt_monovalent", 50.0)),
        dv_conc=thermo_cfg.get("salt_divalent", params.get("salt_divalent", 14.0)),    # RAA typically needs ~14mM Mg2+
        dntp_conc=thermo_cfg.get("dntp_conc", params.get("dntp_conc", 0.8)),
        dna_conc=thermo_cfg.get("dna_conc", params.get("dna_conc", 480.0)),            # RAA typically uses 480nM DNA
        tm_method=thermo_cfg.get("tm_method", params.get("tm_method", "santalucia")),
        salt_corrections=thermo_cfg.get("salt_corrections", params.get("salt_corrections", "owczarzy")),
    )
    
    amp_len = len(amplicon_seq)

    # Probe search bounds with enforced gaps:
    #   start >= fwd_len + min_gap_fwd
    #   end   <= amp_len - rev_len - min_gap_rev  → start <= amp_len - rev_len - min_gap_rev - p_len
    candidates = []

    # Sliding window for probe selection
    for p_len in range(p_len_min, p_len_max + 1):
        probe_start_min = fwd_len + min_gap_fwd
        probe_start_max = amp_len - rev_len - min_gap_rev - p_len
        
        if probe_start_max < probe_start_min:
            continue
            
        for i in range(probe_start_min, probe_start_max + 1):
            p_seq = amplicon_seq[i : i + p_len]
            
            # Use RAA-aware Tm calculation (accounts for Mg2+, DNA conc)
            tm = thermo.calc_tm(p_seq)
            gc = sum(1 for b in p_seq if b in "GC") / p_len * 100
            
            if p_tm_min <= tm <= p_tm_max:
                candidates.append({
                    "sequence": p_seq,
                    "tm": tm,
                    "gc": gc,
                    "local_start": i
                })
                
    if not candidates:
        # NOTE: no local `logger = get_logger()` here. Rebinding the name inside
        # this function makes it local for the WHOLE function body, so the
        # module-level logger used earlier (the non-compliant-probe warning) would
        # raise UnboundLocalError before ever reaching this line.
        logger.warning(f"No probe candidates found satisfying Tm filters: {p_tm_min}-{p_tm_max}")
        return None

    # A probe that has no legally placeable abasic site cannot be cleaved
    # efficiently, so screen for one BEFORE spending thermodynamics on ranking.
    # Doing it afterwards meant the best-Tm window was chosen first and the THF
    # was then forced into it wherever it happened to land.
    if p_cfg.get("type", "exo") != "taqman":
        thf_up = p_cfg.get("thf_upstream_min", THF_UPSTREAM_MIN)
        thf_up_max = p_cfg.get("thf_upstream_max", THF_UPSTREAM_MAX)
        thf_down = p_cfg.get("thf_downstream_min", THF_DOWNSTREAM_MIN)
        compliant = [c for c in candidates
                     if find_thf_site(c["sequence"], thf_up, thf_up_max, thf_down)]
        if compliant:
            candidates = compliant
        else:
            logger.warning(
                f"No probe candidate offers a dT-flanked abasic site within "
                f"{thf_up}-{thf_up_max} nt of its 5' end; the selected probe will "
                f"carry deliberate label mismatches (see probe warnings)")

    # Two-stage ranking to avoid calling calc_homodimer on thousands of candidates:
    # Stage A: Pre-filter by Tm descending → keep top 20 candidates
    # Stage B: Compute homodimer dG only for those 20, then re-rank by
    #          (best homodimer, then best Tm as tiebreaker)
    candidates.sort(key=lambda x: -x["tm"])
    top_candidates = candidates[:20]

    for c in top_candidates:
        c["homodimer_dg"] = primer3.calc_homodimer(c["sequence"]).dg / 1000.0

    top_candidates.sort(key=lambda x: (-x["homodimer_dg"], -x["tm"]))
    best = top_candidates[0]
    
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
    
    # Apply annotations (THF site, fluorophores, etc.)
    anno = annotate_probe(probe, config)
    apply_annotation(probe, anno)

    return probe

def parse_primer3_output(raw_results: Dict[str, Any], config: Dict[str, Any], abs_offset: int = 0) -> List[Dict[str, Any]]:
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
            fwd_rel_start, fwd_len = raw_results.get(fwd_key)
            candidate["forward"] = Primer(
                id=f"forward_{i}",
                sequence=raw_results.get(f'PRIMER_LEFT_{i}_SEQUENCE'),
                tm=raw_results.get(f'PRIMER_LEFT_{i}_TM'),
                gc=raw_results.get(f'PRIMER_LEFT_{i}_GC_PERCENT'),
                length=fwd_len,
                start=fwd_rel_start + abs_offset,
                end=fwd_rel_start + abs_offset + fwd_len - 1,
                hairpin_dg=raw_results.get(f'PRIMER_LEFT_{i}_HAIRPIN_TH', 0.0) / 1000.0,
                homodimer_dg=raw_results.get(f'PRIMER_LEFT_{i}_HOMODIMER_TH', 0.0) / 1000.0,
                end_stability_dg=raw_results.get(f'PRIMER_LEFT_{i}_END_STABILITY', 0.0) / 1000.0
            )
            
        # Reverse Primer
        rev_key = f'PRIMER_RIGHT_{i}'
        if rev_key in raw_results:
            rev_rel_start, rev_len = raw_results.get(rev_key)
            candidate["reverse"] = Primer(
                id=f"reverse_{i}",
                sequence=raw_results.get(f'PRIMER_RIGHT_{i}_SEQUENCE'),
                tm=raw_results.get(f'PRIMER_RIGHT_{i}_TM'),
                gc=raw_results.get(f'PRIMER_RIGHT_{i}_GC_PERCENT'),
                length=rev_len,
                start=rev_rel_start - rev_len + 1 + abs_offset,
                end=rev_rel_start + abs_offset,
                hairpin_dg=raw_results.get(f'PRIMER_RIGHT_{i}_HAIRPIN_TH', 0.0) / 1000.0,
                homodimer_dg=raw_results.get(f'PRIMER_RIGHT_{i}_HOMODIMER_TH', 0.0) / 1000.0,
                end_stability_dg=raw_results.get(f'PRIMER_RIGHT_{i}_END_STABILITY', 0.0) / 1000.0
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
                start=probe_start + abs_offset,
                end=probe_start + abs_offset + probe_len - 1,
                hairpin_dg=raw_results.get(f'PRIMER_INTERNAL_{i}_HAIRPIN_TH', 0.0) / 1000.0,
                homodimer_dg=raw_results.get(f'PRIMER_INTERNAL_{i}_HOMODIMER_TH', 0.0) / 1000.0,
                end_stability_dg=raw_results.get(f'PRIMER_INTERNAL_{i}_END_STABILITY', 0.0) / 1000.0
            )
            candidate["probe"] = probe
            
            # Apply Probe annotations
            anno = annotate_probe(probe, config)
            candidate["probe_annotation"] = anno
            apply_annotation(probe, anno)
        
        if "forward" in candidate and "reverse" in candidate:
            all_candidates.append(candidate)
                
    return all_candidates

def create_amplicon_map(amplicon_seq: str, fwd: Primer, rev: Primer, probe: Optional[Primer] = None, amp_start: Optional[int] = None) -> str:
    """
    Creates a visual text map of the amplicon.
    Uses absolute coordinates to ensure alignment with the provided amplicon_seq.
    """
    amp_len = len(amplicon_seq)
    map_list = ["-"] * amp_len
    
    fwd_start = fwd.start if fwd.start is not None else 0
    rev_start = rev.start if rev.start is not None else (amp_len - rev.length)
    
    # The amplicon_seq provided corresponds to [amp_start, amp_end]
    # We use the provided amp_start to align fwd/rev/probe absolute coordinates.
    if amp_start is None:
        amp_start = fwd_start
    
    f_idx = fwd_start - amp_start
    f_len = fwd.length
    
    r_idx = rev_start - amp_start
    r_len = rev.length
    
    # 1. Mark FWD
    for i in range(f_idx, min(f_idx + f_len, amp_len)):
        if i >= 0:
            map_list[i] = ">"
        
    # 2. Mark REV
    for i in range(r_idx, min(r_idx + r_len, amp_len)):
        if i >= 0:
            map_list[i] = "<"
            
    # 3. Mark Probe
    if probe:
        probe_start = probe.start
        if probe_start is None:
            # Fallback to finding probe sequence in amplicon_seq
            probe_start_idx = amplicon_seq.find(probe.sequence)
            if probe_start_idx != -1:
                probe_start = amp_start + probe_start_idx
            else:
                probe_start = amp_start + f_len + 5
                
        p_idx = probe_start - amp_start
        p_len = probe.length
        if 0 <= p_idx < amp_len:
            for i in range(p_idx, min(p_idx + p_len, amp_len)):
                if map_list[i] in [">", "<"]:
                    map_list[i] = "X" 
                else:
                    map_list[i] = "="
                
    return "".join(map_list)
