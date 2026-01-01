"""
Unit tests for Batch Comparison analysis.
"""

import pytest
import json
import tempfile
from pathlib import Path
from primerlab.core.analysis.batch_compare import (
    BatchComparator,
    DesignRunSummary,
    ComparisonResult,
    compare_batch,
)


# Sample result data
SAMPLE_RESULT_1 = {
    "workflow": "pcr",
    "primers": {
        "forward": {"sequence": "ATGCATGCATGCATGC", "tm": 60.0},
        "reverse": {"sequence": "GCATGCATGCATGCAT", "tm": 59.5},
    },
    "amplicons": [{"length": 250}],
    "qc": {"quality_score": 85, "quality_category": "B"},
}

SAMPLE_RESULT_2 = {
    "workflow": "pcr",
    "primers": {
        "forward": {"sequence": "CTGACTGACTGACTGA", "tm": 58.0},
        "reverse": {"sequence": "AGTCAGTCAGTCAGTC", "tm": 57.5},
    },
    "amplicons": [{"length": 300}],
    "qc": {"quality_score": 72, "quality_category": "C"},
}


class TestDesignRunSummary:
    """Tests for DesignRunSummary model."""
    
    def test_creation(self):
        """Test DesignRunSummary creation."""
        summary = DesignRunSummary(
            name="run1",
            path="/path/to/result.json",
            workflow="pcr",
            success=True,
            quality_score=85,
        )
        
        assert summary.name == "run1"
        assert summary.success is True
        assert summary.quality_score == 85
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        summary = DesignRunSummary(
            name="run1",
            path="/path",
            workflow="pcr",
            success=True,
        )
        
        d = summary.to_dict()
        assert d["name"] == "run1"
        assert d["workflow"] == "pcr"


class TestComparisonResult:
    """Tests for ComparisonResult model."""
    
    def test_creation(self):
        """Test ComparisonResult creation."""
        result = ComparisonResult(
            best_run="run1",
            avg_quality=80.0,
            success_rate=100.0,
        )
        
        assert result.best_run == "run1"
        assert result.avg_quality == 80.0
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        result = ComparisonResult(success_rate=75.0)
        d = result.to_dict()
        assert d["success_rate"] == 75.0


class TestBatchComparator:
    """Tests for BatchComparator."""
    
    def test_comparator_creation(self):
        """Test comparator creation."""
        comparator = BatchComparator()
        assert comparator.config == {}
    
    def test_compare_single_file(self):
        """Test comparison with single file."""
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(SAMPLE_RESULT_1, f)
            temp_path = f.name
        
        try:
            comparator = BatchComparator()
            result = comparator.compare([temp_path])
            
            assert isinstance(result, ComparisonResult)
            assert len(result.runs) == 1
        finally:
            Path(temp_path).unlink()
    
    def test_compare_multiple_files(self):
        """Test comparison with multiple files."""
        temp_files = []
        
        try:
            for data in [SAMPLE_RESULT_1, SAMPLE_RESULT_2]:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(data, f)
                    temp_files.append(f.name)
            
            comparator = BatchComparator()
            result = comparator.compare(temp_files)
            
            assert len(result.runs) == 2
            assert result.success_rate == 100.0
            assert result.avg_quality == (85 + 72) / 2
        finally:
            for f in temp_files:
                Path(f).unlink()
    
    def test_find_differences(self):
        """Test difference detection."""
        temp_files = []
        
        try:
            for data in [SAMPLE_RESULT_1, SAMPLE_RESULT_2]:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(data, f)
                    temp_files.append(f.name)
            
            comparator = BatchComparator()
            result = comparator.compare(temp_files)
            
            # Should detect quality variance (85 - 72 = 13 > 10)
            quality_diffs = [d for d in result.differences if d["type"] == "quality_variance"]
            assert len(quality_diffs) >= 1
        finally:
            for f in temp_files:
                Path(f).unlink()


class TestCompareBatch:
    """Tests for compare_batch function."""
    
    def test_function_call(self):
        """Test function call."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(SAMPLE_RESULT_1, f)
            temp_path = f.name
        
        try:
            result = compare_batch([temp_path])
            assert isinstance(result, ComparisonResult)
        finally:
            Path(temp_path).unlink()
