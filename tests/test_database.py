"""Tests for Primer Database (v0.1.6)."""
import pytest
import tempfile
import json
from pathlib import Path


class TestPrimerDatabase:
    """Tests for PrimerDatabase class."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_history.db"
            from primerlab.core.database import PrimerDatabase
            db = PrimerDatabase(str(db_path))
            yield db
            db.close()
    
    @pytest.fixture
    def sample_result(self):
        """Sample PCR result for testing."""
        return {
            "workflow": "pcr",
            "primers": {
                "forward": {"sequence": "ATGGTGAAGGTCGGAGTCAA", "tm": 60.2, "gc": 50.0, "length": 20},
                "reverse": {"sequence": "TCCACCACCCTGTTGCTGTA", "tm": 60.8, "gc": 50.0, "length": 20}
            },
            "amplicons": [{"length": 400, "gc": 52.5}],
            "qc": {"quality_score": 85.5, "quality_category": "Excellent"},
            "metadata": {"sequence_name": "GAPDH_test"}
        }
    
    def test_database_creation(self, temp_db):
        """Test database file is created."""
        assert temp_db.db_path.exists()
    
    def test_save_design(self, temp_db, sample_result):
        """Test saving a primer design."""
        record_id = temp_db.save_design(sample_result)
        
        assert record_id is not None
        assert record_id > 0
    
    def test_get_by_id(self, temp_db, sample_result):
        """Test retrieving a design by ID."""
        record_id = temp_db.save_design(sample_result)
        
        retrieved = temp_db.get_by_id(record_id)
        
        assert retrieved is not None
        assert retrieved["gene_name"] == "GAPDH_test"
        assert retrieved["fwd_sequence"] == "ATGGTGAAGGTCGGAGTCAA"
        assert retrieved["quality_score"] == 85.5
    
    def test_get_nonexistent_id(self, temp_db):
        """Test retrieving non-existent ID returns None."""
        result = temp_db.get_by_id(99999)
        assert result is None
    
    def test_search_by_gene(self, temp_db, sample_result):
        """Test searching by gene name."""
        temp_db.save_design(sample_result)
        
        results = temp_db.search(gene="GAPDH")
        
        assert len(results) == 1
        assert "GAPDH" in results[0]["gene_name"]
    
    def test_search_by_workflow(self, temp_db, sample_result):
        """Test searching by workflow type."""
        temp_db.save_design(sample_result)
        
        results = temp_db.search(workflow="pcr")
        
        assert len(results) == 1
        assert results[0]["workflow"] == "pcr"
    
    def test_search_by_min_quality(self, temp_db, sample_result):
        """Test searching by minimum quality score."""
        temp_db.save_design(sample_result)
        
        # Should find
        results_high = temp_db.search(min_quality=80.0)
        assert len(results_high) == 1
        
        # Should not find
        results_low = temp_db.search(min_quality=90.0)
        assert len(results_low) == 0
    
    def test_search_by_sequence(self, temp_db, sample_result):
        """Test searching by primer sequence."""
        temp_db.save_design(sample_result)
        
        results = temp_db.search(sequence="ATGGTGAAGGTCGGAGTCAA")
        
        assert len(results) == 1
    
    def test_delete(self, temp_db, sample_result):
        """Test deleting a design."""
        record_id = temp_db.save_design(sample_result)
        
        # Verify it exists
        assert temp_db.get_by_id(record_id) is not None
        
        # Delete
        deleted = temp_db.delete(record_id)
        assert deleted == True
        
        # Verify it's gone
        assert temp_db.get_by_id(record_id) is None
    
    def test_delete_nonexistent(self, temp_db):
        """Test deleting non-existent ID returns False."""
        deleted = temp_db.delete(99999)
        assert deleted == False
    
    def test_get_recent(self, temp_db, sample_result):
        """Test getting recent designs."""
        # Add multiple designs
        for i in range(5):
            result = sample_result.copy()
            result["metadata"] = {"sequence_name": f"GENE_{i}"}
            temp_db.save_design(result)
        
        recent = temp_db.get_recent(limit=3)
        
        assert len(recent) == 3
    
    def test_get_stats(self, temp_db, sample_result):
        """Test getting database statistics."""
        temp_db.save_design(sample_result)
        
        stats = temp_db.get_stats()
        
        assert stats["total_designs"] == 1
        assert "pcr" in stats["by_workflow"]
        assert stats["avg_quality_score"] > 0
    
    def test_export_csv(self, temp_db, sample_result):
        """Test exporting to CSV."""
        temp_db.save_design(sample_result)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "export.csv"
            result = temp_db.export_csv(str(csv_path))
            
            assert Path(result).exists()
            
            # Check CSV content
            content = csv_path.read_text()
            assert "GAPDH" in content
            assert "ATGGTGAAGGTCGGAGTCAA" in content


class TestFormatHistoryTable:
    """Tests for format_history_table function."""
    
    def test_format_empty(self):
        """Test formatting empty list."""
        from primerlab.core.database import format_history_table
        
        result = format_history_table([])
        assert "No designs found" in result
    
    def test_format_with_data(self):
        """Test formatting with data."""
        from primerlab.core.database import format_history_table
        
        designs = [
            {
                "id": 1,
                "created_at": "2025-12-18T00:00:00",
                "gene_name": "GAPDH",
                "workflow": "pcr",
                "fwd_sequence": "ATGGTGAAGGTCGGAGTCAA",
                "quality_score": 85.5
            }
        ]
        
        result = format_history_table(designs)
        
        assert "GAPDH" in result
        assert "pcr" in result
        assert "85.5" in result
