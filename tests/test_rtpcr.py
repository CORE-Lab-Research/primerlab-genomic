"""
Unit tests for RT-qPCR module (v0.6.0 Phase 2).
"""

import pytest
from primerlab.core.rtpcr.exon_junction import (
    detect_exon_junction,
    find_junction_position,
    ExonJunctionResult,
)
from primerlab.core.rtpcr.gdna_check import (
    check_gdna_risk,
    GdnaRiskResult,
)
from primerlab.core.rtpcr.transcript_loader import (
    Exon,
    Transcript,
    parse_gtf_line,
)


# Example exon structure: 3 exons of 100bp each
# Exon1: 0-100, Exon2: 100-200, Exon3: 200-300
EXAMPLE_EXONS = [(0, 100), (100, 200), (200, 300)]


class TestExonJunctionResult:
    """Test ExonJunctionResult dataclass."""
    
    def test_to_dict(self):
        """Test to_dict conversion."""
        result = ExonJunctionResult(
            primer_sequence="ATGCGATCGATCGATCG",
            primer_start=95,
            primer_end=115,
            spans_junction=True,
            junction_position=5,
            exon_5prime=0,
            exon_3prime=1,
            junction_overlap_5=5,
            junction_overlap_3=15,
            is_optimal=True,
            warnings=[],
        )
        
        d = result.to_dict()
        
        assert d["spans_junction"] == True
        assert d["junction_position"] == 5
        assert d["is_optimal"] == True


class TestFindJunctionPosition:
    """Test junction position finding."""
    
    def test_primer_spanning_junction(self):
        """Test primer that spans exon1-exon2 junction."""
        # Primer from position 95 to 115 (spans junction at 100)
        result = find_junction_position(95, 115, EXAMPLE_EXONS)
        
        assert result is not None
        junction_pos, exon_5, exon_3 = result
        assert junction_pos == 5  # Junction at position 5 in primer
        assert exon_5 == 0
        assert exon_3 == 1
    
    def test_primer_within_exon(self):
        """Test primer within single exon."""
        # Primer from 50 to 70 (within exon 1)
        result = find_junction_position(50, 70, EXAMPLE_EXONS)
        
        assert result is None
    
    def test_primer_spanning_second_junction(self):
        """Test primer spanning exon2-exon3 junction."""
        # Primer from 195 to 215
        result = find_junction_position(195, 215, EXAMPLE_EXONS)
        
        assert result is not None
        junction_pos, exon_5, exon_3 = result
        assert junction_pos == 5


class TestDetectExonJunction:
    """Test exon junction detection."""
    
    def test_junction_spanning_optimal(self):
        """Test optimal junction-spanning primer."""
        result = detect_exon_junction(
            primer_sequence="ATGCGATCGATCGATCGATCG",  # 21bp
            primer_start=90,  # 10bp in exon1, 11bp in exon2
            exon_boundaries=EXAMPLE_EXONS,
        )
        
        assert result.spans_junction == True
        assert result.is_optimal == True
        assert len(result.warnings) == 0
    
    def test_junction_spanning_suboptimal(self):
        """Test junction-spanning with poor overlap."""
        result = detect_exon_junction(
            primer_sequence="ATGCGATCGATCGATCGATCG",  # 21bp
            primer_start=98,  # Only 2bp in exon1
            exon_boundaries=EXAMPLE_EXONS,
            min_overlap=5,
        )
        
        assert result.spans_junction == True
        assert result.is_optimal == False
        assert any("overlap" in w.lower() for w in result.warnings)
    
    def test_no_junction(self):
        """Test primer within single exon."""
        result = detect_exon_junction(
            primer_sequence="ATGCGATCGATCGATCG",  # 17bp
            primer_start=50,
            exon_boundaries=EXAMPLE_EXONS,
        )
        
        assert result.spans_junction == False
        assert result.is_optimal == False
        assert any("gdna" in w.lower() for w in result.warnings)


class TestGdnaRiskCheck:
    """Test gDNA contamination risk assessment."""
    
    def test_junction_spanning_no_risk(self):
        """Test junction-spanning primers = no risk."""
        # Forward spans junction
        result = check_gdna_risk(
            fwd_start=95,
            fwd_end=115,  # Spans exon1-exon2
            rev_start=150,
            rev_end=170,
            exon_boundaries=EXAMPLE_EXONS,
        )
        
        assert result.risk_level == "None"
        assert result.is_rt_specific == True
        assert result.fwd_spans_junction == True
    
    def test_same_exon_high_risk(self):
        """Test primers in same exon = high risk."""
        result = check_gdna_risk(
            fwd_start=10,
            fwd_end=30,
            rev_start=50,
            rev_end=70,
            exon_boundaries=EXAMPLE_EXONS,
        )
        
        assert result.risk_level == "High"
        assert result.is_rt_specific == False
        assert any("same exon" in w.lower() for w in result.warnings)
    
    def test_large_intron_low_risk(self):
        """Test large intron between primers = low risk."""
        result = check_gdna_risk(
            fwd_start=50,
            fwd_end=70,
            rev_start=150,
            rev_end=170,
            exon_boundaries=EXAMPLE_EXONS,
            genomic_intron_sizes=[5000, 3000],  # Large introns
        )
        
        assert result.risk_level == "Low"
        assert result.intron_between == True


class TestTranscript:
    """Test Transcript class."""
    
    def test_exon_boundaries(self):
        """Test get_exon_boundaries."""
        transcript = Transcript(
            transcript_id="TEST_001",
            gene_name="TEST",
            chromosome="chr1",
            strand="+",
            exons=[
                Exon(1, 0, 100),
                Exon(2, 200, 350),
                Exon(3, 500, 600),
            ],
        )
        
        boundaries = transcript.get_exon_boundaries()
        
        assert len(boundaries) == 3
        assert boundaries[0] == (0, 100)
        assert boundaries[1] == (100, 250)  # 150bp exon2
        assert boundaries[2] == (250, 350)  # 100bp exon3
    
    def test_junction_positions(self):
        """Test get_junction_positions."""
        transcript = Transcript(
            transcript_id="TEST_001",
            gene_name="TEST",
            chromosome="chr1",
            strand="+",
            exons=[
                Exon(1, 0, 100),
                Exon(2, 200, 300),
            ],
        )
        
        junctions = transcript.get_junction_positions()
        
        assert junctions == [100]  # Junction after exon1


class TestRtpcrAPI:
    """Test RT-qPCR API function."""
    
    def test_api_basic(self):
        """Test basic API call."""
        from primerlab.api import validate_rtpcr_primers_api
        
        result = validate_rtpcr_primers_api(
            fwd_sequence="ATGCGATCGATCGATCGATCG",
            fwd_start=90,  # Spans junction
            rev_sequence="ATGCGATCGATCGATCG",
            rev_start=150,
            exon_boundaries=EXAMPLE_EXONS,
        )
        
        assert "fwd_junction" in result
        assert "rev_junction" in result
        assert "gdna_risk" in result
        assert "is_rt_specific" in result
        assert "grade" in result
    
    def test_api_rt_specific(self):
        """Test API with RT-specific primers."""
        from primerlab.api import validate_rtpcr_primers_api
        
        result = validate_rtpcr_primers_api(
            fwd_sequence="ATGCGATCGATCGATCGATCG",
            fwd_start=90,
            rev_sequence="ATGCGATCGATCGATCG",
            rev_start=150,
            exon_boundaries=EXAMPLE_EXONS,
        )
        
        assert result["is_rt_specific"] == True
        assert result["grade"] in ["A", "B"]
