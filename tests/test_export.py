"""Tests for Export Functionality (v0.1.2 backfill + v0.1.3)."""
import pytest
import tempfile
import os
from pathlib import Path
from primerlab.core.output import OutputManager
from primerlab.core.models import WorkflowResult, Primer, Amplicon
from primerlab.core.models.metadata import RunMetadata
from primerlab.core.models.qc import QCResult


class TestOutputManager:
    """Tests for OutputManager class."""
    
    @pytest.fixture
    def sample_result(self):
        """Create a sample WorkflowResult for testing."""
        primers = {
            "forward": Primer(
                id="forward",
                sequence="ATGCGATCGATCGATCGC",
                tm=60.0,
                gc=55.0,
                length=18,
                start=10,
                end=28
            ),
            "reverse": Primer(
                id="reverse",
                sequence="GCTAGCTAGCTAGCTAG",
                tm=59.0,
                gc=52.0,
                length=17,
                start=100,
                end=117
            )
        }
        
        amplicons = [
            Amplicon(
                start=10,
                end=117,
                length=107,
                sequence="ATGC" * 25,
                gc=50.0,
                tm_forward=60.0,
                tm_reverse=59.0
            )
        ]
        
        metadata = RunMetadata(
            workflow="pcr",
            timestamp="2024-01-01T00:00:00Z",
            version="0.1.3-dev",
            parameters={}
        )
        
        qc = QCResult(
            hairpin_ok=True,
            homodimer_ok=True,
            heterodimer_ok=True,
            tm_balance_ok=True,
            hairpin_dg=0.0,
            homodimer_dg=0.0,
            heterodimer_dg=0.0,
            tm_diff=1.0,
            warnings=[],
            errors=[]
        )
        
        return WorkflowResult(
            workflow="pcr",
            primers=primers,
            amplicons=amplicons,
            metadata=metadata,
            qc=qc,
            raw={}
        )
    
    def test_output_manager_creates_directory(self):
        """OutputManager should create output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = os.path.join(tmpdir, "test_output")
            mgr = OutputManager(output_dir, "pcr")
            
            assert mgr.run_dir.exists()
            assert "PCR" in str(mgr.run_dir)
    
    def test_save_json(self, sample_result):
        """save_json should create valid JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = OutputManager(tmpdir, "pcr")
            mgr.save_json(sample_result)
            
            json_path = mgr.run_dir / "result.json"
            assert json_path.exists()
    
    def test_save_csv(self, sample_result):
        """save_csv should create CSV file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = OutputManager(tmpdir, "pcr")
            mgr.save_csv(sample_result)
            
            csv_path = mgr.run_dir / "primers.csv"
            assert csv_path.exists()
            
            # Check content
            content = csv_path.read_text()
            assert "forward" in content
            assert "reverse" in content
    
    def test_save_ordering_format_idt(self, sample_result):
        """save_ordering_format should create IDT format file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = OutputManager(tmpdir, "pcr")
            mgr.save_ordering_format(sample_result, "idt")
            
            idt_path = mgr.run_dir / "order_idt.csv"
            assert idt_path.exists()
    
    def test_save_ordering_format_sigma(self, sample_result):
        """save_ordering_format should create Sigma format file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = OutputManager(tmpdir, "pcr")
            mgr.save_ordering_format(sample_result, "sigma")
            
            sigma_path = mgr.run_dir / "order_sigma.csv"
            assert sigma_path.exists()
    
    def test_save_ordering_format_thermo(self, sample_result):
        """save_ordering_format should create Thermo format file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = OutputManager(tmpdir, "pcr")
            mgr.save_ordering_format(sample_result, "thermo")
            
            thermo_path = mgr.run_dir / "order_thermo.csv"
            assert thermo_path.exists()


class TestExportFormats:
    """Tests for vendor-specific export formats."""
    
    @pytest.fixture
    def sample_result(self):
        """Create a sample result."""
        primers = {
            "forward": Primer(
                id="forward",
                sequence="ATGCGATCGATCGATCGC",
                tm=60.0,
                gc=55.0,
                length=18,
                start=10,
                end=28
            )
        }
        
        metadata = RunMetadata(
            workflow="pcr",
            timestamp="2024-01-01T00:00:00Z",
            version="0.1.3-dev"
        )
        
        qc = QCResult(
            hairpin_ok=True,
            homodimer_ok=True,
            heterodimer_ok=True,
            tm_balance_ok=True,
            hairpin_dg=0.0,
            homodimer_dg=0.0,
            heterodimer_dg=0.0,
            tm_diff=0.0
        )
        
        return WorkflowResult(
            workflow="pcr",
            primers=primers,
            amplicons=[],
            metadata=metadata,
            qc=qc,
            raw={}
        )
    
    def test_all_formats_have_sequence(self, sample_result):
        """All export formats should include primer sequences."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = OutputManager(tmpdir, "pcr")
            
            for fmt in ["idt", "sigma", "thermo"]:
                mgr.save_ordering_format(sample_result, fmt)
                
                file_path = mgr.run_dir / f"order_{fmt}.csv"
                content = file_path.read_text()
                
                # Should contain the sequence
                assert "ATGCGATCGATCGATCGC" in content
