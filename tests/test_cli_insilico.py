"""
CLI Integration Tests for In-silico PCR command (v0.2.0)

Tests the `primerlab insilico` command end-to-end.

Note: These tests use subprocess to call the CLI which may be flaky
in some environments (e.g., when primerlab is not installed globally).
"""

import pytest
import subprocess
import json
from pathlib import Path
import tempfile
import shutil
import os


# Path to example files
EXAMPLES_DIR = Path(__file__).parent.parent / "examples" / "insilico"
PRIMERS_JSON = EXAMPLES_DIR / "primers.json"
TEMPLATE_FASTA = EXAMPLES_DIR / "template.fasta"

# Check if primerlab is available in PATH
def is_primerlab_available():
    try:
        result = subprocess.run(["primerlab", "--version"], capture_output=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

PRIMERLAB_AVAILABLE = is_primerlab_available()


@pytest.mark.skipif(not PRIMERLAB_AVAILABLE, reason="primerlab not installed or not in PATH")
class TestInsilicoCliCommand:
    """Integration tests for primerlab insilico command."""

    def test_insilico_help(self):
        """Test that help command works."""
        result = subprocess.run(
            ["primerlab", "insilico", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "--primers" in result.stdout
        assert "--template" in result.stdout
        assert "--output" in result.stdout

    def test_insilico_missing_primers(self):
        """Test error when primers file is missing."""
        result = subprocess.run(
            ["primerlab", "insilico", "-p", "nonexistent.json", "-t", str(TEMPLATE_FASTA)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert "not found" in result.stdout.lower() or "not found" in result.stderr.lower()

    def test_insilico_missing_template(self):
        """Test error when template file is missing."""
        result = subprocess.run(
            ["primerlab", "insilico", "-p", str(PRIMERS_JSON), "-t", "nonexistent.fasta"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1

    @pytest.mark.skipif(not PRIMERS_JSON.exists(), reason="Example files not found")
    def test_insilico_with_examples(self):
        """Test insilico command with example files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [
                    "primerlab", "insilico",
                    "-p", str(PRIMERS_JSON),
                    "-t", str(TEMPLATE_FASTA),
                    "-o", tmpdir
                ],
                capture_output=True,
                text=True
            )
            
            # Check output files were created
            output_dir = Path(tmpdir)
            json_file = output_dir / "insilico_result.json"
            fasta_file = output_dir / "predicted_amplicons.fasta"
            
            assert json_file.exists(), f"JSON result not found. stdout: {result.stdout}, stderr: {result.stderr}"
            
            # Verify JSON structure
            with open(json_file) as f:
                data = json.load(f)
            
            assert "success" in data
            assert "template_name" in data
            assert "products" in data
            assert "forward_primer" in data
            assert "reverse_primer" in data

    @pytest.mark.skipif(not PRIMERS_JSON.exists(), reason="Example files not found")
    def test_insilico_json_output(self):
        """Test --json flag outputs valid JSON to stdout."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [
                    "primerlab", "insilico",
                    "-p", str(PRIMERS_JSON),
                    "-t", str(TEMPLATE_FASTA),
                    "-o", tmpdir,
                    "--json"
                ],
                capture_output=True,
                text=True
            )
            
            # Try to parse stdout as JSON
            try:
                data = json.loads(result.stdout)
                assert "success" in data
            except json.JSONDecodeError:
                pytest.fail(f"Output is not valid JSON: {result.stdout[:200]}")

    @pytest.mark.skipif(not PRIMERS_JSON.exists(), reason="Example files not found")
    def test_insilico_fasta_output(self):
        """Test that predicted amplicons FASTA is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [
                    "primerlab", "insilico",
                    "-p", str(PRIMERS_JSON),
                    "-t", str(TEMPLATE_FASTA),
                    "-o", tmpdir
                ],
                capture_output=True,
                text=True
            )
            
            fasta_file = Path(tmpdir) / "predicted_amplicons.fasta"
            
            # FASTA should exist if products were found
            json_file = Path(tmpdir) / "insilico_result.json"
            if json_file.exists():
                with open(json_file) as f:
                    data = json.load(f)
                if data.get("success") and data.get("products_count", 0) > 0:
                    assert fasta_file.exists(), "FASTA output should exist when products found"
                    
                    # Verify FASTA format
                    with open(fasta_file) as f:
                        content = f.read()
                    assert content.startswith(">"), "FASTA should start with >"
                    assert "amplicon" in content.lower()


@pytest.mark.skipif(not PRIMERLAB_AVAILABLE, reason="primerlab not installed or not in PATH")
class TestInsilicoCliEdgeCases:
    """Edge case tests for insilico CLI."""

    def test_insilico_empty_json(self):
        """Test with empty primers JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create empty JSON
            empty_json = Path(tmpdir) / "empty.json"
            empty_json.write_text('{}')
            
            result = subprocess.run(
                [
                    "primerlab", "insilico",
                    "-p", str(empty_json),
                    "-t", str(TEMPLATE_FASTA) if TEMPLATE_FASTA.exists() else "dummy.fasta"
                ],
                capture_output=True,
                text=True
            )
            
            # Should fail gracefully
            assert result.returncode != 0 or "could not parse" in result.stdout.lower()

    def test_insilico_fasta_primers(self):
        """Test with primers in FASTA format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create FASTA primers file
            fasta_primers = Path(tmpdir) / "primers.fasta"
            fasta_primers.write_text(""">Forward_primer
ATGGTGAGCAAGGGCGAGGAG
>Reverse_primer
TTACTTGTACAGCTCGTCCATGCC
""")
            
            if not TEMPLATE_FASTA.exists():
                pytest.skip("Template file not found")
            
            result = subprocess.run(
                [
                    "primerlab", "insilico",
                    "-p", str(fasta_primers),
                    "-t", str(TEMPLATE_FASTA),
                    "-o", tmpdir
                ],
                capture_output=True,
                text=True
            )
            
            # Should work with FASTA primers
            json_file = Path(tmpdir) / "insilico_result.json"
            assert json_file.exists() or result.returncode == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
