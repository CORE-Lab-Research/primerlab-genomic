"""
Tests for Report Generator (v0.3.3)
"""

import pytest
import tempfile
from pathlib import Path

from primerlab.core.report import (
    PrimerReport,
    DesignSummary,
    ValidationSummary,
    OfftargetSummary,
    ReportGenerator,
    HTMLExporter,
    JSONExporter,
    ReportExporter
)
from primerlab.core.report.models import PrimerInfo


class TestReportModels:
    """Tests for report data models."""
    
    def test_primer_report_creation(self):
        """Should create PrimerReport with defaults."""
        report = PrimerReport()
        
        assert report.overall_grade == "?"
        assert report.overall_score == 0.0
        assert report.warnings == []
    
    def test_design_summary_has_primers(self):
        """has_primers should return True when both primers exist."""
        summary = DesignSummary(
            forward_primer=PrimerInfo("Fwd", "ATGC", 4, 55.0, 50.0),
            reverse_primer=PrimerInfo("Rev", "GCTA", 4, 55.0, 50.0)
        )
        
        assert summary.has_primers is True
    
    def test_design_summary_no_primers(self):
        """has_primers should return False when no primers."""
        summary = DesignSummary()
        
        assert summary.has_primers is False
    
    def test_primer_report_calculate_grade(self):
        """Should calculate overall grade from scores."""
        report = PrimerReport()
        report.design = DesignSummary(
            forward_primer=PrimerInfo("Fwd", "ATGC", 4, 55.0, 50.0),
            reverse_primer=PrimerInfo("Rev", "GCTA", 4, 55.0, 50.0),
            quality_score=90.0
        )
        
        grade = report.calculate_overall_grade()
        
        assert grade == "A"
        assert report.overall_score == 90.0


class TestReportGenerator:
    """Tests for ReportGenerator class."""
    
    def test_generator_chaining(self):
        """Generator should support method chaining."""
        generator = ReportGenerator()
        
        result = generator.add_design(
            forward_seq="ATGCATGC",
            reverse_seq="GCTAATGC",
            forward_tm=55.0,
            reverse_tm=55.0,
            forward_gc=50.0,
            reverse_gc=50.0
        ).add_validation(
            amplicons=1,
            product_size=200,
            success_probability=0.95
        ).add_offtarget(
            forward_hits=0,
            reverse_hits=1,
            grade="A",
            score=95.0
        )
        
        assert result is generator
    
    def test_generator_to_markdown(self):
        """Should generate markdown report."""
        generator = ReportGenerator()
        generator.add_design(
            forward_seq="ATGCATGC",
            reverse_seq="GCTAATGC"
        )
        
        markdown = generator.to_markdown()
        
        assert "PrimerLab Report" in markdown
        assert "ATGCATGC" in markdown
    
    def test_generator_to_json(self):
        """Should generate JSON report."""
        generator = ReportGenerator()
        generator.add_design(
            forward_seq="ATGCATGC",
            reverse_seq="GCTAATGC"
        )
        
        json_str = generator.to_json()
        
        assert "ATGCATGC" in json_str
        assert '"primerlab_version"' in json_str  # ReportGenerator uses to_dict()


class TestHTMLExporter:
    """Tests for HTML export."""
    
    def test_html_generation(self):
        """Should generate valid HTML."""
        report = PrimerReport()
        report.design = DesignSummary(
            forward_primer=PrimerInfo("Fwd", "ATGC", 4, 55.0, 50.0),
            reverse_primer=PrimerInfo("Rev", "GCTA", 4, 55.0, 50.0)
        )
        
        exporter = HTMLExporter(report)
        html = exporter.generate()
        
        assert "<!DOCTYPE html>" in html
        assert "PrimerLab Report" in html
        assert "ATGC" in html
    
    def test_html_save(self):
        """Should save HTML to file."""
        report = PrimerReport()
        
        exporter = HTMLExporter(report)
        
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            exporter.save(f.name)
            
            content = Path(f.name).read_text()
            assert "<!DOCTYPE html>" in content


class TestJSONExporter:
    """Tests for JSON export."""
    
    def test_json_generation(self):
        """Should generate valid JSON."""
        report = PrimerReport()
        report.design = DesignSummary(
            forward_primer=PrimerInfo("Fwd", "ATGC", 4, 55.0, 50.0),
            reverse_primer=PrimerInfo("Rev", "GCTA", 4, 55.0, 50.0)
        )
        
        exporter = JSONExporter(report)
        json_str = exporter.generate()
        
        import json
        data = json.loads(json_str)
        
        assert "overall" in data
        assert "design" in data
    
    def test_json_filtering(self):
        """Should filter sections based on options."""
        report = PrimerReport()
        
        exporter = JSONExporter(report)
        json_str = exporter.generate(include_design=False)
        
        import json
        data = json.loads(json_str)
        
        assert "design" not in data


class TestReportExporter:
    """Tests for unified exporter."""
    
    def test_export_markdown(self):
        """Should export markdown format."""
        report = PrimerReport()
        exporter = ReportExporter(report)
        
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            path = exporter.export(f.name, format="markdown")
            
            assert Path(path).exists()
            content = Path(path).read_text()
            assert "PrimerLab Report" in content
    
    def test_export_html(self):
        """Should export HTML format."""
        report = PrimerReport()
        exporter = ReportExporter(report)
        
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            path = exporter.export(f.name, format="html")
            
            content = Path(path).read_text()
            assert "<!DOCTYPE html>" in content
    
    def test_export_json(self):
        """Should export JSON format."""
        report = PrimerReport()
        exporter = ReportExporter(report)
        
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = exporter.export(f.name, format="json")
            
            import json
            content = Path(path).read_text()
            data = json.loads(content)
            assert "overall" in data
