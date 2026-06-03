"""
Base Report Template for PrimerLab Reports.

Provides standardized sections and formatting for all workflow reports.
v0.9.3+ - Report Standardization
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from primerlab.core.models import WorkflowResult, Primer, Amplicon, QCResult


class BaseReportTemplate:
    """
    Base class providing standardized report sections.
    
    All workflow-specific reports should inherit from this
    to ensure consistent formatting.
    """
    
    def __init__(self, result: WorkflowResult):
        self.result = result
        self.lines: List[str] = []
    
    def generate_header(self, title: str) -> None:
        """Generate standardized report header."""
        self.lines.append(f"# {title}")
        self.lines.append("")
        self.lines.append(f"> **Generated:** {self.result.metadata.timestamp}")
        self.lines.append(f"> **Version:** PrimerLab {self.result.metadata.version}")
        self.lines.append("")
        self.lines.append("---")
        self.lines.append("")
    
    def generate_executive_summary(self) -> None:
        """Generate executive summary with key metrics."""
        self.lines.append("## 1. Executive Summary")
        self.lines.append("")
        
        # Calculate metrics
        primers_found = len(self.result.primers) if self.result.primers else 0
        
        # Quality score
        quality_display = "N/A"
        if self.result.qc and self.result.qc.quality_score is not None:
            emoji = self.result.qc.quality_category_emoji or "🔵"
            category = self.result.qc.quality_category or "Unknown"
            quality_display = f"{emoji} {self.result.qc.quality_score}/100 ({category})"
        
        # Amplicon size
        amp_size = "N/A"
        if self.result.amplicons:
            amp_size = f"{self.result.amplicons[0].length} bp"
        
        # QC Status
        qc_status = "⚠️ N/A"
        if self.result.qc:
            if self.result.qc.errors:
                qc_status = f"❌ FAIL ({len(self.result.qc.errors)} errors)"
            elif self.result.qc.warnings:
                qc_status = f"⚠️ WARNING ({len(self.result.qc.warnings)} issues)"
            else:
                qc_status = "✅ PASS"
        
        self.lines.append("| Metric | Value |")
        self.lines.append("|:-------|------:|")
        self.lines.append(f"| **Primers Found** | {primers_found} |")
        self.lines.append(f"| **Quality Score** | {quality_display} |")
        self.lines.append(f"| **Amplicon Size** | {amp_size} |")
        self.lines.append(f"| **QC Status** | {qc_status} |")
        self.lines.append("")
    
    def generate_input_parameters(self) -> None:
        """Generate input parameters section."""
        self.lines.append("---")
        self.lines.append("")
        self.lines.append("## 2. Input Parameters")
        self.lines.append("")
        
        params = self.result.metadata.parameters or {}
        
        self.lines.append("| Parameter | Value |")
        self.lines.append("|:----------|------:|")
        
        # Tm settings
        tm = params.get("tm", {})
        if tm:
            self.lines.append(f"| **Target Tm** | {tm.get('opt', 'N/A')}°C |")
        
        # Product size
        product = params.get("product_size", {})
        if product:
            min_size = product.get("min", "?")
            max_size = product.get("max", "?")
            self.lines.append(f"| **Product Size** | {min_size}-{max_size} bp |")
        
        # Primer size
        primer_size = params.get("primer_size", {})
        if primer_size:
            min_len = primer_size.get("min", "?")
            max_len = primer_size.get("max", "?")
            self.lines.append(f"| **Primer Length** | {min_len}-{max_len} bp |")
        
        # Probe (qPCR)
        probe = params.get("probe", {})
        if probe:
            probe_tm = probe.get("tm", {}).get("opt", "N/A")
            self.lines.append(f"| **Probe Tm** | {probe_tm}°C |")
        
        self.lines.append("")
    
    def generate_primer_table(self) -> None:
        """Generate standardized primer table."""
        self.lines.append("---")
        self.lines.append("")
        self.lines.append("## 3. Best Primer Set")
        self.lines.append("")
        
        if not self.result.primers:
            self.lines.append("> ⚠️ **No valid primers found.**")
            self.lines.append("")
            return
        
        fwd = self.result.primers.get("forward")
        rev = self.result.primers.get("reverse")
        probe = self.result.primers.get("probe")
        
        # Build table header
        cols = ["Property", "Forward", "Reverse"]
        if probe:
            cols.append("Probe")
        
        self.lines.append("| " + " | ".join(cols) + " |")
        self.lines.append("| " + " | ".join([":---"] * len(cols)) + " |")
        
        def row(label: str, fwd_val: str, rev_val: str, probe_val: str = None) -> str:
            r = f"| **{label}** | {fwd_val} | {rev_val} |"
            if probe:
                r += f" {probe_val or 'N/A'} |"
            return r
        
        # Sequence
        self.lines.append(row(
            "Sequence",
            f"`{fwd.sequence}`" if fwd else "N/A",
            f"`{rev.sequence}`" if rev else "N/A",
            f"`{getattr(probe, 'labeled_sequence', None) or probe.sequence}`" if probe else None
        ))
        
        # Length
        self.lines.append(row(
            "Length",
            f"{fwd.length} bp" if fwd else "N/A",
            f"{rev.length} bp" if rev else "N/A",
            f"{probe.length} bp" if probe else None
        ))
        
        # Tm
        self.lines.append(row(
            "Tm",
            f"{fwd.tm:.2f}°C" if fwd and fwd.tm is not None else "N/A",
            f"{rev.tm:.2f}°C" if rev and rev.tm is not None else "N/A",
            f"{probe.tm:.2f}°C" if probe and probe.tm is not None else None
        ))
        
        # GC%
        self.lines.append(row(
            "GC%",
            f"{fwd.gc:.1f}%" if fwd and fwd.gc is not None else "N/A",
            f"{rev.gc:.1f}%" if rev and rev.gc is not None else "N/A",
            f"{probe.gc:.1f}%" if probe and probe.gc is not None else None
        ))
        
        # Position
        self.lines.append(row(
            "Position",
            f"{fwd.start}" if fwd and fwd.start is not None else "N/A",
            f"{rev.start}" if rev and rev.start is not None else "N/A",
            f"{probe.start}" if probe and probe.start is not None else None
        ))
        
        self.lines.append("")
    
    def generate_amplicon_visualization(self) -> None:
        """Generate ASCII amplicon visualization."""
        self.lines.append("---")
        self.lines.append("")
        self.lines.append("## 4. Amplicon Visualization")
        self.lines.append("")
        
        if not self.result.amplicons or not self.result.primers:
            self.lines.append("> No amplicon data available.")
            self.lines.append("")
            return
        
        fwd = self.result.primers.get("forward")
        rev = self.result.primers.get("reverse")
        amp = self.result.amplicons[0]
        
        if not fwd or not rev:
            self.lines.append("> Incomplete primer data for visualization.")
            self.lines.append("")
            return
        
        self.lines.append("```")
        
        # Build visualization
        max_width = 50
        fwd_arrow = "[FWD>>>]"
        rev_arrow = "[<<<REV]"
        middle_len = max(10, max_width - len(fwd_arrow) - len(rev_arrow))
        amplicon_line = "═" * middle_len
        
        line1 = f"5'───{fwd_arrow}{amplicon_line}{rev_arrow}───3'"
        self.lines.append(line1)
        
        # Position markers
        fwd_pos = f"↑ {fwd.start}" if fwd.start is not None else "↑ ?"
        rev_end = rev.end if hasattr(rev, 'end') and rev.end is not None else "?"
        rev_pos = f"↑ {rev_end}"
        
        marker_line = " " * 8 + fwd_pos + " " * (len(line1) - 16 - len(fwd_pos) - len(rev_pos)) + rev_pos
        self.lines.append(marker_line)
        
        # Amplicon size
        amp_len = amp.length if amp.length else "?"
        center_text = f"Amplicon: {amp_len} bp"
        center_pos = (len(line1) - len(center_text)) // 2
        self.lines.append(" " * center_pos + center_text)
        
        self.lines.append("```")
        self.lines.append("")
    
    def generate_qc_section(self) -> None:
        """Generate quality control section."""
        self.lines.append("---")
        self.lines.append("")
        self.lines.append("## 5. Quality Control")
        self.lines.append("")
        
        if not self.result.qc:
            self.lines.append("> ⚠️ No QC data available.")
            self.lines.append("")
            return
        
        qc = self.result.qc
        
        self.lines.append("| Check | Result | Value |")
        self.lines.append("|:------|:------:|:------|")
        
        # Tm Balance
        tm_status = "✅ PASS" if qc.tm_balance_ok else "⚠️ FAIL"
        self.lines.append(f"| **Tm Balance** | {tm_status} | Δ{qc.tm_diff:.2f}°C |")
        
        # Hairpin
        hairpin_status = "✅ PASS" if qc.hairpin_ok else "⚠️ FAIL"
        self.lines.append(f"| **Hairpin ΔG** | {hairpin_status} | {qc.hairpin_dg:.2f} kcal/mol |")
        
        # Homodimer
        homodimer_status = "✅ PASS" if qc.homodimer_ok else "⚠️ FAIL"
        self.lines.append(f"| **Homodimer ΔG** | {homodimer_status} | {qc.homodimer_dg:.2f} kcal/mol |")
        
        # Heterodimer (if available)
        if hasattr(qc, 'heterodimer_ok') and hasattr(qc, 'heterodimer_dg'):
            hetero_status = "✅ PASS" if qc.heterodimer_ok else "⚠️ FAIL"
            self.lines.append(f"| **Heterodimer ΔG** | {hetero_status} | {qc.heterodimer_dg:.2f} kcal/mol |")
        
        self.lines.append("")
        
        # Warnings
        if qc.warnings:
            self.lines.append("### ⚠️ Warnings")
            self.lines.append("")
            for warning in qc.warnings:
                self.lines.append(f"- {warning}")
            self.lines.append("")
        
        # Errors
        if qc.errors:
            self.lines.append("### ❌ Errors")
            self.lines.append("")
            for error in qc.errors:
                self.lines.append(f"- {error}")
            self.lines.append("")
    
    def generate_alternatives(self) -> None:
        """Generate alternative primers section if available."""
        if not hasattr(self.result, 'alternatives') or not self.result.alternatives:
            return
        
        self.lines.append("---")
        self.lines.append("")
        self.lines.append("## 6. Alternative Candidates")
        self.lines.append("")
        self.lines.append("*Other high-quality candidates evaluated:*")
        self.lines.append("")
        
        self.lines.append("| Rank | Forward | Reverse | Score | Status |")
        self.lines.append("|:----:|:--------|:--------|------:|:------:|")
        
        for i, alt in enumerate(self.result.alternatives, start=2):
            fwd_seq = alt.get("fwd_seq") or alt.get("primers", {}).get("forward", {}).get("sequence", "")
            fwd_disp = fwd_seq[:12] + "..." if len(fwd_seq) > 12 else fwd_seq
            
            rev_seq = alt.get("rev_seq") or alt.get("primers", {}).get("reverse", {}).get("sequence", "")
            rev_disp = rev_seq[:12] + "..." if len(rev_seq) > 12 else rev_seq
            
            penalty = alt.get("primer3_penalty") or alt.get("p3_penalty") or alt.get("final_score", 0.0)
            
            if "passes_qc" in alt:
                qc_ok = alt["passes_qc"]
            else:
                qc = alt.get("qc", {})
                qc_ok = not (qc.get("errors") or qc.get("warnings"))
            
            status = "✅" if qc_ok else "⚠️"
            
            self.lines.append(f"| #{i} | `{fwd_disp}` | `{rev_disp}` | {penalty:.2f} | {status} |")
        
        self.lines.append("")
    
    def generate_footer(self) -> None:
        """Generate standardized footer."""
        self.lines.append("---")
        self.lines.append("")
        self.lines.append("*Generated by PrimerLab*")
    
    def build(self, title: str) -> str:
        """
        Build the complete report.
        
        Args:
            title: Report title (e.g., "PCR Primer Design Report")
        
        Returns:
            Complete markdown report string.
        """
        self.lines = []
        
        self.generate_header(title)
        self.generate_executive_summary()
        self.generate_input_parameters()
        self.generate_primer_table()
        self.generate_amplicon_visualization()
        self.generate_qc_section()
        self.generate_alternatives()
        self.generate_footer()
        
        return "\n".join(self.lines)
