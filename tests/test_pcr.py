import pytest
from primerlab.workflows.pcr.workflow import run_pcr_workflow

def test_pcr_workflow_success(gapdh_sequence, test_output_dir):
    """Verifies that PCR workflow runs successfully and produces valid primers."""
    config = {
        "workflow": "pcr",
        "input": {"sequence": gapdh_sequence},
        "parameters": {
            "product_size_range": [[100, 300]],
            "primer_size": {"min": 18, "opt": 20, "max": 25},
            "tm": {"min": 57.0, "opt": 60.0, "max": 63.0}
        },
        "output": {"directory": str(test_output_dir / "pcr_test")},
        "qc": {"hairpin_dg_min": -10.0}
    }
    
    result = run_pcr_workflow(config)
    
    assert result.primers is not None
    assert "forward" in result.primers
    assert "reverse" in result.primers
    
    fwd = result.primers["forward"]
    rev = result.primers["reverse"]
    
    # Check coordinates logic (Critical Bug Fix Verification)
    assert fwd.start < fwd.end, "Forward primer start should be < end"
    assert rev.start < rev.end, "Reverse primer start should be < end (Fix Verification)"
    
    # Check sequence length
    assert 18 <= len(fwd.sequence) <= 25
    assert 18 <= len(rev.sequence) <= 25

def test_pcr_workflow_no_primers():
    """Verifies handling of impossible constraints - should raise ToolExecutionError."""
    from primerlab.core.exceptions import ToolExecutionError
    
    config = {
        "workflow": "pcr",
        "input": {"sequence": "ATGC" * 20}, # Short repetitive sequence
        "parameters": {
            "tm": {"min": 80.0, "opt": 85.0, "max": 90.0} # Impossible Tm
        },
        "output": {"directory": "dummy"}
    }
    
    # v0.1.2: Error handling now raises ToolExecutionError with detailed message
    with pytest.raises(ToolExecutionError) as exc_info:
        run_pcr_workflow(config)
    
    # Verify error contains helpful information
    assert "Primer3 failed to find any primers" in str(exc_info.value)
    assert "ERR_TOOL_P3_NO_PRIMERS" == exc_info.value.error_code
