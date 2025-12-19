"""
In-silico PCR Simulation Module (v0.2.2)

Virtual PCR simulation for amplicon prediction and primer validation.
"""

from primerlab.core.insilico.engine import InsilicoPCR, run_insilico_pcr
from primerlab.core.insilico.binding import BindingSite, analyze_binding
from primerlab.core.insilico.report import (
    generate_markdown_report,
    generate_amplicon_fasta,
    format_console_alignment
)

__all__ = [
    "InsilicoPCR",
    "run_insilico_pcr",
    "BindingSite",
    "analyze_binding",
    "generate_markdown_report",
    "generate_amplicon_fasta",
    "format_console_alignment",
]
