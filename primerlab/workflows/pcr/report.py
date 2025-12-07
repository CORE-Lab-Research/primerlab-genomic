from typing import Dict, Any
from primerlab.core.models import WorkflowResult

class ReportGenerator:
    """
    Generates a Markdown report for PCR/qPCR workflow results.
    """
    
    def generate_report(self, result: WorkflowResult) -> str:
        """
        Converts WorkflowResult into a Markdown string.
        """
        md = []
        
        # 1. Header
        md.append(f"# PrimerLab Report: {result.workflow.upper()}")
        md.append(f"**Date:** {result.metadata.timestamp}")
        md.append(f"**Version:** {result.metadata.version}")
        md.append("")
        
        # 2. Input Summary
        md.append("## 1. Input Summary")
        params = result.metadata.parameters
        md.append(f"- **Target Tm:** {params.get('tm', {}).get('opt')}°C")
        md.append(f"- **Target Size:** {params.get('primer_size', {}).get('opt')} bp")
        if "probe" in params:
             md.append(f"- **Probe Tm:** {params.get('probe', {}).get('tm', {}).get('opt')}°C")
        md.append("")
        
        # 2.5 Summary Statistics
        if result.primers:
            md.append("## Summary Statistics")
            fwd = result.primers.get("forward")
            rev = result.primers.get("reverse")
            
            if fwd and rev:
                avg_tm = (fwd.tm + rev.tm) / 2
                avg_gc = (fwd.gc + rev.gc) / 2
                tm_diff = abs(fwd.tm - rev.tm)
                
                # QC Status
                qc_status = "✅ PASS"
                if result.qc and result.qc.warnings:
                    qc_status = f"⚠️ WARNING ({len(result.qc.warnings)} issues)"
                if result.qc and result.qc.errors:
                    qc_status = f"❌ FAIL ({len(result.qc.errors)} errors)"
                
                md.append("| Metric | Value |")
                md.append("|:-------|------:|")
                md.append(f"| **Primers Found** | {len(result.primers)} |")
                md.append(f"| **Average Tm** | {avg_tm:.1f}°C |")
                md.append(f"| **Tm Difference** | {tm_diff:.1f}°C |")
                md.append(f"| **Average GC%** | {avg_gc:.1f}% |")
                if result.amplicons:
                    md.append(f"| **Amplicon Size** | {result.amplicons[0].length} bp |")
                md.append(f"| **QC Status** | {qc_status} |")
                md.append("")

        # 3. Primer Results
        md.append("## 2. Best Primer Set")
        
        if not result.primers:
            md.append("> **No valid primers found.**")
            return "\n".join(md)

        fwd = result.primers.get("forward")
        rev = result.primers.get("reverse")
        probe = result.primers.get("probe")
        
        # Table for Primers
        cols = ["Property", "Forward Primer", "Reverse Primer"]
        if probe:
            cols.append("Probe")
            
        header = "| " + " | ".join(cols) + " |"
        separator = "| " + " | ".join([":---"] * len(cols)) + " |"
        
        md.append(header)
        md.append(separator)
        
        def row(label, f_val, r_val, p_val=None):
            r = f"| **{label}** | {f_val} | {r_val} |"
            if probe:
                r += f" {p_val} |"
            return r

        md.append(row("ID", f"`{fwd.id}`", f"`{rev.id}`", f"`{probe.id}`" if probe else ""))
        md.append(row("Sequence", f"`{fwd.sequence}`", f"`{rev.sequence}`", f"`{probe.sequence}`" if probe else ""))
        md.append(row("Length", f"{fwd.length} bp", f"{rev.length} bp", f"{probe.length} bp" if probe else ""))
        md.append(row("Tm", f"{fwd.tm:.2f}°C", f"{rev.tm:.2f}°C", f"{probe.tm:.2f}°C" if probe else ""))
        md.append(row("GC", f"{fwd.gc:.1f}%", f"{rev.gc:.1f}%", f"{probe.gc:.1f}%" if probe else ""))
        md.append(row("Position", f"{fwd.start}", f"{rev.start}", f"{probe.start}" if probe else ""))
        md.append("")
        
        # 4. Amplicon Info
        if result.amplicons:
            amp = result.amplicons[0]
            md.append("### Amplicon Details")
            md.append(f"- **Product Size:** {amp.length} bp")
            md.append(f"- **Position:** {amp.start} - {amp.end}")
            md.append("")
            
            # ASCII Amplicon Visualizer
            md.append("### Amplicon Visualization")
            md.append("```")
            visualizer = self._generate_ascii_amplicon(fwd, rev, amp)
            md.append(visualizer)
            md.append("```")
            md.append("")

        # 5. QC Evaluation
        md.append("## 3. QC Evaluation")
        if result.qc:
            qc = result.qc
            
            # Status Badge
            status = "✅ PASS" if not qc.warnings and not qc.errors else "⚠️ WARNING"
            if qc.errors: status = "❌ FAIL"
            
            md.append(f"**Overall Status:** {status}")
            md.append("")
            
            md.append("| Metric | Value | Status |")
            md.append("| :--- | :--- | :--- |")
            md.append(f"| **Tm Difference** | {qc.tm_diff:.2f}°C | {'✅' if qc.tm_balance_ok else '⚠️'} |")
            md.append(f"| **Hairpin ΔG** | {qc.hairpin_dg:.2f} | {'✅' if qc.hairpin_ok else '⚠️'} |")
            md.append(f"| **Homodimer ΔG** | {qc.homodimer_dg:.2f} | {'✅' if qc.homodimer_ok else '⚠️'} |")
            
            if qc.warnings:
                md.append("")
                md.append("### Warnings")
                for w in qc.warnings:
                    md.append(f"- ⚠️ {w}")
        else:
            md.append("QC data not available.")
        
        # 6. Rejected Candidates Log
        if hasattr(result, 'raw') and result.raw:
            left_explain = result.raw.get('PRIMER_LEFT_EXPLAIN', '')
            right_explain = result.raw.get('PRIMER_RIGHT_EXPLAIN', '')
            
            if left_explain or right_explain:
                md.append("")
                md.append("## 4. Primer Candidate Statistics")
                md.append("*Why were some candidates rejected by Primer3?*")
                md.append("")
                
                if left_explain:
                    md.append(f"**Forward Primer Candidates:** `{left_explain}`")
                if right_explain:
                    md.append(f"**Reverse Primer Candidates:** `{right_explain}`")
                md.append("")
        
        # 7. Alternative Primers (v0.1.3)
        if hasattr(result, 'alternatives') and result.alternatives:
            md.append("")
            md.append("## 5. Alternative Primer Pairs")
            md.append("*Other high-quality candidates evaluated by ViennaRNA QC:*")
            md.append("")
            
            md.append("| Rank | Fwd Sequence | Rev Sequence | Primer3 Score | QC Status | Product |")
            md.append("|:----:|:-------------|:-------------|:-------------:|:---------:|--------:|")
            
            for i, alt in enumerate(result.alternatives, start=2):
                qc_status = "✅ PASS" if alt.get("passes_qc", False) else "⚠️ FAIL"
                fwd_seq = alt.get("fwd_seq", "")[:15] + "..." if len(alt.get("fwd_seq", "")) > 15 else alt.get("fwd_seq", "")
                rev_seq = alt.get("rev_seq", "")[:15] + "..." if len(alt.get("rev_seq", "")) > 15 else alt.get("rev_seq", "")
                penalty = alt.get("primer3_penalty", 0.0)
                product = alt.get("product_size", "N/A")
                
                md.append(f"| #{i} | `{fwd_seq}` | `{rev_seq}` | {penalty:.2f} | {qc_status} | {product} bp |")
            
            # Ranking Rationale
            md.append("")
            md.append("### Ranking Rationale")
            md.append("*Why weren't alternatives selected as best?*")
            md.append("")
            
            for i, alt in enumerate(result.alternatives, start=2):
                reasons = alt.get("qc_details", {}).get("rejection_reasons", [])
                penalty = alt.get("primer3_penalty", 0.0)
                
                if reasons:
                    md.append(f"- **#{i}:** {', '.join(reasons)}")
                else:
                    md.append(f"- **#{i}:** Higher Primer3 penalty ({penalty:.2f}) than best candidate")
            
            md.append("")
        
        md.append("")
        md.append("---")
        md.append("*Generated by PrimerLab*")
        
        return "\n".join(md)
    
    def _generate_ascii_amplicon(self, fwd, rev, amp) -> str:
        """
        Generates an ASCII visualization of primer positioning.
        
        Example output:
        5'─────[FWD PRIMER>>>]══════════════════[<<<REV PRIMER]─────3'
                 ↑ 45                                    ↑ 214
                              Amplicon: 169 bp
        """
        # Scale factor: max width 60 chars for amplicon region
        max_width = 50
        amp_len = amp.length if amp.length else 100
        
        # Calculate proportional lengths
        fwd_len = min(len(fwd.sequence), 15)  # Max 15 chars for primer display
        rev_len = min(len(rev.sequence), 15)
        
        # Amplicon middle section
        middle_len = max(10, max_width - fwd_len - rev_len)
        
        # Build visualization
        lines = []
        
        # Line 1: Primer arrows
        fwd_arrow = f"[FWD>>>]"
        rev_arrow = f"[<<<REV]"
        amplicon_line = "═" * middle_len
        
        line1 = f"5'───{fwd_arrow}{amplicon_line}{rev_arrow}───3'"
        lines.append(line1)
        
        # Line 2: Position markers
        fwd_pos = f"↑ {fwd.start}" if fwd.start else "↑ ?"
        rev_pos = f"↑ {rev.end}" if rev.end else "↑ ?"
        
        # Calculate spacing
        fwd_marker_pos = 5 + len(fwd_arrow) // 2
        rev_marker_pos = len(line1) - 5 - len(rev_arrow) // 2
        
        marker_line = " " * fwd_marker_pos + fwd_pos
        marker_line += " " * (rev_marker_pos - len(marker_line)) + rev_pos
        lines.append(marker_line)
        
        # Line 3: Amplicon size
        center_text = f"Amplicon: {amp_len} bp"
        center_pos = (len(line1) - len(center_text)) // 2
        lines.append(" " * center_pos + center_text)
        
        return "\n".join(lines)
