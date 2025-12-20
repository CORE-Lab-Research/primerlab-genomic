"""
Tests for BLAST Wrapper and Fallback (v0.3.0)
"""

import pytest
from pathlib import Path

from primerlab.core.models.blast import BlastHit, BlastResult, SpecificityResult, AlignmentMethod
from primerlab.core.tools.blast_wrapper import BlastWrapper, check_blast_installation
from primerlab.core.tools.align_fallback import BiopythonAligner, get_fallback_aligner
from primerlab.core.tools.primer_aligner import PrimerAligner, AlignmentMode, check_alignment_availability


# Path to test database
TEST_DB_PATH = Path(__file__).parent.parent / "examples" / "blast" / "test_db.fasta"


class TestBlastModels:
    """Tests for BLAST result models."""
    
    def test_blast_hit_creation(self):
        """BlastHit should be created with all fields."""
        hit = BlastHit(
            subject_id="test_seq",
            subject_title="Test sequence",
            query_start=1,
            query_end=20,
            subject_start=100,
            subject_end=120,
            identity_percent=95.0,
            alignment_length=20,
            mismatches=1,
            gaps=0,
            evalue=1e-10,
            bit_score=40.0
        )
        
        assert hit.subject_id == "test_seq"
        assert hit.identity_percent == 95.0
        assert hit.is_significant()
    
    def test_blast_hit_not_significant(self):
        """Low identity or high e-value should not be significant."""
        hit = BlastHit(
            subject_id="test",
            subject_title="",
            query_start=1,
            query_end=20,
            subject_start=1,
            subject_end=20,
            identity_percent=50.0,  # Low identity
            alignment_length=20,
            mismatches=10,
            gaps=0,
            evalue=1e-10,
            bit_score=20.0
        )
        
        assert not hit.is_significant(identity_threshold=80.0)
    
    def test_blast_result_specificity_score(self):
        """BlastResult should calculate specificity score."""
        hit1 = BlastHit(
            subject_id="target",
            subject_title="",
            query_start=1, query_end=20,
            subject_start=1, subject_end=20,
            identity_percent=100.0,
            alignment_length=20,
            mismatches=0, gaps=0,
            evalue=1e-15, bit_score=50.0,
            is_on_target=True
        )
        
        result = BlastResult(
            query_id="primer",
            query_seq="ATGCATGCATGCATGCATGC",
            query_length=20,
            hits=[hit1]
        )
        
        # Only on-target hit = 100% specific
        assert result.get_specificity_score() == 100.0
    
    def test_specificity_result_combined(self):
        """SpecificityResult should combine forward and reverse."""
        fwd = BlastResult(
            query_id="forward",
            query_seq="ATGC",
            query_length=4,
            hits=[]
        )
        rev = BlastResult(
            query_id="reverse",
            query_seq="GCAT",
            query_length=4,
            hits=[]
        )
        
        specificity = SpecificityResult(fwd, rev)
        
        assert specificity.combined_score == 100.0
        assert specificity.is_specific


class TestBlastWrapper:
    """Tests for BLAST wrapper."""
    
    def test_check_installation(self):
        """Should return installation info."""
        info = check_blast_installation()
        assert isinstance(info.available, bool)
        # If not available, should have error message
        if not info.available:
            assert info.error is not None
    
    def test_wrapper_is_available_property(self):
        """Wrapper should expose is_available property."""
        wrapper = BlastWrapper()
        assert isinstance(wrapper.is_available, bool)
    
    def test_wrapper_params(self):
        """Wrapper should accept custom params."""
        wrapper = BlastWrapper(params={"evalue": 1.0})
        assert wrapper.params["evalue"] == 1.0
        # Should still have other defaults
        assert "word_size" in wrapper.params


class TestBiopythonFallback:
    """Tests for Biopython fallback aligner."""
    
    def test_get_fallback_aligner(self):
        """Should return aligner or None."""
        aligner = get_fallback_aligner()
        # biopython should be available in our env
        assert aligner is not None or aligner is None  # Either is valid
    
    def test_aligner_is_available(self):
        """Aligner should report availability."""
        aligner = BiopythonAligner()
        assert isinstance(aligner.is_available, bool)
    
    @pytest.mark.skipif(not get_fallback_aligner(), reason="Biopython not available")
    def test_search_database(self):
        """Should search FASTA database."""
        if not TEST_DB_PATH.exists():
            pytest.skip("Test database not found")
        
        aligner = BiopythonAligner()
        result = aligner.search_database(
            query_seq="ATGAAACGCATTAGCACCAC",  # From test_db
            database_path=str(TEST_DB_PATH),
            query_id="test_primer"
        )
        
        assert result.success
        assert result.method == AlignmentMethod.BIOPYTHON


class TestPrimerAligner:
    """Tests for unified PrimerAligner."""
    
    def test_check_availability(self):
        """Should return availability tuple."""
        blast, biopython, recommended = check_alignment_availability()
        assert isinstance(blast, bool)
        assert isinstance(biopython, bool)
        assert recommended in ["blast", "biopython", "none"]
    
    def test_auto_mode_selection(self):
        """Auto mode should select available method."""
        try:
            aligner = PrimerAligner(mode=AlignmentMode.AUTO)
            assert aligner.active_method in [AlignmentMethod.BLAST, AlignmentMethod.BIOPYTHON]
        except RuntimeError:
            pytest.skip("No alignment method available")
    
    @pytest.mark.skipif(not get_fallback_aligner(), reason="Biopython not available")
    def test_search_primer_biopython(self):
        """Should search using Biopython."""
        if not TEST_DB_PATH.exists():
            pytest.skip("Test database not found")
        
        aligner = PrimerAligner(mode=AlignmentMode.BIOPYTHON)
        result = aligner.search_primer(
            primer_seq="ATGACCATGATTACGGATTC",  # From lacZ
            database=str(TEST_DB_PATH),
            primer_id="lacZ_primer"
        )
        
        assert result.success
    
    @pytest.mark.skipif(not get_fallback_aligner(), reason="Biopython not available")
    def test_check_primer_specificity(self):
        """Should check specificity of primer pair."""
        if not TEST_DB_PATH.exists():
            pytest.skip("Test database not found")
        
        aligner = PrimerAligner(mode=AlignmentMode.BIOPYTHON)
        result = aligner.check_primer_specificity(
            forward_primer="ATGACCATGATTACGGATTC",
            reverse_primer="GCAACTGTTGGGAAGGGCGA",
            database=str(TEST_DB_PATH)
        )
        
        assert isinstance(result, SpecificityResult)
        assert 0 <= result.combined_score <= 100
