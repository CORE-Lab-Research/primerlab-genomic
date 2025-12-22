"""
Report Generator (v0.3.3)

Generate combined reports from primer design workflow results.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from primerlab.core.report.models import (
    PrimerReport,
    PrimerInfo,
    DesignSummary,
    ValidationSummary,
    OfftargetSummary,
    VariantSummary,
    ReportFormat
)
from primerlab import __version__


class ReportGenerator:
    """
    Generate combined primer reports.
    
    Aggregates results from design, validation, and off-target analysis
    into a single unified report.
    """
    
    def __init__(self):
        """Initialize report generator."""
        self.report = PrimerReport(
            primerlab_version=__version__,
            created_at=datetime.now()
        )
    
    def from_workflow_result(self, result: Any) -> "ReportGenerator":
        """
        Build report from PCR workflow result.
        
        Args:
            result: PCRWorkflowResult from run_pcr_workflow
            
        Returns:
            Self for chaining
        """
        # Design summary
        if hasattr(result, "primers") and result.primers:
            fwd = result.primers.get("forward")
            rev = result.primers.get("reverse")
            
            self.report.design = DesignSummary(
                forward_primer=PrimerInfo(
                    name="Forward",
                    sequence=fwd.sequence if fwd else "",
                    length=len(fwd.sequence) if fwd else 0,
                    tm=fwd.tm if fwd else 0.0,
                    gc_percent=fwd.gc_percent if fwd else 0.0,
                    orientation="forward"
                ) if fwd else None,
                reverse_primer=PrimerInfo(
                    name="Reverse",
                    sequence=rev.sequence if rev else "",
                    length=len(rev.sequence) if rev else 0,
                    tm=rev.tm if rev else 0.0,
                    gc_percent=rev.gc_percent if rev else 0.0,
                    orientation="reverse"
                ) if rev else None,
                product_size=result.product_size if hasattr(result, "product_size") else None,
                quality_score=result.quality_score if hasattr(result, "quality_score") else 0.0
            )
        
        # Validation summary
        if hasattr(result, "validation") and result.validation:
            val = result.validation
            self.report.validation = ValidationSummary(
                validated=True,
                amplicons_predicted=val.get("amplicons_predicted", 0),
                primary_product_size=val.get("product_size"),
                pcr_success_probability=val.get("success_probability", 0.0)
            )
        
        # Off-target summary
        if hasattr(result, "offtarget_check") and result.offtarget_check:
            ot = result.offtarget_check
            self.report.offtarget = OfftargetSummary(
                checked=True,
                forward_hits=ot.get("forward_offtargets", 0),
                reverse_hits=ot.get("reverse_offtargets", 0),
                specificity_score=ot.get("specificity_score", 0.0),
                combined_grade=ot.get("grade", "?")
            )
        
        # Calculate overall grade
        self.report.calculate_overall_grade()
        
        return self
    
    def add_design(
        self,
        forward_seq: str,
        reverse_seq: str,
        forward_tm: float = 0.0,
        reverse_tm: float = 0.0,
        forward_gc: float = 0.0,
        reverse_gc: float = 0.0,
        product_size: Optional[int] = None,
        quality_score: float = 0.0
    ) -> "ReportGenerator":
        """Add design summary manually."""
        self.report.design = DesignSummary(
            forward_primer=PrimerInfo(
                name="Forward",
                sequence=forward_seq,
                length=len(forward_seq),
                tm=forward_tm,
                gc_percent=forward_gc,
                orientation="forward"
            ),
            reverse_primer=PrimerInfo(
                name="Reverse",
                sequence=reverse_seq,
                length=len(reverse_seq),
                tm=reverse_tm,
                gc_percent=reverse_gc,
                orientation="reverse"
            ),
            product_size=product_size,
            quality_score=quality_score
        )
        return self
    
    def add_validation(
        self,
        amplicons: int = 0,
        product_size: Optional[int] = None,
        success_probability: float = 0.0
    ) -> "ReportGenerator":
        """Add validation summary."""
        self.report.validation = ValidationSummary(
            validated=True,
            amplicons_predicted=amplicons,
            primary_product_size=product_size,
            pcr_success_probability=success_probability
        )
        return self
    
    def add_offtarget(
        self,
        database: str = "",
        forward_hits: int = 0,
        reverse_hits: int = 0,
        grade: str = "?",
        score: float = 0.0
    ) -> "ReportGenerator":
        """Add off-target summary."""
        self.report.offtarget = OfftargetSummary(
            checked=True,
            database=database,
            forward_hits=forward_hits,
            reverse_hits=reverse_hits,
            combined_grade=grade,
            specificity_score=score
        )
        return self
    
    def generate(self) -> PrimerReport:
        """Generate and return the report."""
        self.report.calculate_overall_grade()
        return self.report
    
    def to_markdown(self) -> str:
        """Generate markdown report."""
        report = self.report
        lines = []
        
        # Header
        lines.append(f"# 🧬 PrimerLab Report")
        lines.append(f"")
        lines.append(f"**Generated:** {report.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Version:** PrimerLab v{report.primerlab_version}")
        lines.append(f"**Overall Grade:** **{report.overall_grade}** ({report.overall_score:.1f}/100)")
        lines.append(f"")
        
        # Design Summary
        if report.design.has_primers:
            lines.append(f"## 🔬 Design Summary")
            lines.append(f"")
            lines.append(f"| Primer | Sequence | Length | Tm | GC% |")
            lines.append(f"|--------|----------|--------|-----|-----|")
            
            fwd = report.design.forward_primer
            rev = report.design.reverse_primer
            
            lines.append(f"| Forward | `{fwd.sequence}` | {fwd.length}bp | {fwd.tm:.1f}°C | {fwd.gc_percent:.1f}% |")
            lines.append(f"| Reverse | `{rev.sequence}` | {rev.length}bp | {rev.tm:.1f}°C | {rev.gc_percent:.1f}% |")
            
            if report.design.product_size:
                lines.append(f"")
                lines.append(f"**Product Size:** {report.design.product_size}bp")
            
            lines.append(f"")
        
        # Validation Summary
        if report.validation.validated:
            lines.append(f"## ✅ Validation")
            lines.append(f"")
            lines.append(f"- **Amplicons Predicted:** {report.validation.amplicons_predicted}")
            if report.validation.primary_product_size:
                lines.append(f"- **Primary Product:** {report.validation.primary_product_size}bp")
            lines.append(f"- **PCR Success:** {report.validation.pcr_success_probability*100:.0f}%")
            lines.append(f"")
        
        # Off-target Summary
        if report.offtarget.checked:
            lines.append(f"## 🎯 Off-target Analysis")
            lines.append(f"")
            lines.append(f"- **Database:** {report.offtarget.database or 'N/A'}")
            lines.append(f"- **Forward Hits:** {report.offtarget.forward_hits}")
            lines.append(f"- **Reverse Hits:** {report.offtarget.reverse_hits}")
            lines.append(f"- **Specificity Grade:** **{report.offtarget.combined_grade}** ({report.offtarget.specificity_score:.1f}/100)")
            lines.append(f"")
        
        # Warnings
        if report.warnings:
            lines.append(f"## ⚠️ Warnings")
            lines.append(f"")
            for w in report.warnings:
                lines.append(f"- {w}")
            lines.append(f"")
        
        # Recommendations
        if report.recommendations:
            lines.append(f"## 💡 Recommendations")
            lines.append(f"")
            for r in report.recommendations:
                lines.append(f"- {r}")
            lines.append(f"")
        
        lines.append(f"---")
        lines.append(f"*Generated by PrimerLab v{report.primerlab_version}*")
        
        return "\n".join(lines)
    
    def to_json(self) -> str:
        """Generate JSON report."""
        return json.dumps(self.report.to_dict(), indent=2, default=str)
    
    def save(self, path: str, format: ReportFormat = ReportFormat.MARKDOWN):
        """
        Save report to file.
        
        Args:
            path: Output file path
            format: Report format
        """
        content = ""
        
        if format == ReportFormat.MARKDOWN:
            content = self.to_markdown()
        elif format == ReportFormat.JSON:
            content = self.to_json()
        elif format == ReportFormat.HTML:
            # TODO: Implement in Phase 3
            content = f"<html><body><pre>{self.to_markdown()}</pre></body></html>"
        
        Path(path).write_text(content, encoding="utf-8")


def generate_report(workflow_result: Any) -> PrimerReport:
    """
    Convenience function to generate report from workflow result.
    
    Args:
        workflow_result: Result from PCR workflow
        
    Returns:
        PrimerReport
    """
    generator = ReportGenerator()
    generator.from_workflow_result(workflow_result)
    return generator.generate()
