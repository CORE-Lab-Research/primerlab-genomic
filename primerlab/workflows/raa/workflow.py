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

    p3_wrapper = Primer3Wrapper()
    
    # RAA typically requires long primers and specialized conditions
    # We pass the config as-is since Primer3Wrapper handles the mapping from preset
    raw_results = p3_wrapper.design_primers(sequence, config)

    num_returned = raw_results.get('PRIMER_LEFT_NUM_RETURNED', 0)
    logger.info(f"Primer3 returned {num_returned} sets.")

    # 3. Parse Results using RAA probe module (annotates THF)
    primers = parse_primer3_output(raw_results, config)

    # 4. Create Amplicon
    amplicons = []
    if primers and "forward" in primers and "reverse" in primers:
        fwd = primers["forward"]
        rev = primers["reverse"]
        product_size = raw_results.get('PRIMER_PAIR_0_PRODUCT_SIZE')

        amplicon = Amplicon(
            start=fwd.start,
            end=rev.start,
            length=product_size,
            sequence="N/A",  # Primer3Wrapper doesn't return full amplicon seq directly here
            gc=0.0,
            tm_forward=fwd.tm,
            tm_reverse=rev.tm
        )
        amplicons.append(amplicon)

    # 5. Run QC (using RAAQC)
    qc_engine = RAAQC(config)
    qc_result = None

    if primers and "forward" in primers and "reverse" in primers:
        fwd = primers["forward"]
        rev = primers["reverse"]
        probe = primers.get("probe")

        # RAA-specific pair QC (includes cross dimer and GC clamp checks)
        qc_result = qc_engine.evaluate_pair_extended(fwd, rev, probe)

        # Probe-specific QC
        if probe:
            probe_qc = qc_engine.evaluate_probe(probe, fwd, rev)
            qc_result.warnings.extend(probe_qc["warnings"])
            if not probe_qc["probe_tm_ok"]:
                qc_result.tm_balance_ok = False

        # Amplicon size validation
        if amplicons:
            size_qc = qc_engine.validate_amplicon_size(amplicons[0].length)
            if not size_qc["size_ok"]:
                qc_result.warnings.extend(size_qc["warnings"])

        if qc_result.warnings:
            logger.warning(f"QC Warnings: {qc_result.warnings}")

    # 6. Metadata & Result
    from primerlab import __version__
    metadata = RunMetadata(
        workflow="raa",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version=__version__,
        parameters=config.get("parameters", {})
    )

    result = WorkflowResult(
        workflow="raa",
        primers=primers,
        amplicons=amplicons,
        metadata=metadata,
        qc=qc_result,
        raw=raw_results
    )

    return result
