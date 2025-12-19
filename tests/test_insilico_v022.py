"""
Tests for v0.2.2 features: In-silico Reporting & UX
"""

import pytest
from pathlib import Path
import tempfile

from primerlab.core.insilico.engine import run_insilico_pcr
from primerlab.core.insilico.report import (
    generate_markdown_report,
    generate_amplicon_fasta,
    format_console_alignment
)


# Test template and primers
TEMPLATE_SEQ = (
    "ATGAGTAAAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGAATTAGATGGTGATGTTAATGGGCACA"
    "AATTTTCTGTCAGTGGAGAGGGTGAAGGTGATGCAACATACGGAAAACTTACCCTTAAATTTATTTGCACTACTGG"
    "AAAACTACCTGTTCCATGGCCAACACTTGTCACTACTTTCTCTTATGGTGTTCAATGCTTTTCCCGTTATCCGGAT"
)
FORWARD_PRIMER = "ATGAGTAAAGGAGAAGAACTTTTC"
REVERSE_PRIMER = "ATCCGGATAACGGGAAAAGCATTG"


@pytest.fixture
def insilico_result():
    """Generate a sample in-silico PCR result."""
    return run_insilico_pcr(
        template=TEMPLATE_SEQ,
        forward_primer=FORWARD_PRIMER,
        reverse_primer=REVERSE_PRIMER,
        template_name="GFP_test"
    )


class TestMarkdownReport:
    """Tests for markdown report generation."""
    
    def test_generate_markdown_report_returns_string(self, insilico_result):
        """Should return a markdown string."""
        report = generate_markdown_report(insilico_result)
        assert isinstance(report, str)
        assert len(report) > 0
    
    def test_markdown_contains_header(self, insilico_result):
        """Report should contain main header."""
        report = generate_markdown_report(insilico_result)
        assert "# In-silico PCR Report" in report
    
    def test_markdown_contains_summary(self, insilico_result):
        """Report should contain summary section."""
        report = generate_markdown_report(insilico_result)
        assert "## Summary" in report
        assert "GFP_test" in report
    
    def test_markdown_contains_products(self, insilico_result):
        """Report should list products if present."""
        report = generate_markdown_report(insilico_result)
        if insilico_result.products:
            assert "## Predicted Products" in report
    
    def test_markdown_saves_to_file(self, insilico_result):
        """Should save to file when output_dir provided."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            generate_markdown_report(insilico_result, output_dir)
            
            report_path = output_dir / "insilico_report.md"
            assert report_path.exists()
            
            content = report_path.read_text()
            assert "# In-silico PCR Report" in content


class TestAmpliconFasta:
    """Tests for amplicon FASTA export."""
    
    def test_generate_fasta_returns_string(self, insilico_result):
        """Should return a FASTA string."""
        fasta = generate_amplicon_fasta(insilico_result)
        assert isinstance(fasta, str)
    
    def test_fasta_contains_headers_if_products(self, insilico_result):
        """FASTA should contain headers for each product."""
        if insilico_result.products:
            fasta = generate_amplicon_fasta(insilico_result)
            assert fasta.startswith(">")
            assert "GFP_test" in fasta
    
    def test_fasta_header_format(self, insilico_result):
        """FASTA headers should contain product info."""
        if insilico_result.products:
            fasta = generate_amplicon_fasta(insilico_result)
            assert "size=" in fasta
            assert "pos=" in fasta
            assert "likelihood=" in fasta
    
    def test_fasta_saves_to_file(self, insilico_result):
        """Should save to file when output_dir provided."""
        if insilico_result.products:
            with tempfile.TemporaryDirectory() as tmpdir:
                output_dir = Path(tmpdir)
                generate_amplicon_fasta(insilico_result, output_dir)
                
                fasta_path = output_dir / "predicted_amplicons.fasta"
                assert fasta_path.exists()


class TestConsoleAlignment:
    """Tests for console alignment formatting."""
    
    def test_format_console_returns_string(self, insilico_result):
        """Should return a formatted string."""
        output = format_console_alignment(insilico_result)
        assert isinstance(output, str)
        assert len(output) > 0
    
    def test_console_contains_header(self, insilico_result):
        """Output should contain header."""
        output = format_console_alignment(insilico_result)
        assert "IN-SILICO PCR RESULTS" in output
    
    def test_console_contains_template_info(self, insilico_result):
        """Output should show template information."""
        output = format_console_alignment(insilico_result)
        assert "GFP_test" in output
    
    def test_console_shows_products(self, insilico_result):
        """Output should list products if present."""
        output = format_console_alignment(insilico_result)
        if insilico_result.products:
            assert "PREDICTED PRODUCTS" in output
