from typing import Dict, Any
import os
from datetime import datetime, timezone
from primerlab.core.models import WorkflowResult, Amplicon, RunMetadata
from primerlab.core.tools.primer3_wrapper import Primer3Wrapper
from primerlab.core.sequence import SequenceLoader
from primerlab.core.logger import get_logger
from primerlab.core.exceptions import WorkflowError
from primerlab.workflows.raa.qc import RAAQC
from primerlab.workflows.raa.probe import parse_primer3_output, find_exo_probe, annotate_probe, create_amplicon_map

logger = get_logger()

def run_raa_workflow(config: Dict[str, Any]) -> WorkflowResult:
    """
    Executes the RAA workflow (Primers + optional Exo-Probe).
    """
    logger.info("Starting RAA Workflow execution...")

    # 1. Parse Input
    input_config = config.get("input", {})
    raw_sequence = input_config.get("sequence")
    seq_path = input_config.get("sequence_path")
    preserve_iupac = input_config.get("preserve_iupac", True)
    input_type = input_config.get("type", "auto")

    try:
        if seq_path:
            sequence = SequenceLoader.load(seq_path, preserve_iupac=preserve_iupac, input_type=input_type)
        elif raw_sequence:
            sequence = SequenceLoader.load(raw_sequence, preserve_iupac=preserve_iupac, input_type=input_type)
        else:
            raise WorkflowError("No sequence provided.", "ERR_WORKFLOW_001")
    except Exception as e:
        raise WorkflowError(f"Sequence loading failed: {e}", "ERR_WORKFLOW_SEQ")

    logger.info(f"Input sequence length: {len(sequence)} bp")

    # 2. Run Primer3
    probe_cfg = config.get("parameters", {}).get("probe", {})
    probe_enabled = probe_cfg.get("enabled", False)

    if not probe_enabled:
        logger.info("RAA Mode: Primer-only (Probe disabled)")
        if "probe" in config.get("parameters", {}):
            # Tell Primer3 not to design internal oligos
            config["parameters"]["probe"]["enabled"] = False
    else:
        logger.info(f"RAA Mode: Probe-based ({probe_cfg.get('type', 'exo')})")
        # Ensure Primer3Wrapper knows to pick internal oligos
        if "probe" not in config["parameters"]:
            config["parameters"]["probe"] = {}
        config["parameters"]["probe"]["enabled"] = True

    # 2. Run Search (Parallel Windowing for Long Sequences)
    input_len = len(sequence)
    slice_start = 0
    window_size = config.get("advanced", {}).get("window_size", 350)
    overlap = config.get("advanced", {}).get("overlap", 200)
    
    # Pre-calculate max_workers for auto-balancing (v1.2.3)
    req_cores = config.get("advanced", {}).get("cores")
    if req_cores is None:
        # Default behavior: use up to 8 cores for windowing if not specified
        temp_max = min(8, os.cpu_count() or 1)
    else:
        temp_max = int(req_cores)

    windows = []
    slice_start = 0  # Global offset; updated if Smart Slicing is active
    params = config.get("parameters", {})
    target = params.get("target_region")
    
    if target:
        # Smart Slicing: Crop sequence around the target to speed up Primer3
        t_start = target.get("start", 0)
        t_len = target.get("length", 150)
        
        buffer = 300  # Sufficient for flanking primers
        slice_start = max(0, t_start - buffer)
        slice_end = min(input_len, t_start + t_len + buffer)
        
        logger.info(f"Target detected. Slicing sequence: {slice_start}-{slice_end} (Buffer: {buffer}bp)")
        sequence = sequence[slice_start:slice_end]
        
        # Translate target to relative coordinates for the slice
        params["target_region"]["start"] = t_start - slice_start
        
        # Single window for the slice
        windows = [(0, len(sequence))]
    elif input_len > 600:
        # Auto-balance overlap if needed
        if temp_max > 1 and config.get("advanced", {}).get("overlap") is None:
            step = max(1, (input_len - window_size) // (temp_max - 1))
            overlap = max(150, window_size - step)

        for i in range(0, input_len - window_size + 1, window_size - overlap):
            start = i
            end = min(i + window_size, input_len)
            windows.append((start, end))
            if end == input_len: break
            
        if windows and windows[-1][1] < input_len:
            windows.append((input_len - window_size, input_len))
    else:
        windows = [(0, input_len)]

    all_raw_data = []
    p3_wrapper = Primer3Wrapper()
    for start, end in windows:
        sub_seq = sequence[start:end]
        try:
            res = p3_wrapper.design_primers(sub_seq, config)
            all_raw_data.append((res, start + slice_start))
        except Exception as e:
            logger.warning(f"⚠️ Window {(start, end)} failed: {e}")


    # 3. Merge and Deduplicate Results
    raw_results = {}
    total_pairs = 0
    seen_hashes = set()
    
    for res_dict, offset in all_raw_data:
        num_returned = res_dict.get('PRIMER_PAIR_NUM_RETURNED', 0)
        for i in range(num_returned):
            fwd_seq = res_dict.get(f'PRIMER_LEFT_{i}_SEQUENCE')
            rev_seq = res_dict.get(f'PRIMER_RIGHT_{i}_SEQUENCE')
            if not fwd_seq or not rev_seq: continue
            
            pair_hash = f"{fwd_seq}_{rev_seq}"
            if pair_hash not in seen_hashes:
                idx = total_pairs
                for key, val in res_dict.items():
                    if any(key.startswith(p) for p in [f'PRIMER_LEFT_{i}', f'PRIMER_RIGHT_{i}', f'PRIMER_INTERNAL_{i}', f'PRIMER_PAIR_{i}']):
                        new_key = key.replace(f'_{i}', f'_{idx}')
                        # Adjust coordinates (POS is a comma-separated string: "start,len")
                        if '_POS' in key and isinstance(val, str) and ',' in val:
                            p_start, p_len = map(int, val.split(','))
                            raw_results[new_key] = f"{p_start + offset},{p_len}"
                        else:
                            raw_results[new_key] = val
                seen_hashes.add(pair_hash)
                total_pairs += 1

    raw_results['PRIMER_PAIR_NUM_RETURNED'] = total_pairs
    raw_results['PRIMER_LEFT_NUM_RETURNED'] = total_pairs
    logger.info(f"✅ Parallel search complete. Found {total_pairs} unique candidates across all windows.")
    
    # Advanced: Evaluate target sequence accessibility
    qc_engine = RAAQC(config)
    target_qc = qc_engine.evaluate_target_structure(sequence)
    if target_qc["warnings"]:
        logger.warning(f"Target Structure Warning: {target_qc['warnings']}")

    # 3. Parse Results (returns List of triplets)
    candidates = parse_primer3_output(raw_results, config)
    logger.info(f"Processing {len(candidates)} candidate sets for deep QC...")

    # 4. Evaluate and Score all candidates
    qc_engine = RAAQC(config)
    evaluated_results = []
    probe = None  # Initialize to prevent UnboundLocalError later

    for primers_triplet in candidates:
        fwd = primers_triplet["forward"]
        rev = primers_triplet["reverse"]
        probe = primers_triplet.get("probe")
        
        # Extract original index from fwd ID (e.g. "forward_5" -> 5)
        orig_i = int(fwd.id.split("_")[1])

        # Extract amplicon sequence for this candidate
        from primerlab.core.models import Amplicon
        product_size = raw_results.get(f'PRIMER_PAIR_{orig_i}_PRODUCT_SIZE', 0)
        amp_seq = sequence[fwd.start : rev.end + 1]
        
        # RAA-specific pair QC
        qcr = qc_engine.evaluate_pair_extended(fwd, rev, probe)
        
        # Probe-specific logic
        if not probe and config.get("parameters", {}).get("probe", {}).get("enabled"):
            probe = find_exo_probe(amp_seq, fwd.length, rev.length, config)
            if probe:
                logger.debug(f"Manual fallback found probe for triplet {orig_i}")
                # Add annotation
                ann = annotate_probe(probe, config)
                probe.labeled_sequence = ann["annotated_sequence"]
                primers_triplet["probe"] = probe
        
        if probe:
            probe_qc = qc_engine.evaluate_probe(probe, fwd, rev)
            qcr.warnings.extend(probe_qc["warnings"])
            if not probe_qc["probe_tm_ok"]:
                qcr.tm_balance_ok = False

        # Scoring logic
        p3_penalty = raw_results.get(f'PRIMER_PAIR_{orig_i}_PENALTY', 100.0)
        qc_penalty = len(qcr.warnings) * 10.0
        dimer_penalty = 0
        if qcr.cross_dimer_dg < -8.0:
            dimer_penalty += abs(qcr.cross_dimer_dg) * 2.0
            
        total_score = p3_penalty + qc_penalty + dimer_penalty
        
        amplicon = Amplicon(
            start=fwd.start, end=rev.start, length=product_size,
            sequence=amp_seq, gc=0.0, tm_forward=fwd.tm, tm_reverse=rev.tm
        )
        
        evaluated_results.append({
            "primers": primers_triplet,
            "amplicon": amplicon,
            "qc": qcr,
            "score": total_score
        })
    
    # 5. Rerank based on total_score (Lowest is Best)
    evaluated_results.sort(key=lambda x: x["score"])

    # Log Top 5 for debugging
    for i, res in enumerate(evaluated_results[:5]):
        p_status = "YES" if res["primers"].get("probe") else "NO"
        logger.info(f"Candidate Rank {i+1}: Score={res['score']:.2f}, Probe={p_status}")

    # 5.1 ViennaRNA Tiering (Advanced QC for RAA accessibility)
    vienna_limit = config.get("qc", {}).get("vienna_ranking_limit", 20)
    if vienna_limit > 0 and qc_engine.vienna.is_available:
        count = min(len(evaluated_results), vienna_limit)
        logger.info(f"Refining Top {count} candidates with ViennaRNA folding...")
        for res in evaluated_results[:count]:
            # Extract amplicon sequence
            amp = res["amplicon"]
            # Coordinates from Primer3: start is 5' of FWD, end is 3' of REV
            amp_seq = sequence[amp.start : amp.end + 1]
            
            # Run ViennaRNA folding
            v_res = qc_engine.evaluate_target_structure(amp_seq)
            
            # Add accessibility penalty: more stable structure = higher score (worse)
            if not v_res["accessible"]:
                # Penalty based on stability (normalized dG)
                penalty = abs(v_res["normalized_dg"]) / 5.0
                res["score"] += penalty
                res["qc"].warnings.append(f"Amplicon secondary structure stable (normalized ΔG: {v_res['normalized_dg']:.2f}). Penalty applied.")
            
            # Store vienna data in result for transparency
            res["amplicon"].sequence = amp_seq
            res["qc"].additional_metrics = {"vienna_dg": v_res["dg"], "normalized_dg": v_res["normalized_dg"]}
        
        # Final rerank after ViennaRNA penalties
        evaluated_results.sort(key=lambda x: x["score"])

    # 6. Select Top Result and prepare Output
    if evaluated_results:
        top_res = evaluated_results[0]
        primers = top_res["primers"]
        qc_result = top_res["qc"]
        amplicons = [res["amplicon"] for res in evaluated_results]
        logger.info(f"Top candidate selected (Global Score: {top_res['score']:.2f})")
    else:
        primers = {}
        qc_result = None
        amplicons = []
        logger.warning("No valid candidates found.")

    # 6. Metadata & Result
    from primerlab import __version__
    metadata = RunMetadata(
        workflow="raa",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version=__version__,
        parameters=config.get("parameters", {})
    )

    # Prepare alternatives for transparency (Top 10)
    alternatives_data = []
    for res in evaluated_results[:10]:
        alt = {
            "score": res["score"],
            "fwd_tm": res["primers"].get("forward").tm if res["primers"].get("forward") else 0,
            "rev_tm": res["primers"].get("reverse").tm if res["primers"].get("reverse") else 0,
            "product_size": res["amplicon"].length,
            "cross_dimer_dg": res["qc"].cross_dimer_dg,
            "has_probe": "Yes" if res["primers"].get("probe") else "No"
        }
        alternatives_data.append(alt)

    # 7. Metadata and Result Construction
    # Add amplicon maps to alternatives
    for i, alt in enumerate(alternatives_data):
        res = evaluated_results[i]
        alt["visual_map"] = create_amplicon_map(
            res["amplicon"].sequence,
            res["primers"].get("forward"),
            res["primers"].get("reverse"),
            res["primers"].get("probe")
        )

    # Add map to top candidate metadata
    metadata["visual_map"] = create_amplicon_map(
        amplicons[0].sequence,
        primers.get("forward"),
        primers.get("reverse"),
        primers.get("probe")
    )

    result = WorkflowResult(
        workflow="raa",
        primers=primers,
        amplicons=amplicons,
        metadata=metadata,
        qc=qc_result,
        score=top_res.get("score") if evaluated_results else None,
        alternatives=alternatives_data,
        raw=raw_results
    )

    return result
