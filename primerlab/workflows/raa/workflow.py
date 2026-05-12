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

    # 2. Run Search
    # Default: pass the entire sequence to Primer3 in a single call (no windowing).
    # Windowing is opt-in: only activates when the user explicitly sets
    # 'advanced.window_size' in the config. This avoids silently truncating the
    # search space without the user knowing.
    input_len = len(sequence)
    slice_start = 0

    # Pre-calculate max_workers for auto-balancing (v1.2.3)
    req_cores = config.get("advanced", {}).get("cores")
    if req_cores is None:
        temp_max = min(8, os.cpu_count() or 1)
    else:
        temp_max = int(req_cores)

    windows = []
    slice_start = 0  # Global offset; updated if Smart Slicing is active
    params = config.get("parameters", {})
    target = params.get("target_region")

    # Explicit window_size from user → opt-in windowing mode
    user_window_size = config.get("advanced", {}).get("window_size")
    
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

    elif user_window_size is not None:
        # User explicitly requested windowed search
        window_size = int(user_window_size)
        overlap = config.get("advanced", {}).get("overlap", 200)
        logger.info(f"Windowed search enabled (window={window_size}bp, overlap={overlap}bp)")

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

    # 2. Run Search
    params = config.get("parameters", {})
    target = params.get("target_region")
    search_strategy = params.get("search_strategy", "standard")
    hard_filter = params.get("hard_qc_filter", False)
    target_quota = params.get("num_candidates", 1000)
    max_iters = params.get("max_search_iterations", 5)

    # Prepare Size Buckets if diversified
    size_ranges = params.get('product_size_range', [[150, 300]])
    if search_strategy == "diversified" and len(size_ranges) == 1:
        s_min, s_max = size_ranges[0]
        step = (s_max - s_min) // 3
        if step >= 20:
            size_ranges = [
                [s_min, s_min + step],
                [s_min + step + 1, s_min + 2 * step],
                [s_min + 2 * step + 1, s_max]
            ]
            logger.info(f"Diversified Search: Splitting range into buckets: {size_ranges}")

    # Windowing Logic (Opt-in)
    user_window_size = config.get("advanced", {}).get("window_size")
    windows = []
    if target:
        t_start = target.get("start", 0)
        t_len = target.get("length", 150)
        buffer = 300
        slice_start = max(0, t_start - buffer)
        slice_end = min(input_len, t_start + t_len + buffer)
        logger.info(f"Target detected. Slicing: {slice_start}-{slice_end}")
        sequence = sequence[slice_start:slice_end]
        params["target_region"]["start"] = t_start - slice_start
        windows = [(0, len(sequence))]
    elif user_window_size:
        window_size = int(user_window_size)
        overlap = config.get("advanced", {}).get("overlap", 200)
        for i in range(0, input_len - window_size + 1, window_size - overlap):
            windows.append((i, min(i + window_size, input_len)))
            if windows[-1][1] == input_len: break
    else:
        windows = [(0, input_len)]

    import copy
    p3_wrapper = Primer3Wrapper()
    qc_engine = RAAQC(config)
    
    all_valid_candidates = []
    seen_hashes = set()
    
    # Probe-Centered Search (Probe-First) — only when probe is enabled
    if search_strategy == "probe_centered" and config.get("parameters", {}).get("probe", {}).get("enabled"):
        logger.info("Strategy: Probe-Centered Search. Scanning for optimal probes first...")
        from primerlab.workflows.raa.probe import find_exo_probe, parse_primer3_output as parse_p3

        p_cfg = config.get("parameters", {}).get("probe", {})
        p_len = p_cfg.get("size", {}).get("opt", 48)
        probe_pool = []

        for scan_i in range(0, len(sequence) - p_len, 10):
            sub = sequence[scan_i: scan_i + p_len + 100]
            prb = find_exo_probe(sub, 5, 5, config, fwd_start=scan_i)
            if prb and prb.sequence not in [x.sequence for x in probe_pool]:
                probe_pool.append(prb)

        logger.info(f"Found {len(probe_pool)} probe candidates. Finding flanking primers...")
        for prb in probe_pool[:50]:
            local_cfg = copy.deepcopy(config)
            # Use SEQUENCE_TARGET so primers are guaranteed to flank the probe
            local_cfg["parameters"]["target_region"] = {"start": prb.start, "length": prb.length}
            try:
                res_dict = p3_wrapper.design_primers(sequence, local_cfg)
                cand_list = parse_p3(res_dict, config)
                for ci, cand in enumerate(cand_list):
                    h = f"{cand['forward'].sequence}_{cand['reverse'].sequence}"
                    # --- STRICT OVERLAP CHECK ---
                    f_end = cand['forward'].start + cand['forward'].length
                    r_start = cand['reverse'].start
                    p_start = prb.start
                    p_end = prb.start + prb.length
                    
                    min_gap = 5 # RAA needs gap for enzyme accessibility
                    if (p_start < f_end + min_gap) or (p_end > r_start - min_gap):
                        logger.debug(f"Overlap detected for probe at {prb.start}. Skipping.")
                        continue

                    seen_hashes.add(h)
                    all_valid_candidates.append({
                        "triplet": cand,
                        "p3_penalty": res_dict.get(f'PRIMER_PAIR_{ci}_PENALTY', 99.0),
                        "product_size": res_dict.get(f'PRIMER_PAIR_{ci}_PRODUCT_SIZE', 0),
                        "qc": qcr
                    })
            except Exception as e:
                logger.debug(f"Probe-centered search failed for probe at {prb.start}: {e}")
                continue


    # STANDARD / DIVERSIFIED SEARCH with Iterative Loop
    else:
        for s_range in size_ranges:
            current_bucket_valid = []
            bucket_quota = target_quota // len(size_ranges)
            excluded_regions = copy.deepcopy(params.get("excluded_regions", []))
            
            for iteration in range(max_iters):
                if len(current_bucket_valid) >= bucket_quota: break
                
                logger.info(f"Search Iteration {iteration+1} for size {s_range} (Found: {len(current_bucket_valid)}/{bucket_quota})")
                
                for start, end in windows:
                    sub_seq = sequence[start:end]
                    local_config = copy.deepcopy(config)
                    local_config["parameters"]["product_size_range"] = [s_range]
                    local_config["parameters"]["num_candidates"] = bucket_quota * 2 # Over-request
                    local_config["parameters"]["excluded_regions"] = excluded_regions
                    
                    try:
                        res_dict = p3_wrapper.design_primers(sub_seq, local_config)
                        num_returned = res_dict.get('PRIMER_PAIR_NUM_RETURNED', 0)
                        
                        for i in range(num_returned):
                            f_seq = res_dict.get(f'PRIMER_LEFT_{i}_SEQUENCE')
                            r_seq = res_dict.get(f'PRIMER_RIGHT_{i}_SEQUENCE')
                            if not f_seq or not r_seq: continue
                            
                            pair_hash = f"{f_seq}_{r_seq}"
                            if pair_hash not in seen_hashes:
                                # Perform RAPID QC check for dimer threshold
                                # We need to create Primer objects to use QC engine
                                from primerlab.workflows.raa.probe import parse_primer3_output
                                # Minimal dict to trick parse_primer3_output
                                mini_res = {
                                    'PRIMER_LEFT_NUM_RETURNED': 1,
                                    f'PRIMER_LEFT_0': res_dict.get(f'PRIMER_LEFT_{i}'),
                                    f'PRIMER_LEFT_0_SEQUENCE': f_seq,
                                    f'PRIMER_LEFT_0_TM': res_dict.get(f'PRIMER_LEFT_{i}_TM'),
                                    f'PRIMER_LEFT_0_GC_PERCENT': res_dict.get(f'PRIMER_LEFT_{i}_GC_PERCENT'),
                                    f'PRIMER_RIGHT_0': res_dict.get(f'PRIMER_RIGHT_{i}'),
                                    f'PRIMER_RIGHT_0_SEQUENCE': r_seq,
                                    f'PRIMER_RIGHT_0_TM': res_dict.get(f'PRIMER_RIGHT_{i}_TM'),
                                    f'PRIMER_RIGHT_0_GC_PERCENT': res_dict.get(f'PRIMER_RIGHT_{i}_GC_PERCENT'),
                                }
                                if f'PRIMER_INTERNAL_{i}_SEQUENCE' in res_dict:
                                    mini_res[f'PRIMER_INTERNAL_0_SEQUENCE'] = res_dict.get(f'PRIMER_INTERNAL_{i}_SEQUENCE')
                                    mini_res[f'PRIMER_INTERNAL_0'] = res_dict.get(f'PRIMER_INTERNAL_{i}')
                                    mini_res[f'PRIMER_INTERNAL_0_TM'] = res_dict.get(f'PRIMER_INTERNAL_{i}_TM')
                                
                                cand_list = parse_primer3_output(mini_res, config)
                                if cand_list:
                                    c = cand_list[0]
                                    
                                    # --- STRICT OVERLAP CHECK ---
                                    if c.get("probe"):
                                        p = c["probe"]
                                        f_end = c["forward"].start + c["forward"].length
                                        r_start = c["reverse"].start
                                        p_start = p.start
                                        p_end = p.start + p.length
                                        
                                        min_gap = 5
                                        if (p_start < f_end + min_gap) or (p_end > r_start - min_gap):
                                            continue

                                    qcr = qc_engine.evaluate_pair_extended(c["forward"], c["reverse"], c.get("probe"))
                                    
                                    # HARD FILTER CHECK
                                    if hard_filter:
                                        # Only accept if Tier 1 (0 warnings)
                                        if len(qcr.warnings) > 0:
                                            # Still add to excluded to avoid finding it again
                                            f_pos, f_len = res_dict.get(f'PRIMER_LEFT_{i}')
                                            excluded_regions.append([f_pos, f_len])
                                            continue
                                    
                                    seen_hashes.add(pair_hash)
                                    # Store results in a clean structure
                                    item = {
                                        "triplet": c,
                                        "p3_penalty": res_dict.get(f'PRIMER_PAIR_{i}_PENALTY', 99.0),
                                        "product_size": res_dict.get(f'PRIMER_PAIR_{i}_PRODUCT_SIZE', 0),
                                        "qc": qcr
                                    }
                                    current_bucket_valid.append(item)
                                    
                                    if len(current_bucket_valid) >= bucket_quota: break
                        
                    except Exception as e:
                        logger.debug(f"Iterative window failed: {e}")
                
                if not hard_filter: break # No looping if hard filter is off
                if len(current_bucket_valid) >= bucket_quota: break
            
            all_valid_candidates.extend(current_bucket_valid)

    logger.info(f"✅ Search complete. Total valid candidates: {len(all_valid_candidates)}")
    
    # 4. Final Ranking Logic (Replace the old Stage 1)
    evaluated_results = []
    for item in all_valid_candidates:
        c = item["triplet"]
        qcr = item["qc"]
        p3_penalty = item["p3_penalty"]
        product_size = item["product_size"]
        
        # Calculate Tier
        num_warnings = len(qcr.warnings)
        tier = 1 if num_warnings == 0 else (2 if num_warnings <= 2 else 3)
        
        # Calculate Amplicon for the result object
        from primerlab.core.models import Amplicon
        fwd = c["forward"]
        rev = c["reverse"]
        amp_seq = sequence[fwd.start : rev.end + 1]
        
        amplicon = Amplicon(
            start=fwd.start, end=rev.start, length=product_size,
            sequence=amp_seq, gc=0.0, tm_forward=fwd.tm, tm_reverse=rev.tm
        )
        
        evaluated_results.append({
            "primers": c, # triplet
            "amplicon": amplicon,
            "qc": qcr,
            "p3_penalty": p3_penalty,
            "tier": tier,
            "score": p3_penalty
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

    # 5.1 Stage 2: ViennaRNA Accessibility Refining (Parallelized)
    vienna_limit = config.get("qc", {}).get("vienna_ranking_limit", 20)
    if vienna_limit > 0 and qc_engine.vienna.is_available:
        count = min(len(evaluated_results), vienna_limit)
        workers = temp_max  # Reuse core count from earlier config
        logger.info(f"Refining Top {count} candidates with ViennaRNA folding at Stage 2 ({workers} workers)...")

        from concurrent.futures import ThreadPoolExecutor, as_completed

        def _fold_one(res):
            """Fold a single amplicon. Returns (res, vienna_result)."""
            amp = res["amplicon"]
            amp_seq = sequence[amp.start : amp.end + 1]
            v_res = qc_engine.evaluate_target_structure(amp_seq)
            return res, amp_seq, v_res

        top_results = evaluated_results[:count]

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(_fold_one, res): res for res in top_results}
            for future in as_completed(futures):
                res, amp_seq, v_res = future.result()

                res["amplicon"].sequence = amp_seq
                res["qc"].additional_metrics = {
                    "vienna_dg": v_res["dg"],
                    "normalized_dg": v_res["normalized_dg"]
                }

                vienna_penalty = 0.0
                if not v_res["accessible"]:
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
            "primers": {k: v.to_dict() for k, v in res["primers"].items() if v is not None},
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

    # 6. Final Result Object
    if evaluated_results:
        top_res = evaluated_results[0]
        primers = top_res["primers"]
        amplicons = [top_res["amplicon"]]
        qc_result = top_res["qc"]
    else:
        top_res = {}
        primers = {}
        amplicons = []
        qc_result = None

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
        raw={}
    )

    return result
