"""
Rich Console Output for PrimerLab v0.1.3

Provides colorized console output for better user experience.
"""

from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

# Custom theme for PrimerLab
PRIMERLAB_THEME = Theme({
    "info": "blue",
    "success": "green bold",
    "warning": "yellow",
    "error": "red bold",
    "highlight": "cyan",
    "title": "magenta bold",
})

console = Console(theme=PRIMERLAB_THEME)


def print_header(text: str):
    """Print a styled header."""
    console.print(f"\n[title]═══ {text} ═══[/title]")


def print_success(text: str):
    """Print a success message."""
    console.print(f"[success]✅ {text}[/success]")


def print_warning(text: str):
    """Print a warning message."""
    console.print(f"[warning]⚠️  {text}[/warning]")


def print_error(text: str):
    """Print an error message."""
    console.print(f"[error]❌ {text}[/error]")


def print_info(text: str):
    """Print an info message."""
    console.print(f"[info]ℹ️  {text}[/info]")


def print_primer_summary(result):
    """Print a summary table of designed primers."""
    if not result.primers:
        print_warning("No primers were designed.")
        return
    
    table = Table(title="[title]Primer Summary[/title]", show_header=True)
    table.add_column("Primer", style="cyan")
    table.add_column("Sequence", style="green")
    table.add_column("Tm (°C)", justify="right")
    table.add_column("GC%", justify="right")
    table.add_column("Length", justify="right")
    
    for name, primer in result.primers.items():
        table.add_row(
            name.capitalize(),
            primer.sequence[:20] + "..." if len(primer.sequence) > 20 else primer.sequence,
            f"{primer.tm:.1f}",
            f"{primer.gc:.1f}%",
            f"{primer.length} bp"
        )
    
    console.print(table)


def print_qc_status(result):
    """Print QC status with color coding."""
    if not result.qc:
        print_info("QC data not available.")
        return
    
    qc = result.qc
    
    if qc.errors:
        print_error(f"QC Status: FAIL ({len(qc.errors)} errors)")
        for err in qc.errors:
            console.print(f"  [error]• {err}[/error]")
    elif qc.warnings:
        print_warning(f"QC Status: WARNING ({len(qc.warnings)} warnings)")
        for warn in qc.warnings:
            console.print(f"  [warning]• {warn}[/warning]")
    else:
        print_success("QC Status: PASS")


def create_progress_bar():
    """Create a Rich progress bar for batch processing."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    )
