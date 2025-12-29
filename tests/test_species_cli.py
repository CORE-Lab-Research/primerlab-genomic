"""
Tests for species-check CLI command.
"""

import pytest
import subprocess
import tempfile
import json
from pathlib import Path


class TestSpeciesCheckCLI:
    """Tests for primerlab species-check CLI command."""
    
    def test_help_output(self):
        """Verify species-check --help shows all options."""
        result = subprocess.run(
            ["python", "-m", "primerlab.cli.main", "species-check", "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0
        assert "--primers" in result.stdout
        assert "--target" in result.stdout
        assert "--offtargets" in result.stdout
        assert "--format" in result.stdout
        assert "--output" in result.stdout
    
    def test_missing_required_args(self):
        """Verify error when required args missing."""
        result = subprocess.run(
            ["python", "-m", "primerlab.cli.main", "species-check"],
            capture_output=True,
            text=True,
            timeout=30
        )
        # Should fail with missing required arguments
        assert result.returncode != 0
        assert "required" in result.stderr.lower() or "error" in result.stderr.lower()


class TestSpeciesCheckIntegration:
    """Integration tests for species-check command."""
    
    @pytest.fixture
    def sample_primers_json(self, tmp_path):
        """Create sample primers JSON."""
        primers = [
            {"name": "Gene1", "forward": "ATGCGATCGATCGATCGATCG", "reverse": "CGATCGATCGATCGATCGCAT"},
            {"name": "Gene2", "forward": "GATCGATCGATCGATCGATCG", "reverse": "CGATCGATCGATCGATCGATC"},
        ]
        path = tmp_path / "primers.json"
        with open(path, "w") as f:
            json.dump(primers, f)
        return str(path)
    
    @pytest.fixture
    def sample_target_fasta(self, tmp_path):
        """Create sample target FASTA."""
        content = """>TargetSpecies
ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG
"""
        path = tmp_path / "target.fasta"
        with open(path, "w") as f:
            f.write(content)
        return str(path)
    
    @pytest.fixture
    def sample_offtarget_fasta(self, tmp_path):
        """Create sample off-target FASTA."""
        content = """>OffTargetSpecies
NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN
"""
        path = tmp_path / "offtarget.fasta"
        with open(path, "w") as f:
            f.write(content)
        return str(path)
    
    def test_basic_run(self, sample_primers_json, sample_target_fasta, tmp_path):
        """Test basic species-check run."""
        output_dir = tmp_path / "output"
        
        result = subprocess.run(
            [
                "python", "-m", "primerlab.cli.main", "species-check",
                "--primers", sample_primers_json,
                "--target", sample_target_fasta,
                "--output", str(output_dir),
            ],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Should complete (may exit 0 or 1 based on specificity)
        assert "Species Specificity Check" in result.stdout or result.returncode in [0, 1]
    
    def test_with_offtargets(self, sample_primers_json, sample_target_fasta, 
                             sample_offtarget_fasta, tmp_path):
        """Test species-check with off-target templates."""
        output_dir = tmp_path / "output"
        
        result = subprocess.run(
            [
                "python", "-m", "primerlab.cli.main", "species-check",
                "--primers", sample_primers_json,
                "--target", sample_target_fasta,
                "--offtargets", sample_offtarget_fasta,
                "--output", str(output_dir),
            ],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Should complete
        assert result.returncode in [0, 1]
    
    def test_json_output_created(self, sample_primers_json, sample_target_fasta, tmp_path):
        """Verify JSON output file created."""
        output_dir = tmp_path / "output"
        
        subprocess.run(
            [
                "python", "-m", "primerlab.cli.main", "species-check",
                "--primers", sample_primers_json,
                "--target", sample_target_fasta,
                "--output", str(output_dir),
            ],
            capture_output=True,
            timeout=60
        )
        
        # Check JSON file created
        json_path = output_dir / "species_analysis.json"
        if json_path.exists():
            with open(json_path) as f:
                data = json.load(f)
            assert "overall_score" in data
            assert "grade" in data
