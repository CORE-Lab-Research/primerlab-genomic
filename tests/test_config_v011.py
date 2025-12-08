import pytest
from primerlab.core.config_loader import _process_enhancements
from primerlab.workflows.qpcr.workflow import run_qpcr_workflow
from unittest.mock import MagicMock, patch

def test_product_size_conversion():
    """Verify product_size (min/opt/max) converts to product_size_range."""
    config = {
        "parameters": {
            "product_size": {"min": 200, "opt": 400, "max": 600}
        }
    }
    processed = _process_enhancements(config)
    p_range = processed["parameters"].get("product_size_range")
    
    assert p_range is not None
    assert p_range == [[200, 600]]

def test_preset_loading():
    """Verify preset loading logic from YAML file."""
    config = {
        "preset": "long_range",
        "parameters": {}
    }
    processed = _process_enhancements(config)
    params = processed["parameters"]
    
    # long_range_default.yaml has tm.min: 62.0
    assert params["tm"]["min"] == 62.0
    # long_range_default.yaml has product_size_range: "3000-10000"
    assert params["product_size_range"] == "3000-10000"

def test_qpcr_mode_sybr():
    """Verify SYBR mode disables probe design."""
    # Mock Primer3Wrapper to avoid actual execution
    with patch("primerlab.workflows.qpcr.workflow.Primer3Wrapper") as MockWrapper:
        mock_instance = MockWrapper.return_value
        # Mock return value to avoid parsing errors
        mock_instance.design_primers.return_value = {
            "PRIMER_LEFT_NUM_RETURNED": 0,
            "PRIMER_PAIR_NUM_RETURNED": 0
        }
        
        config = {
            "workflow": "qpcr",
            "input": {"sequence": "ATGC" * 50},
            "parameters": {
                "mode": "sybr",
                "probe": {"size": {"min": 20}} # Should be removed
            },
            "output": {"directory": "test_out"}
        }
        
        # We need to mock SequenceLoader too since we pass raw sequence
        with patch("primerlab.workflows.qpcr.workflow.SequenceLoader") as MockLoader:
            MockLoader.load.return_value = "ATGC" * 50
            
            run_qpcr_workflow(config)
            
            # Check if probe config was removed from the config passed to design_primers
            call_args = mock_instance.design_primers.call_args
            passed_config = call_args[0][1] # 2nd arg is config
            
            assert "probe" not in passed_config["parameters"]

def test_qpcr_mode_taqman():
    """Verify TaqMan mode keeps probe design."""
    with patch("primerlab.workflows.qpcr.workflow.Primer3Wrapper") as MockWrapper:
        mock_instance = MockWrapper.return_value
        mock_instance.design_primers.return_value = {
            "PRIMER_LEFT_NUM_RETURNED": 0,
            "PRIMER_PAIR_NUM_RETURNED": 0
        }
        
        config = {
            "workflow": "qpcr",
            "input": {"sequence": "ATGC" * 50},
            "parameters": {
                "mode": "taqman",
                "probe": {"size": {"min": 20}} # Should stay
            },
            "output": {"directory": "test_out"}
        }
        
        with patch("primerlab.workflows.qpcr.workflow.SequenceLoader") as MockLoader:
            MockLoader.load.return_value = "ATGC" * 50
            
            run_qpcr_workflow(config)
            
            call_args = mock_instance.design_primers.call_args
            passed_config = call_args[0][1]
            
            assert "probe" in passed_config["parameters"]
