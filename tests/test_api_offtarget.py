"""
Tests for Off-target Public API (v0.3.1)
"""

import pytest
from pathlib import Path

from primerlab.api.public import check_offtargets


# Test database
TEST_DB_PATH = Path(__file__).parent.parent / "examples" / "blast" / "test_db.fasta"


class TestCheckOfftargetsAPI:
    """Tests for check_offtargets() function."""
    
    @pytest.mark.skipif(not TEST_DB_PATH.exists(), reason="Test DB not found")
    def test_check_offtargets_basic(self):
        """Basic off-target check should work."""
        result = check_offtargets(
            forward_primer="ATGACCATGATTACGGATTC",
            reverse_primer="GCAACTGTTGGGAAGGGCGA",
            database=str(TEST_DB_PATH)
        )
        
        assert isinstance(result, dict)
        assert "specificity_score" in result
        assert "grade" in result
        assert "is_specific" in result
        assert "forward_offtargets" in result
        assert "reverse_offtargets" in result
    
    @pytest.mark.skipif(not TEST_DB_PATH.exists(), reason="Test DB not found")
    def test_check_offtargets_score_range(self):
        """Score should be 0-100."""
        result = check_offtargets(
            forward_primer="ATGACCATGATTACGGATTC",
            reverse_primer="GCAACTGTTGGGAAGGGCGA",
            database=str(TEST_DB_PATH)
        )
        
        assert 0 <= result["specificity_score"] <= 100
    
    @pytest.mark.skipif(not TEST_DB_PATH.exists(), reason="Test DB not found")
    def test_check_offtargets_grade(self):
        """Grade should be A-F."""
        result = check_offtargets(
            forward_primer="ATGACCATGATTACGGATTC",
            reverse_primer="GCAACTGTTGGGAAGGGCGA",
            database=str(TEST_DB_PATH)
        )
        
        assert result["grade"] in ["A", "B", "C", "D", "F"]
    
    @pytest.mark.skipif(not TEST_DB_PATH.exists(), reason="Test DB not found")
    def test_check_offtargets_with_target(self):
        """Should work with target ID."""
        result = check_offtargets(
            forward_primer="ATGACCATGATTACGGATTC",
            reverse_primer="GCAACTGTTGGGAAGGGCGA",
            database=str(TEST_DB_PATH),
            target_id="NC_000913.3_partial"
        )
        
        assert isinstance(result, dict)
        assert "details" in result
    
    @pytest.mark.skipif(not TEST_DB_PATH.exists(), reason="Test DB not found")
    def test_check_offtargets_details(self):
        """Details should include component scores."""
        result = check_offtargets(
            forward_primer="ATGACCATGATTACGGATTC",
            reverse_primer="GCAACTGTTGGGAAGGGCGA",
            database=str(TEST_DB_PATH)
        )
        
        details = result.get("details", {})
        assert "forward_score" in details
        assert "reverse_score" in details
