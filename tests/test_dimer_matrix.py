"""
Unit tests for Dimer Matrix analysis.
"""

import pytest
from primerlab.core.analysis.dimer_matrix import (
    DimerMatrixAnalyzer,
    DimerResult,
    DimerMatrixResult,
    analyze_dimer_matrix,
)


class TestDimerResult:
    """Tests for DimerResult model."""
    
    def test_creation(self):
        """Test DimerResult creation."""
        result = DimerResult(
            primer1_name="FWD1",
            primer2_name="REV1",
            primer1_seq="ATGCATGCATGCATGC",
            primer2_seq="GCATGCATGCATGCAT",
            dg=-5.5,
            tm=45.0,
            structure="...",
            is_problematic=False,
        )
        
        assert result.primer1_name == "FWD1"
        assert result.dg == -5.5
        assert result.is_problematic is False
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        result = DimerResult(
            primer1_name="FWD1",
            primer2_name="REV1",
            primer1_seq="ATGC",
            primer2_seq="GCAT",
            dg=-5.5,
            tm=45.0,
            structure="",
        )
        
        d = result.to_dict()
        assert d["primer1"] == "FWD1"
        assert d["dg"] == -5.5


class TestDimerMatrixResult:
    """Tests for DimerMatrixResult model."""
    
    def test_creation(self):
        """Test DimerMatrixResult creation."""
        result = DimerMatrixResult(
            primers=[
                {"name": "P1", "sequence": "ATGC"},
                {"name": "P2", "sequence": "GCAT"},
            ],
            matrix=[[0.0, -3.0], [-3.0, 0.0]],
            grade="A",
        )
        
        assert len(result.primers) == 2
        assert result.matrix[0][1] == -3.0
        assert result.grade == "A"
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        result = DimerMatrixResult(
            primers=[{"name": "P1", "sequence": "ATGC"}],
            matrix=[[0.0]],
            grade="A",
        )
        
        d = result.to_dict()
        assert d["primer_count"] == 1
        assert d["grade"] == "A"


class TestDimerMatrixAnalyzer:
    """Tests for DimerMatrixAnalyzer."""
    
    def test_analyzer_creation(self):
        """Test analyzer creation."""
        analyzer = DimerMatrixAnalyzer()
        assert analyzer.dg_threshold == -6.0
    
    def test_analyzer_custom_config(self):
        """Test analyzer with custom config."""
        analyzer = DimerMatrixAnalyzer({"dg_threshold": -5.0})
        assert analyzer.dg_threshold == -5.0
    
    def test_analyze_single_primer(self):
        """Test analysis with single primer (homodimer only)."""
        analyzer = DimerMatrixAnalyzer()
        primers = [{"name": "P1", "sequence": "ATGCATGCATGCATGCATGC"}]
        
        result = analyzer.analyze(primers)
        
        assert isinstance(result, DimerMatrixResult)
        assert len(result.matrix) == 1
        assert len(result.matrix[0]) == 1
    
    def test_analyze_two_primers(self):
        """Test analysis with two primers."""
        analyzer = DimerMatrixAnalyzer()
        primers = [
            {"name": "FWD", "sequence": "ATGCATGCATGCATGCATGC"},
            {"name": "REV", "sequence": "GCATGCATGCATGCATGCAT"},
        ]
        
        result = analyzer.analyze(primers)
        
        assert len(result.matrix) == 2
        assert len(result.matrix[0]) == 2
        # Matrix should be symmetric
        assert result.matrix[0][1] == result.matrix[1][0]
    
    def test_generate_svg(self):
        """Test SVG generation."""
        analyzer = DimerMatrixAnalyzer()
        primers = [
            {"name": "P1", "sequence": "ATGCATGCATGCATGCATGC"},
            {"name": "P2", "sequence": "GCATGCATGCATGCATGCAT"},
        ]
        
        result = analyzer.analyze(primers)
        svg = analyzer.generate_heatmap_svg(result)
        
        assert "<svg" in svg
        assert "</svg>" in svg
        assert "Primer Dimer Matrix" in svg


class TestAnalyzeDimerMatrix:
    """Tests for analyze_dimer_matrix function."""
    
    def test_function_call(self):
        """Test function call."""
        primers = [
            {"name": "P1", "sequence": "ATGCATGCATGCATGCATGC"},
            {"name": "P2", "sequence": "GCATGCATGCATGCATGCAT"},
        ]
        
        result = analyze_dimer_matrix(primers)
        
        assert isinstance(result, DimerMatrixResult)
        assert result.grade in ["A", "B", "C", "D", "F"]
    
    def test_custom_threshold(self):
        """Test with custom threshold."""
        primers = [{"name": "P1", "sequence": "ATGCATGCATGCATGCATGC"}]
        
        result = analyze_dimer_matrix(primers, dg_threshold=-3.0)
        
        assert isinstance(result, DimerMatrixResult)
