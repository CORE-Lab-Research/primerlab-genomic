"""
Tests for Batch Summary Module (v0.1.5)
"""

import pytest
from primerlab.core.batch_summary import (
    generate_batch_summary,
    format_batch_summary_cli
)


# Sample result data
SAMPLE_SUCCESS_RESULT = {
    "workflow": "pcr",
    "metadata": {"sequence_name": "GAPDH"},
    "primers": {
        "forward": {
            "id": "GAPDH_F1",
            "sequence": "ATGCGTACGATCGATCG",
            "tm": 60.5,
            "gc": 52.0
        },
        "reverse": {
            "id": "GAPDH_R1",
            "sequence": "TCGATCGATCGTAGCAT",
            "tm": 59.8,
            "gc": 48.0
        }
    },
    "amplicons": [{"length": 200}],
    "qc": {"quality_score": 85}
}

SAMPLE_FAIL_RESULT = {
    "workflow": "pcr",
    "metadata": {"sequence_name": "TP53_fail"},
    "primers": {},
    "amplicons": [],
    "qc": {},
    "error": "No primers found"
}


class TestGenerateBatchSummary:
    """Tests for batch summary generation."""
    
    def test_counts_total(self):
        """Should count total sequences."""
        results = [SAMPLE_SUCCESS_RESULT, SAMPLE_FAIL_RESULT]
        summary = generate_batch_summary(results)
        assert summary["total_sequences"] == 2
    
    def test_counts_successful(self):
        """Should count successful runs."""
        results = [SAMPLE_SUCCESS_RESULT, SAMPLE_SUCCESS_RESULT]
        summary = generate_batch_summary(results)
        assert summary["successful"] == 2
        assert summary["failed"] == 0
    
    def test_counts_failed(self):
        """Should count failed runs."""
        results = [SAMPLE_FAIL_RESULT, SAMPLE_FAIL_RESULT]
        summary = generate_batch_summary(results)
        assert summary["successful"] == 0
        assert summary["failed"] == 2
    
    def test_calculates_success_rate(self):
        """Should calculate success rate."""
        results = [SAMPLE_SUCCESS_RESULT, SAMPLE_FAIL_RESULT]
        summary = generate_batch_summary(results)
        assert summary["success_rate"] == 50.0
    
    def test_calculates_avg_quality(self):
        """Should calculate average quality score."""
        results = [SAMPLE_SUCCESS_RESULT, SAMPLE_SUCCESS_RESULT]
        summary = generate_batch_summary(results)
        assert summary["avg_quality_score"] == 85.0
    
    def test_generates_summary_table(self):
        """Should generate summary table."""
        results = [SAMPLE_SUCCESS_RESULT]
        summary = generate_batch_summary(results)
        assert len(summary["summary_table"]) == 1
        
        row = summary["summary_table"][0]
        assert row["name"] == "GAPDH"
        assert "Success" in row["status"]
        assert row["fwd_tm"] == 60.5
        assert row["product_size"] == 200
    
    def test_handles_empty_results(self):
        """Should handle empty results list."""
        summary = generate_batch_summary([])
        assert summary["total_sequences"] == 0
        assert summary["success_rate"] == 0


class TestFormatBatchSummaryCLI:
    """Tests for CLI formatting."""
    
    def test_formats_without_error(self):
        """Should format summary for CLI."""
        results = [SAMPLE_SUCCESS_RESULT, SAMPLE_FAIL_RESULT]
        summary = generate_batch_summary(results)
        output = format_batch_summary_cli(summary)
        
        assert "BATCH RUN SUMMARY" in output
        assert "Total Sequences: 2" in output
        assert "GAPDH" in output
    
    def test_shows_success_rate(self):
        """Should show success rate."""
        results = [SAMPLE_SUCCESS_RESULT]
        summary = generate_batch_summary(results)
        output = format_batch_summary_cli(summary)
        
        assert "Success Rate: 100.0%" in output
