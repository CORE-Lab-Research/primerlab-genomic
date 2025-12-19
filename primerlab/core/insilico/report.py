"""
In-silico PCR Report Generator (v0.2.2)

Generates human-readable reports from in-silico PCR results.
"""

from pathlib import Path
from typing import Optional
from datetime import datetime

from primerlab.core.insilico.engine import InsilicoPCRResult, AmpliconPrediction, PrimerBinding


def generate_markdown_report(result: InsilicoPCRResult, output_dir: Optional[Path] = None) -> str:
    """
    Generate a markdown report from in-silico PCR results.
    
    Args:
        result: InsilicoPCRResult from run_insilico_pcr
        output_dir: Optional directory to save report file
        
    Returns:
        Markdown string
    """
    lines = []
    
    # Header
    lines.append("# In-silico PCR Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Parameter | Value |")
    lines.append("|-----------|-------|")
    lines.append(f"| Template | {result.template_name} |")
    lines.append(f"| Template Length | {result.template_length:,} bp |")
    lines.append(f"| Forward Primer | `{result.forward_primer}` |")
    lines.append(f"| Reverse Primer | `{result.reverse_primer}` |")
    lines.append(f"| Products Found | {len(result.products)} |")
    lines.append(f"| Success | {'✅ Yes' if result.success else '❌ No'} |")
    lines.append("")
    
    # Binding Sites Summary
    lines.append("## Binding Sites")
    lines.append("")
    lines.append(f"- **Forward primer bindings:** {len(result.all_forward_bindings)}")
    lines.append(f"- **Reverse primer bindings:** {len(result.all_reverse_bindings)}")
    lines.append("")
    
    # Products
    if result.products:
        lines.append("## Predicted Products")
        lines.append("")
        
        for i, product in enumerate(result.products, 1):
            primary_badge = " 🏆 **PRIMARY**" if product.is_primary else ""
            lines.append(f"### Product {i}{primary_badge}")
            lines.append("")
            lines.append(f"| Property | Value |")
            lines.append("|----------|-------|")
            lines.append(f"| Size | **{product.product_size} bp** |")
            lines.append(f"| Position | {product.start_position} - {product.end_position} |")
            lines.append(f"| Likelihood | {product.likelihood_score:.1f}% |")
            lines.append("")
            
            # Binding details
            lines.append("**Forward Binding:**")
            lines.append(_format_binding(product.forward_binding))
            lines.append("")
            
            lines.append("**Reverse Binding:**")
            lines.append(_format_binding(product.reverse_binding))
            lines.append("")
            
            # Alignment visualization
            lines.append("**Alignment:**")
            lines.append("```")
            lines.append(_generate_alignment_view(product, result.forward_primer, result.reverse_primer))
            lines.append("```")
            lines.append("")
            
            # Product sequence (truncated)
            seq = product.product_sequence
            if len(seq) > 100:
                lines.append(f"**Sequence Preview:** `{seq[:50]}...{seq[-50:]}`")
            else:
                lines.append(f"**Sequence:** `{seq}`")
            lines.append("")
            
            if product.warnings:
                lines.append("⚠️ **Warnings:**")
                for w in product.warnings:
                    lines.append(f"- {w}")
                lines.append("")
    else:
        lines.append("## Predicted Products")
        lines.append("")
        lines.append("**No products predicted.** Check primer binding or adjust parameters.")
        lines.append("")
    
    # Warnings & Errors
    if result.warnings:
        lines.append("## ⚠️ Warnings")
        lines.append("")
        for w in result.warnings:
            lines.append(f"- {w}")
        lines.append("")
    
    if result.errors:
        lines.append("## ❌ Errors")
        lines.append("")
        for e in result.errors:
            lines.append(f"- {e}")
        lines.append("")
    
    # Parameters
    lines.append("## Parameters Used")
    lines.append("")
    lines.append("```yaml")
    for k, v in result.parameters.items():
        lines.append(f"{k}: {v}")
    lines.append("```")
    lines.append("")
    
    report = "\n".join(lines)
    
    # Save if output_dir provided
    if output_dir:
        output_path = Path(output_dir) / "insilico_report.md"
        output_path.write_text(report, encoding="utf-8")
    
    return report


def _format_binding(binding: PrimerBinding) -> str:
    """Format binding details as markdown list."""
    valid_icon = "✅" if binding.is_valid else "⚠️"
    return (
        f"- Position: {binding.position} ({binding.strand} strand)\n"
        f"- Match: {binding.match_percent:.1f}% ({binding.mismatches} mismatches)\n"
        f"- 3' Match: {binding.three_prime_match} bp\n"
        f"- Binding Tm: {binding.binding_tm:.1f}°C\n"
        f"- Valid: {valid_icon}"
    )


def _generate_alignment_view(product: AmpliconPrediction, fwd_seq: str, rev_seq: str) -> str:
    """Generate ASCII alignment visualization."""
    fwd = product.forward_binding
    rev = product.reverse_binding
    
    # Calculate positions
    fwd_pos = fwd.position
    rev_pos = rev.position
    
    # Create simple visualization
    lines = []
    
    # Forward primer
    fwd_arrow = "5'─" + "─" * min(20, len(fwd_seq)) + "→3'"
    lines.append(f"FWD @ {fwd_pos:>6}: {fwd_arrow}  ({fwd.match_percent:.0f}% match)")
    
    # Template representation
    template_line = "Template:    " + "═" * 40
    lines.append(template_line)
    
    # Reverse primer
    rev_arrow = "3'←" + "─" * min(20, len(rev_seq)) + "─5'"
    lines.append(f"REV @ {rev_pos:>6}:                    {rev_arrow}  ({rev.match_percent:.0f}% match)")
    
    # Product info
    lines.append("")
    lines.append(f"Product: {product.product_size} bp  [{fwd_pos} → {rev_pos}]")
    
    return "\n".join(lines)


def generate_amplicon_fasta(result: InsilicoPCRResult, output_dir: Optional[Path] = None) -> str:
    """
    Generate FASTA file with predicted amplicon sequences.
    
    Args:
        result: InsilicoPCRResult from run_insilico_pcr
        output_dir: Optional directory to save FASTA file
        
    Returns:
        FASTA string
    """
    lines = []
    
    for i, product in enumerate(result.products, 1):
        primary_tag = "_PRIMARY" if product.is_primary else ""
        header = (
            f">{result.template_name}_amplicon{i}{primary_tag} "
            f"size={product.product_size}bp "
            f"pos={product.start_position}-{product.end_position} "
            f"likelihood={product.likelihood_score:.1f}%"
        )
        lines.append(header)
        
        # Wrap sequence at 60 chars
        seq = product.product_sequence
        for j in range(0, len(seq), 60):
            lines.append(seq[j:j+60])
    
    fasta = "\n".join(lines)
    
    # Save if output_dir provided
    if output_dir:
        output_path = Path(output_dir) / "predicted_amplicons.fasta"
        output_path.write_text(fasta, encoding="utf-8")
    
    return fasta


def format_console_alignment(result: InsilicoPCRResult) -> str:
    """
    Generate enhanced console output with alignment visualization.
    
    Args:
        result: InsilicoPCRResult from run_insilico_pcr
        
    Returns:
        Formatted string for console output
    """
    lines = []
    
    lines.append("")
    lines.append("=" * 60)
    lines.append("  IN-SILICO PCR RESULTS")
    lines.append("=" * 60)
    lines.append("")
    
    # Summary
    lines.append(f"Template: {result.template_name} ({result.template_length:,} bp)")
    lines.append(f"Forward:  {result.forward_primer}")
    lines.append(f"Reverse:  {result.reverse_primer}")
    lines.append("")
    
    # Binding summary
    lines.append(f"Forward bindings: {len(result.all_forward_bindings)}")
    lines.append(f"Reverse bindings: {len(result.all_reverse_bindings)}")
    lines.append("")
    
    if result.products:
        lines.append("-" * 60)
        lines.append(f"  PREDICTED PRODUCTS: {len(result.products)}")
        lines.append("-" * 60)
        
        for i, product in enumerate(result.products, 1):
            primary = " ★" if product.is_primary else ""
            lines.append("")
            lines.append(f"Product {i}{primary}:")
            lines.append(f"  Size:       {product.product_size} bp")
            lines.append(f"  Position:   {product.start_position} → {product.end_position}")
            lines.append(f"  Likelihood: {product.likelihood_score:.1f}%")
            
            # Compact alignment
            fwd = product.forward_binding
            rev = product.reverse_binding
            lines.append(f"  FWD bind:   pos {fwd.position}, {fwd.match_percent:.0f}% match, 3'={fwd.three_prime_match}bp")
            lines.append(f"  REV bind:   pos {rev.position}, {rev.match_percent:.0f}% match, 3'={rev.three_prime_match}bp")
            
            if product.warnings:
                for w in product.warnings:
                    lines.append(f"  ⚠️ {w}")
    else:
        lines.append("No products predicted.")
    
    lines.append("")
    lines.append("=" * 60)
    
    if result.warnings:
        lines.append("Warnings:")
        for w in result.warnings:
            lines.append(f"  ⚠️ {w}")
    
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  ❌ {e}")
    
    return "\n".join(lines)
