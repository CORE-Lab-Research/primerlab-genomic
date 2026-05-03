from typing import Dict, Any
from datetime import datetime, timezone
from primerlab.core.models import WorkflowResult, Amplicon, RunMetadata
from primerlab.core.tools.primer3_wrapper import Primer3Wrapper
from primerlab.core.sequence import SequenceLoader
from primerlab.core.logger import get_logger
from primerlab.core.exceptions import WorkflowError
from primerlab.workflows.raa.qc import RAAQC
from primerlab.workflows.raa.probe import parse_primer3_output

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

    # 2. Run Search (Parallel Windowing for Long Sequences)
    input_len = len(sequence)
    window_size = config.get("advanced", {}).get("window_size", 350)
    overlap = config.get("advanced", {}).get("overlap", 200)
    
    windows = []
    if input_len > 600:
        logger.info(f"🚀 Long sequence detected ({input_len}bp). Enabling Multi-core Parallel Search...")
        for i in range(0, input_len - window_size + overlap, window_size - overlap):
            start = i
            end = min(i + window_size, input_len)
            windows.append((start, end))
            if end == input_len: break
    else:
        windows = [(0, input_len)]

    all_raw_data = []
    from concurrent.futures import ProcessPoolExecutor
    import os
    
    # Use dynamic core allocation from config (v1.2.1)
    req_cores = config.get("advanced", {}).get("cores")
    if req_cores is None:
        max_workers = min(len(windows), os.cpu_count() or 1, 8) # Default safe limit
    else:
        # User specified cores (could be 64 on HPC!)
        max_workers = min(len(windows), int(req_cores))
    
    p3_wrapper = Primer3Wrapper()
    
    if max_workers > 1:
        logger.info(f"📡 Dispatching searches across {max_workers} CPU cores...")
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for start, end in windows:
                sub_seq = sequence[start:end]
                futures.append(executor.submit(p3_wrapper.design_primers, sub_seq, config))
            
            for i, future in enumerate(futures):
                try:
                    res = future.result(timeout=config.get("advanced", {}).get("timeout", 300))
                    all_raw_data.append((res, windows[i][0]))
                except Exception as e:
                    logger.warning(f"⚠️ Window {windows[i]} failed: {e}")
    else:
        raw_results = p3_wrapper.design_primers(sequence, config)
        all_raw_data = [(raw_results, 0)]

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

    for i, primers_triplet in enumerate(candidates):
        fwd = primers_triplet["forward"]
        rev = primers_triplet["reverse"]
        probe = primers_triplet.get("probe")
        
        # RAA-specific pair QC (includes cross dimer and GC clamp checks with ViennaRNA)
        qcr = qc_engine.evaluate_pair_extended(fwd, rev, probe)
        
        # Probe-specific QC
        if probe:
            probe_qc = qc_engine.evaluate_probe(probe, fwd, rev)
            qcr.warnings.extend(probe_qc["warnings"])
            if not probe_qc["probe_tm_ok"]:
                qcr.tm_balance_ok = False

        # Calculate a combined score for ranking:
        # Base penalty from Primer3 (lower is better) + 
        # penalty for QC warnings (higher is worse)
        p3_penalty = raw_results.get(f'PRIMER_PAIR_{i}_PENALTY', 100.0)
        qc_penalty = len(qcr.warnings) * 10.0 # Heavy penalty for warnings
        
        # Dimer penalty: add absolute dG if below -8.0 (more negative = more penalty)
        dimer_penalty = 0
        if qcr.cross_dimer_dg < -8.0:
            dimer_penalty += abs(qcr.cross_dimer_dg) * 2.0
            
        total_score = p3_penalty + qc_penalty + dimer_penalty
        
        # Create Amplicon for this candidate
        product_size = raw_results.get(f'PRIMER_PAIR_{i}_PRODUCT_SIZE', 0)
        amplicon = Amplicon(
            start=fwd.start,
            end=rev.start,
            length=product_size,
            sequence="N/A",
            gc=0.0,
            tm_forward=fwd.tm,
            tm_reverse=rev.tm
        )
        
        evaluated_results.append({
            "primers": primers_triplet,
            "amplicon": amplicon,
            "qc": qcr,
            "score": total_score
        })

    # 5. Rerank based on total_score (Lowest is Best)
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
            "cross_dimer_dg": res["qc"].cross_dimer_dg
        }
        alternatives_data.append(alt)

    # 7. Post-processing: Label Exo-probes
    def format_exo_probe(seq, labels):
        if not seq or len(seq) < 45: return seq
        # Standard RAA Exo-probe layout:
        # [5'] -- (~30nt) -- [FAM-dT][THF][BHQ1-dT] -- (~15nt) -- [3' Blocker]
        # We'll place it at 30bp from 5' end as a heuristic if not specified
        pos = 30
        labeled = (
            seq[:pos-1] + 
            f"[{labels.get('fluorophore', 'FAM')}-dT]" +
            "[THF]" +
            f"[{labels.get('quencher', 'BHQ1')}-dT]" +
            seq[pos+2:] +
            f"[{labels.get('blocker', 'C3-spacer')}]"
        )
        return labeled

    if probe:
        probe_labels = config.get("parameters", {}).get("probe", {}).get("labels", {})
        probe.labeled_sequence = format_exo_probe(probe.sequence, probe_labels)

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
