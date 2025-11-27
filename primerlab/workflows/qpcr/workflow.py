from typing import Dict, Any
from datetime import datetime, timezone
from primerlab.core.models import WorkflowResult, Amplicon, RunMetadata
from primerlab.core.tools.primer3_wrapper import Primer3Wrapper
from primerlab.core.sequence import SequenceLoader
from primerlab.core.logger import get_logger
from primerlab.core.exceptions import WorkflowError
from primerlab.workflows.qpcr.qc import qPCRQC
from primerlab.workflows.qpcr.design import parse_primer3_output
from primerlab.workflows.qpcr.report import qPCRReportGenerator

logger = get_logger()

def run_qpcr_workflow(config: Dict[str, Any]) -> WorkflowResult:
    """
    Executes the qPCR workflow (Primers + Probe).
    """
    logger.info("Starting qPCR Workflow execution...")
    
    # 1. Parse Input
    input_config = config.get("input", {})
    raw_sequence = input_config.get("sequence")
    seq_path = input_config.get("sequence_path")
    
    try:
        if seq_path:
            sequence = SequenceLoader.load(seq_path)
        elif raw_sequence:
            sequence = SequenceLoader.load(raw_sequence)
        else:
            raise WorkflowError("No sequence provided.", "ERR_WORKFLOW_001")
    except Exception as e:
        raise WorkflowError(f"Sequence loading failed: {e}", "ERR_WORKFLOW_SEQ")

    logger.info(f"Input sequence length: {len(sequence)} bp")

    # 2. Run Primer3 (with Probe settings)
    p3_wrapper = Primer3Wrapper()
    raw_results = p3_wrapper.design_primers(sequence, config)
    
    num_returned = raw_results.get('PRIMER_LEFT_NUM_RETURNED', 0)
    logger.info(f"Primer3 returned {num_returned} sets.")

    # 3. Parse Results using design module
    primers = parse_primer3_output(raw_results)
    
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
            sequence="N/A",
            gc=0.0,
            tm_forward=fwd.tm,
            tm_reverse=rev.tm
        )
        amplicons.append(amplicon)

    # 5. Run QC (using qPCRQC)
    qc_engine = qPCRQC(config)
    qc_result = None
    efficiency = None
    
    if primers and "forward" in primers and "reverse" in primers:
        fwd = primers["forward"]
        rev = primers["reverse"]
        
        # Standard primer pair QC
        qc_result = qc_engine.evaluate_pair(fwd, rev)
        
        # Probe-specific QC
        if "probe" in primers:
            probe = primers["probe"]
            probe_qc = qc_engine.evaluate_probe(probe, fwd, rev)
            
            # Merge probe warnings into main QC result
            qc_result.warnings.extend(probe_qc["warnings"])
            if not probe_qc["probe_tm_ok"]:
                qc_result.tm_balance_ok = False
        
        # Amplicon size validation
        if amplicons:
            size_qc = qc_engine.validate_amplicon_size(amplicons[0].length)
            if not size_qc["size_ok"]:
                qc_result.warnings.extend(size_qc["warnings"])
        
        # Estimate efficiency
        probe = primers.get("probe")
        efficiency = qc_engine.estimate_efficiency(fwd, rev, probe)
        
        if qc_result.warnings:
            logger.warning(f"QC Warnings: {qc_result.warnings}")

    # 6. Metadata & Result
    metadata = RunMetadata(
        workflow="qpcr",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="0.1.0",
        parameters=config.get("parameters", {})
    )

    result = WorkflowResult(
        workflow="qpcr",
        primers=primers,
        amplicons=amplicons,
        metadata=metadata,
        qc=qc_result,
        raw=raw_results
    )
    
    # Add efficiency as custom attribute
    result.efficiency = efficiency
    
    return result
