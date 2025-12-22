"""
JSON Export (v0.3.3)

Generate machine-readable JSON reports.
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import asdict

from primerlab.core.report.models import PrimerReport


class JSONExporter:
    """
    Generate machine-readable JSON reports.
    
    Provides complete metrics export with optional filtering.
    """
    
    def __init__(self, report: PrimerReport):
        """
        Initialize JSON exporter.
        
        Args:
            report: PrimerReport to export
        """
        self.report = report
    
    def generate(
        self,
        include_metadata: bool = True,
        include_design: bool = True,
        include_validation: bool = True,
        include_offtarget: bool = True,
        include_variant: bool = True,
        pretty: bool = True
    ) -> str:
        """
        Generate JSON report.
        
        Args:
            include_metadata: Include report metadata
            include_design: Include design summary
            include_validation: Include validation summary
            include_offtarget: Include off-target summary
            include_variant: Include variant summary
            pretty: Pretty print JSON
            
        Returns:
            JSON string
        """
        data = {}
        
        # Metadata
        if include_metadata:
            data["metadata"] = {
                "report_id": self.report.report_id,
                "created_at": self.report.created_at.isoformat(),
                "primerlab_version": self.report.primerlab_version,
                "config_file": self.report.config_file,
                "sequence_source": self.report.sequence_source
            }
        
        # Overall status
        data["overall"] = {
            "grade": self.report.overall_grade,
            "score": self.report.overall_score,
            "warnings": self.report.warnings,
            "recommendations": self.report.recommendations
        }
        
        # Design summary
        if include_design and self.report.design.has_primers:
            d = self.report.design
            data["design"] = {
                "forward_primer": self._primer_to_dict(d.forward_primer),
                "reverse_primer": self._primer_to_dict(d.reverse_primer),
                "probe": self._primer_to_dict(d.probe) if d.probe else None,
                "product_size": d.product_size,
                "design_method": d.design_method,
                "candidates_evaluated": d.candidates_evaluated,
                "quality_score": d.quality_score
            }
        
        # Validation summary
        if include_validation and self.report.validation.validated:
            v = self.report.validation
            data["validation"] = {
                "validated": v.validated,
                "amplicons_predicted": v.amplicons_predicted,
                "primary_product_size": v.primary_product_size,
                "off_products": v.off_products,
                "forward_binding_score": v.forward_binding_score,
                "reverse_binding_score": v.reverse_binding_score,
                "pcr_success_probability": v.pcr_success_probability,
                "warnings": v.warnings
            }
        
        # Off-target summary
        if include_offtarget and self.report.offtarget.checked:
            o = self.report.offtarget
            data["offtarget"] = {
                "checked": o.checked,
                "database": o.database,
                "forward_hits": o.forward_hits,
                "reverse_hits": o.reverse_hits,
                "forward_grade": o.forward_grade,
                "reverse_grade": o.reverse_grade,
                "combined_grade": o.combined_grade,
                "specificity_score": o.specificity_score,
                "high_risk_sites": o.high_risk_sites,
                "alignment_method": o.alignment_method
            }
        
        # Variant summary
        if include_variant and self.report.variant.checked:
            var = self.report.variant
            data["variant"] = {
                "checked": var.checked,
                "vcf_file": var.vcf_file,
                "forward_overlaps": var.forward_overlaps,
                "reverse_overlaps": var.reverse_overlaps,
                "critical_variants": var.critical_variants,
                "maf_threshold": var.maf_threshold
            }
        
        indent = 2 if pretty else None
        return json.dumps(data, indent=indent, default=str)
    
    def _primer_to_dict(self, primer) -> Optional[Dict[str, Any]]:
        """Convert primer info to dict."""
        if primer is None:
            return None
        return {
            "name": primer.name,
            "sequence": primer.sequence,
            "length": primer.length,
            "tm": primer.tm,
            "gc_percent": primer.gc_percent,
            "position": primer.position,
            "orientation": primer.orientation
        }
    
    def save(self, path: str, **kwargs):
        """
        Save JSON report to file.
        
        Args:
            path: Output file path
            **kwargs: Options passed to generate()
        """
        json_str = self.generate(**kwargs)
        Path(path).write_text(json_str, encoding="utf-8")


def export_json(report: PrimerReport, path: str, **kwargs):
    """
    Convenience function to export JSON report.
    
    Args:
        report: PrimerReport to export
        path: Output file path
        **kwargs: Options passed to generate()
    """
    exporter = JSONExporter(report)
    exporter.save(path, **kwargs)


class ReportExporter:
    """
    Unified exporter for all formats.
    
    Use this class to export reports in any supported format.
    """
    
    def __init__(self, report: PrimerReport):
        """
        Initialize exporter.
        
        Args:
            report: PrimerReport to export
        """
        self.report = report
    
    def export(self, path: str, format: str = "markdown") -> str:
        """
        Export report to file.
        
        Args:
            path: Output file path
            format: Export format (markdown, html, json)
            
        Returns:
            Path to exported file
        """
        from primerlab.core.report.generator import ReportGenerator
        
        if format == "html":
            exporter = HTMLExporter(self.report)
            exporter.save(path)
        elif format == "json":
            exporter = JSONExporter(self.report)
            exporter.save(path)
        else:  # markdown
            gen = ReportGenerator()
            gen.report = self.report
            content = gen.to_markdown()
            Path(path).write_text(content, encoding="utf-8")
        
        return path
