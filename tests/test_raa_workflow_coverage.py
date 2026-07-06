"""Additional unit tests with mocked components to increase coverage of RAA workflow."""

import pytest
from unittest.mock import patch, MagicMock
from primerlab.workflows.raa.workflow import run_raa_workflow
from primerlab.core.exceptions import WorkflowError
from primerlab.core.models import Primer

@pytest.fixture
def mock_p3_results():
    return {
        "PRIMER_PAIR_NUM_RETURNED": 1,
        "PRIMER_LEFT_NUM_RETURNED": 1,
        "PRIMER_LEFT_0": (10, 30),
        "PRIMER_RIGHT_0": (200, 30),
        "PRIMER_LEFT_0_SEQUENCE": "A"*30,
        "PRIMER_RIGHT_0_SEQUENCE": "T"*30,
        "PRIMER_PAIR_0_PRODUCT_SIZE": 190,
        "PRIMER_PAIR_0_PENALTY": 1.0,
        "PRIMER_LEFT_0_TM": 60.0,
        "PRIMER_LEFT_0_GC_PERCENT": 50.0,
        "PRIMER_RIGHT_0_TM": 60.0,
        "PRIMER_RIGHT_0_GC_PERCENT": 50.0,
    }

def test_raa_workflow_no_sequence():
    """Verify that RAA workflow raises an exception when no sequence is provided."""
    config = {
        "input": {},
        "parameters": {}
    }
    with pytest.raises(WorkflowError) as exc_info:
        run_raa_workflow(config)
    assert "No sequence provided" in str(exc_info.value)

def test_raa_workflow_invalid_sequence_path():
    """Verify that RAA workflow raises an exception when sequence file does not exist."""
    config = {
        "input": {
            "sequence_path": "non_existent_file_path_123.fasta"
        },
        "parameters": {}
    }
    with pytest.raises(WorkflowError) as exc_info:
        run_raa_workflow(config)
    assert "Sequence loading failed" in str(exc_info.value)

def test_raa_workflow_diversified_search(gapdh_sequence, mock_p3_results):
    """Verify RAA workflow execution with diversified search strategy using mock."""
    config = {
        "input": {
            "sequence": gapdh_sequence[:600]
        },
        "parameters": {
            "search_strategy": "diversified",
            "product_size_range": [[150, 400]],
            "num_candidates": 6,
            "probe": {
                "enabled": False
            }
        },
        "qc": {
            "vienna_ranking_limit": 1
        }
    }
    
    with patch("primerlab.workflows.raa.workflow.Primer3Wrapper") as mock_p3_class:
        mock_p3_inst = MagicMock()
        mock_p3_inst.design_primers.return_value = mock_p3_results
        mock_p3_class.return_value = mock_p3_inst
        
        result = run_raa_workflow(config)
        assert result.workflow == "raa"
        assert len(result.alternatives) > 0

def test_raa_workflow_with_probe_and_slicing(gapdh_sequence, mock_p3_results):
    """Verify RAA workflow with probe enabled and custom slicing config using mock."""
    config = {
        "input": {
            "sequence": gapdh_sequence[:500]
        },
        "parameters": {
            "probe": {
                "enabled": True,
                "type": "exo"
            },
            "num_candidates": 1
        },
        "advanced": {
            "cores": 1,
            "window_size": 300,
            "overlap": 150
        },
        "qc": {
            "vienna_ranking_limit": 1
        }
    }
    
    with patch("primerlab.workflows.raa.workflow.Primer3Wrapper") as mock_p3_class:
        mock_p3_inst = MagicMock()
        mock_p3_inst.design_primers.return_value = mock_p3_results
        mock_p3_class.return_value = mock_p3_inst
        
        result = run_raa_workflow(config)
        assert result.workflow == "raa"

def test_raa_workflow_hard_qc_filter(gapdh_sequence, mock_p3_results):
    """Verify RAA workflow with hard QC filtering active using mock."""
    config = {
        "input": {
            "sequence": gapdh_sequence[:500]
        },
        "parameters": {
            "hard_qc_filter": True,
            "num_candidates": 1,
            "probe": {
                "enabled": False
            }
        },
        "qc": {
            "vienna_ranking_limit": 1
        }
    }
    
    with patch("primerlab.workflows.raa.workflow.Primer3Wrapper") as mock_p3_class:
        mock_p3_inst = MagicMock()
        mock_p3_inst.design_primers.return_value = mock_p3_results
        mock_p3_class.return_value = mock_p3_inst
        
        result = run_raa_workflow(config)
        assert result.workflow == "raa"

def test_raa_workflow_vienna_disabled(gapdh_sequence, mock_p3_results):
    """Verify RAA workflow runs correctly when vienna ranking limit is disabled."""
    config = {
        "input": {
            "sequence": gapdh_sequence[:500]
        },
        "parameters": {
            "num_candidates": 1,
            "probe": {
                "enabled": False
            }
        },
        "qc": {
            "vienna_ranking_limit": 0
        }
    }
    
    with patch("primerlab.workflows.raa.workflow.Primer3Wrapper") as mock_p3_class:
        mock_p3_inst = MagicMock()
        mock_p3_inst.design_primers.return_value = mock_p3_results
        mock_p3_class.return_value = mock_p3_inst
        
        result = run_raa_workflow(config)
        assert result.workflow == "raa"
