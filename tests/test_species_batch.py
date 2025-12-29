"""
Unit tests for batch species-check module.
"""

import pytest
import tempfile
import json
from pathlib import Path

from primerlab.core.species.batch.batch_loader import (
    BatchInput,
    load_primers_from_directory,
    load_multi_fasta_templates,
)
from primerlab.core.species.batch.cache import AlignmentCache
from primerlab.core.species.batch.parallel import (
    BatchSpeciesResult,
    generate_batch_csv,
)


class TestBatchInput:
    """Tests for BatchInput dataclass."""
    
    def test_creation(self):
        """Test basic creation."""
        batch = BatchInput()
        assert batch.total_primers == 0
        assert len(batch.primer_files) == 0
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        batch = BatchInput(total_primers=5, total_templates=3)
        d = batch.to_dict()
        assert d["total_primers"] == 5
        assert d["total_templates"] == 3


class TestLoadPrimersFromDirectory:
    """Tests for load_primers_from_directory function."""
    
    def test_load_from_directory(self, tmp_path):
        """Test loading primers from directory."""
        # Create test primer files
        primers1 = [{"name": "P1", "forward": "ATGC", "reverse": "GCAT"}]
        primers2 = [{"name": "P2", "forward": "CGTA", "reverse": "TACG"}]
        
        with open(tmp_path / "primers1.json", "w") as f:
            json.dump(primers1, f)
        with open(tmp_path / "primers2.json", "w") as f:
            json.dump(primers2, f)
        
        batch = load_primers_from_directory(str(tmp_path))
        
        assert len(batch.primer_files) == 2
        assert batch.total_primers == 2
    
    def test_empty_directory(self, tmp_path):
        """Test loading from empty directory."""
        batch = load_primers_from_directory(str(tmp_path))
        assert batch.total_primers == 0
    
    def test_nonexistent_directory(self):
        """Test error on nonexistent directory."""
        with pytest.raises(FileNotFoundError):
            load_primers_from_directory("/nonexistent/path")


class TestLoadMultiFastaTemplates:
    """Tests for load_multi_fasta_templates function."""
    
    def test_load_multi_fasta(self, tmp_path):
        """Test loading multi-FASTA file."""
        fasta_content = """>Species1
ATGCGATCGATCGATCG
>Species2
GCTAGCTAGCTAGCTAG
"""
        fasta_path = tmp_path / "templates.fasta"
        with open(fasta_path, "w") as f:
            f.write(fasta_content)
        
        templates = load_multi_fasta_templates(str(fasta_path))
        
        assert len(templates) == 2
        assert "Species1" in templates
        assert "Species2" in templates
    
    def test_nonexistent_fasta(self):
        """Test error on nonexistent file."""
        with pytest.raises(FileNotFoundError):
            load_multi_fasta_templates("/nonexistent/file.fasta")


class TestAlignmentCache:
    """Tests for AlignmentCache."""
    
    def test_set_and_get(self, tmp_path):
        """Test storing and retrieving cache."""
        cache = AlignmentCache(str(tmp_path / "test.db"))
        
        result = {"score": 95.0, "matches": 18}
        cache.set("ATGCGATCG", "ATGCGATCGATCG", result, "Primer1", "Human")
        
        retrieved = cache.get("ATGCGATCG", "ATGCGATCGATCG")
        
        assert retrieved is not None
        assert retrieved["score"] == 95.0
    
    def test_cache_miss(self, tmp_path):
        """Test cache miss returns None."""
        cache = AlignmentCache(str(tmp_path / "test.db"))
        
        result = cache.get("UNKNOWN", "SEQUENCE")
        assert result is None
    
    def test_stats(self, tmp_path):
        """Test cache statistics."""
        cache = AlignmentCache(str(tmp_path / "test.db"))
        
        cache.set("SEQ1", "TEMPLATE1", {"score": 90})
        cache.set("SEQ2", "TEMPLATE2", {"score": 85})
        
        stats = cache.stats()
        assert stats["total_entries"] == 2
    
    def test_clear_all(self, tmp_path):
        """Test clearing cache."""
        cache = AlignmentCache(str(tmp_path / "test.db"))
        
        cache.set("SEQ1", "TEMPLATE1", {"score": 90})
        cache.clear_all()
        
        stats = cache.stats()
        assert stats["total_entries"] == 0


class TestBatchSpeciesResult:
    """Tests for BatchSpeciesResult."""
    
    def test_creation(self):
        """Test basic creation."""
        result = BatchSpeciesResult(total_files=5, total_primers=10)
        assert result.total_files == 5
        assert result.total_primers == 10
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        result = BatchSpeciesResult(
            total_files=5,
            processed=4,
            passed=3,
            failed=1
        )
        d = result.to_dict()
        assert d["pass_rate"] == 75.0


class TestGenerateBatchCSV:
    """Tests for generate_batch_csv function."""
    
    def test_generate_csv(self, tmp_path):
        """Test CSV generation."""
        result = BatchSpeciesResult(
            total_files=1,
            processed=1,
            passed=1,
            summary={"avg_score": 90.0}
        )
        # Add mock result - skip for now as it requires full SpeciesCheckResult
        
        csv_path = tmp_path / "batch_results.csv"
        path = generate_batch_csv(result, str(csv_path))
        
        assert Path(path).exists()
