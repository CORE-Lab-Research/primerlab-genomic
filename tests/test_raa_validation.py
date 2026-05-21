"""Tests for RAA In-Silico Validation (v1.2.0)."""

import pytest
import subprocess
import sys
import json
import yaml
from pathlib import Path
from primerlab.api import design_raa_assays
from primerlab.workflows.raa.workflow import run_raa_workflow

def test_design_raa_assays_without_validation(gapdh_sequence):
    """Test design_raa_assays API without running in-silico validation."""
    fast_config = {
        "parameters": {
            "num_candidates": 5,
        },
        "qc": {
            "vienna_ranking_limit": 1
        }
    }
    result = design_raa_assays(
        sequence=gapdh_sequence,
        config=fast_config,
        validate=False
    )
    assert result.workflow == "raa"
    assert result.primers is not None
    assert result.insilico_validation is None

def test_design_raa_assays_with_validation(gapdh_sequence):
    """Test design_raa_assays API with in-silico validation enabled."""
    fast_config = {
        "parameters": {
            "num_candidates": 5,
        },
        "qc": {
            "vienna_ranking_limit": 1
        }
    }
    result = design_raa_assays(
        sequence=gapdh_sequence,
        config=fast_config,
        validate=True
    )
    assert result.workflow == "raa"
    assert result.primers is not None
    assert result.insilico_validation is not None
    assert "success" in result.insilico_validation
    assert "products_count" in result.insilico_validation

def test_cli_raa_validate(gapdh_sequence, tmp_path):
    """Test CLI primerlab raa --validate command."""
    fasta_path = tmp_path / "gapdh.fasta"
    fasta_path.write_text(f">GAPDH\n{gapdh_sequence}\n")
    
    # Load default RAA config and override candidate limit for speed
    default_config_path = Path("primerlab/config/raa_default.yaml")
    with open(default_config_path, "r") as f:
        config_data = yaml.safe_load(f)
        
    config_data["parameters"]["num_candidates"] = 5
    config_data["qc"]["vienna_ranking_limit"] = 1
    
    config_path = tmp_path / "fast_config.yaml"
    with open(config_path, "w") as f:
        yaml.safe_dump(config_data, f)
        
    out_dir = tmp_path / "raa_out"
    
    result = subprocess.run(
        [
            sys.executable, "-m", "primerlab.cli.main", "raa",
            "-sp", str(fasta_path),
            "-c", str(config_path),
            "-o", str(out_dir),
            "--validate"
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    assert result.returncode == 0
    assert "IN-SILICO VALIDATION" in result.stdout
    
    # Check that output files exist
    assert (out_dir / "summary.json").exists()
    assert (out_dir / "insilico_validation.json").exists()
    
    with open(out_dir / "summary.json") as f:
        summary = json.load(f)
    assert "insilico_validation" in summary

def test_cli_insilico_mode_raa(gapdh_sequence, tmp_path):
    """Test CLI primerlab insilico --mode raa command."""
    # Write template
    template_path = tmp_path / "gapdh.fasta"
    template_path.write_text(f">GAPDH\n{gapdh_sequence}\n")
    
    # Write primers JSON (designed to amplify a 272bp product)
    primers_data = {
        "forward": "GGGGCTCTCTGCTCCTCCCT",
        "reverse": "CTTCTCCTCAGGAGTCAGGT"
    }
    primers_path = tmp_path / "primers.json"
    with open(primers_path, "w") as f:
        json.dump(primers_data, f)
        
    out_dir = tmp_path / "insilico_out"
    
    result = subprocess.run(
        [
            sys.executable, "-m", "primerlab.cli.main", "insilico",
            "-p", str(primers_path),
            "-t", str(template_path),
            "-o", str(out_dir),
            "--mode", "raa"
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    assert result.returncode == 0
    assert "Applying isothermal RAA parameters" in result.stdout or "Applying isothermal RAA parameters" in result.stderr
    assert "Predicted 1 products" in result.stdout or "PREDICTED PRODUCTS: 1" in result.stdout
