"""
Unit tests for v0.6.0 qPCR CLI commands.
Tests: probe-check, melt-curve, amplicon-qc
"""

import pytest
import subprocess
import json


class TestProbeCheckCLI:
    """Tests for probe-check CLI command."""
    
    def test_probe_check_basic(self):
        """Test basic probe-check command."""
        result = subprocess.run(
            ["python", "-m", "primerlab.cli.main", "probe-check",
             "--probe", "ATGCGATCGATCGATCGATCG"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "PROBE BINDING CHECK" in result.stdout
        assert "Binding Tm" in result.stdout
    
    def test_probe_check_json_output(self):
        """Test probe-check with JSON output."""
        result = subprocess.run(
            ["python", "-m", "primerlab.cli.main", "probe-check",
             "--probe", "ATGCGATCGATCGATCGATCG",
             "--format", "json"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        # Should be valid JSON
        data = json.loads(result.stdout)
        assert "tm" in data or "grade" in data
    
    def test_probe_check_with_amplicon(self):
        """Test probe-check with amplicon context."""
        result = subprocess.run(
            ["python", "-m", "primerlab.cli.main", "probe-check",
             "--probe", "ATGCGATCGATCGATCGATCG",
             "--amplicon", "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "PROBE BINDING CHECK" in result.stdout


class TestMeltCurveCLI:
    """Tests for melt-curve CLI command."""
    
    def test_melt_curve_basic(self):
        """Test basic melt-curve command."""
        result = subprocess.run(
            ["python", "-m", "primerlab.cli.main", "melt-curve",
             "--amplicon", "ATGCGATCGATCGATCGATCGATCGATCGATCG"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "MELT CURVE PREDICTION" in result.stdout
        assert "Predicted Tm" in result.stdout
    
    def test_melt_curve_json_output(self):
        """Test melt-curve with JSON output."""
        result = subprocess.run(
            ["python", "-m", "primerlab.cli.main", "melt-curve",
             "--amplicon", "ATGCGATCGATCGATCGATCGATCGATCGATCG",
             "--format", "json"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        # Should be valid JSON
        data = json.loads(result.stdout)
        assert "predicted_tm" in data


class TestAmpliconQcCLI:
    """Tests for amplicon-qc CLI command."""
    
    def test_amplicon_qc_basic(self):
        """Test basic amplicon-qc command."""
        # 97bp amplicon
        amplicon = "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
        result = subprocess.run(
            ["python", "-m", "primerlab.cli.main", "amplicon-qc",
             "--amplicon", amplicon],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "AMPLICON QC" in result.stdout
        assert "Length:" in result.stdout
        assert "GC Content:" in result.stdout
    
    def test_amplicon_qc_json_output(self):
        """Test amplicon-qc with JSON output."""
        amplicon = "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
        result = subprocess.run(
            ["python", "-m", "primerlab.cli.main", "amplicon-qc",
             "--amplicon", amplicon,
             "--format", "json"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        # Should be valid JSON
        data = json.loads(result.stdout)
        assert "amplicon_length" in data
        assert "gc_content" in data
        assert "grade" in data
    
    def test_amplicon_qc_custom_length(self):
        """Test amplicon-qc with custom length range."""
        amplicon = "ATGCGATCGATCGATCGATCGATCGATCGATCG"  # 33bp
        result = subprocess.run(
            ["python", "-m", "primerlab.cli.main", "amplicon-qc",
             "--amplicon", amplicon,
             "--min-length", "20",
             "--max-length", "50"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "Length OK:" in result.stdout


class TestPlotMeltOption:
    """Tests for --plot-melt option in run command."""
    
    def test_plot_melt_help(self):
        """Test --plot-melt appears in run help."""
        result = subprocess.run(
            ["python", "-m", "primerlab.cli.main", "run", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "--plot-melt" in result.stdout
        assert "--plot-format" in result.stdout
