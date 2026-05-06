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

    import copy
    all_raw_data = []
    p3_wrapper = Primer3Wrapper()
    for start, end in windows:
        sub_seq = sequence[start:end]
        
        # Localize config to prevent modifying the global dict and to adjust coordinates
        local_config = copy.deepcopy(config)
        global_excluded = config.get("parameters", {}).get("excluded_regions", [])
        
        if global_excluded:
            local_excluded = []
            for r in global_excluded:
                if isinstance(r, (list, tuple)):
                    r_start, r_len = r[0], r[1]
                elif isinstance(r, dict):
                    r_start, r_len = r['start'], r['length']
                else:
                    continue
                
                r_end = r_start + r_len
                # Check overlap with current window
                if r_start < end and r_end > start:
                    local_r_start = max(0, r_start - start)
                    local_r_end = min(end - start, r_end - start)
                    if local_r_end > local_r_start:
                        local_excluded.append([local_r_start, local_r_end - local_r_start])
            
            if "parameters" not in local_config:
                local_config["parameters"] = {}
            local_config["parameters"]["excluded_regions"] = local_excluded
            
        try:
            res = p3_wrapper.design_primers(sub_seq, local_config)
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
            probe = find_exo_probe(amp_seq, fwd.length, rev.length, config, fwd_start=fwd.start)
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

        # 6. Ranking Score = Pure Primer3 Penalty (Objective)
        # Lower penalty = closer to ideal thermodynamic parameters.
        # QC checks are informational labels only, NOT score deductions.
        p3_penalty = raw_results.get(f'PRIMER_PAIR_{orig_i}_PENALTY', 100.0)
        
        amplicon = Amplicon(
            start=fwd.start, end=rev.start, length=product_size,
            sequence=amp_seq, gc=0.0, tm_forward=fwd.tm, tm_reverse=rev.tm
        )
        
        # Calculate Tier based on warnings
        num_warnings = len(qcr.warnings)
        tier = 1 if num_warnings == 0 else (2 if num_warnings <= 2 else 3)

        evaluated_results.append({
            "primers": primers_triplet,
            "amplicon": amplicon,
            "qc": qcr,
            "p3_penalty": p3_penalty,
            "tier": tier,
            "score": p3_penalty  # Keep 'score' for backward compatibility
        })
    
    # 5. Stage 1: Sort by (tier, p3_penalty) — Clean candidates first, then minor devs, then suboptimal.
    # Within each tier, sort by p3_penalty ascending (lowest is best).
    evaluated_results.sort(key=lambda x: (x["tier"], x["p3_penalty"]))

    # Store Stage 1 Ranks & Initial Scores
    for idx, res in enumerate(evaluated_results):
        res["stage1_rank"] = idx + 1
        res["vienna_penalty"] = 0.0
        res["final_score"] = float(idx + 1)
        res["final_rank"] = idx + 1

    # Log Top 5 for debugging
    for i, res in enumerate(evaluated_results[:5]):
        p_status = "YES" if res["primers"].get("probe") else "NO"
        logger.info(f"Stage 1 Rank {i+1}: Tier {res['tier']} | P3 Penalty={res['p3_penalty']:.2f}, Probe={p_status}")

    # 5.1 Stage 2: ViennaRNA Accessibility Refining
    vienna_limit = config.get("qc", {}).get("vienna_ranking_limit", 20)
    if vienna_limit > 0 and qc_engine.vienna.is_available:
        count = min(len(evaluated_results), vienna_limit)
        logger.info(f"Refining Top {count} candidates with ViennaRNA folding at Stage 2...")
        for res in evaluated_results[:count]:
            # Extract amplicon sequence
            amp = res["amplicon"]
            amp_seq = sequence[amp.start : amp.end + 1]
            
            # Run ViennaRNA folding
            v_res = qc_engine.evaluate_target_structure(amp_seq)
            
            # Store vienna data in result for transparency
            res["amplicon"].sequence = amp_seq
            res["qc"].additional_metrics = {"vienna_dg": v_res["dg"], "normalized_dg": v_res["normalized_dg"]}
            
            # Calculate vienna penalty
            vienna_penalty = 0.0
            if not v_res["accessible"]:
                # Penalty based on stability (normalized dG)
                vienna_penalty = abs(v_res["normalized_dg"]) * 1.5
                res["qc"].warnings.append(
                    f"Amplicon secondary structure stable (normalized ΔG: {v_res['normalized_dg']:.2f} kcal/mol). "
                    f"Target accessibility re-ranking penalty applied: +{vienna_penalty:.2f} ranks."
                )
            
            res["vienna_penalty"] = vienna_penalty
            res["final_score"] = float(res["stage1_rank"]) + vienna_penalty
        
        # Ensure any candidate outside count has high final score
        for res in evaluated_results[count:]:
            res["vienna_penalty"] = 0.0
            res["final_score"] = float(res["stage1_rank"]) + 999.0
            
        # Re-sort after ViennaRNA penalties
        evaluated_results.sort(key=lambda x: x["final_score"])
        
        # Finalize ranks
        for idx, res in enumerate(evaluated_results):
            res["final_rank"] = idx + 1

    # 6. Select Top Result and prepare Output
    if evaluated_results:
        top_res = evaluated_results[0]
        primers = top_res["primers"]
        qc_result = top_res["qc"]
        # Only include the TOP amplicon in the main list to avoid confusion
        amplicons = [top_res["amplicon"]]
        logger.info(f"Top candidate selected (Stage 1 Rank: {top_res['stage1_rank']}, Final Rank: {top_res['final_rank']}, Final Score: {top_res['final_score']:.2f})")
    else:
        primers = {}
        qc_result = None
        amplicons = []
        logger.warning("No valid candidates found.")

    # 6.1 Build Ranking Details (for CSV export — all objective physical values)
    ranking_details = []
    # Include up to len(evaluated_results) for better user review
    for res in evaluated_results[:max(20, len(evaluated_results))]:
        row = {
            "rank": res["final_rank"],
            "stage1_rank": res["stage1_rank"],
            "tier": f"Tier {res['tier']}",
            "p3_penalty": round(res["p3_penalty"], 3),
            "vienna_penalty": round(res.get("vienna_penalty", 0.0), 3),
            "final_score": round(res["final_score"], 3),
            "fwd_tm": res["primers"]["forward"].tm if res["primers"].get("forward") else None,
            "rev_tm": res["primers"]["reverse"].tm if res["primers"].get("reverse") else None,
            "prb_tm": res["primers"]["probe"].tm if res["primers"].get("probe") else None,
            "fwd_gc": res["primers"]["forward"].gc if res["primers"].get("forward") else None,
            "rev_gc": res["primers"]["reverse"].gc if res["primers"].get("reverse") else None,
            "product_size": res["amplicon"].length,
            "cross_dimer_dg": res["qc"].cross_dimer_dg,
            "vienna_dg": res["qc"].additional_metrics.get("vienna_dg") if res["qc"] and res["qc"].additional_metrics else None,
            "normalized_dg": res["qc"].additional_metrics.get("normalized_dg") if res["qc"] and res["qc"].additional_metrics else None,
            "qc_warnings": len(res["qc"].warnings),
            "fwd_seq": res["primers"]["forward"].sequence if res["primers"].get("forward") else None,
            "rev_seq": res["primers"]["reverse"].sequence if res["primers"].get("reverse") else None,
            "prb_seq": res["primers"]["probe"].sequence if res["primers"].get("probe") else None,
        }
        ranking_details.append(row)

    # 6.2 Prepare Detailed Alternatives (Full JSON Data)
    num_alt_export = config.get("output", {}).get("num_results_to_export", 10)
    alternatives_data = []
    for res in evaluated_results[:num_alt_export]:
        alt = {
            "final_rank": res["final_rank"],
            "stage1_rank": res["stage1_rank"],
            "tier": res["tier"],
            "p3_penalty": round(res["p3_penalty"], 3),
            "vienna_penalty": round(res.get("vienna_penalty", 0.0), 3),
            "final_score": round(res["final_score"], 3),
            "primers": {k: v.to_dict() for k, v in res["primers"].items()},
            "amplicon": res["amplicon"].to_dict(),
            "qc": res["qc"].to_dict(),
            "visual_map": create_amplicon_map(
                res["amplicon"].sequence,
                res["primers"].get("forward"),
                res["primers"].get("reverse"),
                res["primers"].get("probe")
            )
        }
        alternatives_data.append(alt)

    # 7. Metadata & Result
    from primerlab import __version__
    metadata = RunMetadata(
        workflow="raa",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version=__version__,
        parameters=config.get("parameters", {})
    )

    # Add map to top candidate metadata if candidates exist
    if amplicons:
        metadata.parameters["visual_map"] = create_amplicon_map(
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
        visual_map=metadata.parameters.get("visual_map"),
        alternatives=alternatives_data,
        ranking_details=ranking_details,
        raw=raw_results
    )

    return result
