from typing import Dict, Any
from datetime import datetime, timezone
from primerlab.core.models import WorkflowResult, Primer, Amplicon, QCResult, RunMetadata
from primerlab.core.tools.primer3_wrapper import Primer3Wrapper
from primerlab.core.logger import get_logger
from primerlab.core.exceptions import WorkflowError

logger = get_logger()

def run_pcr_workflow(config: Dict[str, Any]) -> WorkflowResult:
    """
    Executes the PCR workflow.
    """
    logger.info("Starting PCR Workflow execution...")
    
    # 1. Parse Input
    input_config = config.get("input", {})
    raw_sequence = input_config.get("sequence")
    seq_path = input_config.get("sequence_path")
    
    from primerlab.core.sequence import SequenceLoader
    
    try:
        if seq_path:
            sequence = SequenceLoader.load(seq_path)
        elif raw_sequence:
            sequence = SequenceLoader.load(raw_sequence)
        else:
            raise WorkflowError("No sequence provided in input (sequence or sequence_path).", "ERR_WORKFLOW_001")
    except Exception as e:
        raise WorkflowError(f"Sequence loading failed: {e}", "ERR_WORKFLOW_SEQ")
    
    logger.info(f"Input sequence length: {len(sequence)} bp")

    # 2. Run Primer3
    p3_wrapper = Primer3Wrapper()
    raw_results = p3_wrapper.design_primers(sequence, config)
    
    num_returned = raw_results.get('PRIMER_LEFT_NUM_RETURNED', 0)
    logger.info(f"Primer3 returned {num_returned} pairs.")

    # 3. Parse Results into Data Models
    primers = {}
    amplicons = []
    
    # We'll just take the best pair (index 0) for this milestone
    if num_returned > 0:
        # Forward Primer
        fwd_seq = raw_results.get('PRIMER_LEFT_0_SEQUENCE')
        fwd_tm = raw_results.get('PRIMER_LEFT_0_TM')
        fwd_gc = raw_results.get('PRIMER_LEFT_0_GC_PERCENT')
        fwd_start, fwd_len = raw_results.get('PRIMER_LEFT_0') # tuple (start, len)
        
        fwd_primer = Primer(
            id="forward_0",
            sequence=fwd_seq,
            tm=fwd_tm,
            gc=fwd_gc,
            length=fwd_len,
            start=fwd_start,
            end=fwd_start + fwd_len - 1, # 0-based inclusive
            hairpin_dg=raw_results.get('PRIMER_LEFT_0_HAIRPIN_TH', 0.0),
            homodimer_dg=raw_results.get('PRIMER_LEFT_0_HOMODIMER_TH', 0.0),
            raw={"p3_index": 0}
        )
        primers["forward"] = fwd_primer

        # Reverse Primer
        rev_seq = raw_results.get('PRIMER_RIGHT_0_SEQUENCE')
        rev_tm = raw_results.get('PRIMER_RIGHT_0_TM')
        rev_gc = raw_results.get('PRIMER_RIGHT_0_GC_PERCENT')
        rev_start, rev_len = raw_results.get('PRIMER_RIGHT_0')
        
        rev_primer = Primer(
            id="reverse_0",
            sequence=rev_seq,
            tm=rev_tm,
            gc=rev_gc,
            length=rev_len,
            start=rev_start - rev_len + 1, # 5' end on template
            end=rev_start, # 3' end on template (Primer3 returns this as index)
            hairpin_dg=raw_results.get('PRIMER_RIGHT_0_HAIRPIN_TH', 0.0),
            homodimer_dg=raw_results.get('PRIMER_RIGHT_0_HOMODIMER_TH', 0.0),
            raw={"p3_index": 0}
        )
        primers["reverse"] = rev_primer

        # Amplicon
        product_size = raw_results.get('PRIMER_PAIR_0_PRODUCT_SIZE')
        amplicon = Amplicon(
            start=fwd_start,
            end=rev_start, # Simplified
            length=product_size,
            sequence="N/A", # TODO: Extract subsequence
            gc=0.0, # TODO: Calculate GC
            tm_forward=fwd_tm,
            tm_reverse=rev_tm
        )
        amplicons.append(amplicon)

    # 4. Run QC
    from primerlab.workflows.pcr.qc import PCRQC
    qc_engine = PCRQC(config)
    
    qc_result = None
    if primers:
        qc_result = qc_engine.evaluate_pair(primers["forward"], primers["reverse"])
        
        # Add QC warnings to main result warnings
        if qc_result.warnings:
            logger.warning(f"QC Warnings: {qc_result.warnings}")

    # 5. Create Metadata
    metadata = RunMetadata(
        workflow="pcr",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="0.1.0",
        parameters=config.get("parameters", {})
    )

    # 6. Create Result
    result = WorkflowResult(
        workflow="pcr",
        primers=primers,
        amplicons=amplicons,
        metadata=metadata,
        qc=qc_result,
        raw=raw_results
    )
    
    return result
