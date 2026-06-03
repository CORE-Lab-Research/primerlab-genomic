"""
PCR Report Generator using standardized template.
v0.9.3+ - Report Standardization
"""

from typing import Dict, Any
from primerlab.core.models import WorkflowResult
from primerlab.core.report.base_report import BaseReportTemplate


class ReportGenerator:
    """
    Generates a Markdown report for PCR workflow results.
    Uses standardized BaseReportTemplate for consistent formatting.
    """

    def generate_report(self, result: WorkflowResult) -> str:
        """
        Converts WorkflowResult into a Markdown string.
        """
        template = PCRReportTemplate(result)
        return template.build("PCR Primer Design Report")


class PCRReportTemplate(BaseReportTemplate):
    """
    PCR-specific report template extending base template.
    """
    
    def build(self, title: str) -> str:
        """Build PCR report with all standard sections + PCR-specific additions."""
        self.lines = []
        
        # Standard sections
        self.generate_header(title)
        self.generate_executive_summary()
        self.generate_input_parameters()
        self.generate_primer_table()
        self.generate_amplicon_visualization()
        self.generate_qc_section()
        
        # PCR-specific: Candidate statistics
        self.generate_candidate_statistics()
        
        # Standard sections continued
        self.generate_alternatives()
        
        # PCR-specific: Ranking rationale
        self.generate_ranking_rationale()
        
        self.generate_footer()
        
        return "\n".join(self.lines)
    
    def generate_candidate_statistics(self) -> None:
        """Generate Primer3 candidate statistics section."""
        if not hasattr(self.result, 'raw') or not self.result.raw:
            return
        
        left_explain = self.result.raw.get('PRIMER_LEFT_EXPLAIN', '')
        right_explain = self.result.raw.get('PRIMER_RIGHT_EXPLAIN', '')
        
        if not left_explain and not right_explain:
            return
        
        self.lines.append("---")
        self.lines.append("")
        self.lines.append("## 6. Primer Candidate Statistics")
        self.lines.append("")
        self.lines.append("*Why were some candidates rejected by Primer3?*")
        self.lines.append("")
        
        if left_explain:
            self.lines.append(f"**Forward Primer:** `{left_explain}`")
            self.lines.append("")
        if right_explain:
            self.lines.append(f"**Reverse Primer:** `{right_explain}`")
            self.lines.append("")
    
    def generate_ranking_rationale(self) -> None:
        """Generate ranking rationale for alternative primers."""
        if not hasattr(self.result, 'alternatives') or not self.result.alternatives:
            return
        
        self.lines.append("### Ranking Rationale")
        self.lines.append("")
        self.lines.append("*Why weren't alternatives selected as best?*")
        self.lines.append("")
        
        for i, alt in enumerate(self.result.alternatives, start=2):
            qc = alt.get("qc", {})
            reasons = alt.get("qc_details", {}).get("rejection_reasons", []) or qc.get("warnings", [])
            penalty = alt.get("primer3_penalty") or alt.get("p3_penalty") or 0.0
            
            if reasons:
                self.lines.append(f"- **#{i}:** {', '.join(reasons)}")
            else:
                self.lines.append(f"- **#{i}:** Higher Primer3 penalty ({penalty:.2f}) than best candidate")
        
        self.lines.append("")
