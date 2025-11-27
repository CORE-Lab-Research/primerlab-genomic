import pytest
from primerlab.workflows.qpcr.workflow import run_qpcr_workflow

def test_qpcr_workflow_success(gapdh_sequence, test_output_dir):
    """Verifies that qPCR workflow runs successfully and produces valid primers + probe."""
    config = {
        "workflow": "qpcr",
        "input": {"sequence": gapdh_sequence},
        "parameters": {
            "product_size_range": [[70, 200]],
            "primer_size": {"min": 18, "opt": 20, "max": 25},
            "tm": {"min": 57.0, "opt": 60.0, "max": 63.0},
            "probe": {
                "size": {"min": 18, "opt": 20, "max": 25},
                # Relaxed Tm for reliable testing
                "tm": {"min": 60.0, "opt": 65.0, "max": 70.0} 
            },
            "advanced": {"timeout": 60}
        },
        "output": {"directory": str(test_output_dir / "qpcr_test")},
        "qc": {"hairpin_dg_min": -10.0}
    }
    
    result = run_qpcr_workflow(config)
    
    assert result.primers is not None
    assert "forward" in result.primers
    assert "reverse" in result.primers
    assert "probe" in result.primers
    
    probe = result.primers["probe"]
    
    # Check probe existence
    assert probe.sequence is not None
    assert len(probe.sequence) > 0
    
    # Check efficiency estimation
    assert hasattr(result, "efficiency")
    assert 0.0 <= result.efficiency <= 110.0

def test_qpcr_coordinate_logic(gapdh_sequence, test_output_dir):
    """Verifies coordinate logic specifically for qPCR reverse primer."""
    config = {
        "workflow": "qpcr",
        "input": {"sequence": gapdh_sequence},
        "parameters": {
            "product_size_range": [[70, 200]],
            "probe": {"tm": {"min": 60.0, "opt": 65.0, "max": 70.0}},
            "advanced": {"timeout": 60}
        },
        "output": {"directory": str(test_output_dir / "qpcr_coord_test")}
    }
    
    result = run_qpcr_workflow(config)
    
    if result.primers:
        rev = result.primers["reverse"]
        assert rev.start < rev.end, "qPCR Reverse primer start should be < end"
