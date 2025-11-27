import pytest
from primerlab.api.public import design_pcr_primers, design_qpcr_assays

def test_api_pcr(gapdh_sequence):
    """Verifies design_pcr_primers API."""
    config = {
        "parameters": {
            "product_size_range": [[100, 200]]
        }
    }
    result = design_pcr_primers(gapdh_sequence, config)
    assert result.primers is not None
    assert "forward" in result.primers

def test_api_qpcr(gapdh_sequence):
    """Verifies design_qpcr_assays API."""
    config = {
        "parameters": {
            "product_size_range": [[70, 200]],
            "probe": {"tm": {"min": 60.0, "opt": 65.0, "max": 70.0}},
            "advanced": {"timeout": 60}
        }
    }
    result = design_qpcr_assays(gapdh_sequence, config)
    assert result.primers is not None
    assert "probe" in result.primers
