"""
CLI Output Formatter (v0.3.2)

Rich/colored console output for PrimerLab CLI.
"""

import sys
from typing import Optional, List, Any
from dataclasses import dataclass
from enum import Enum


class OutputLevel(Enum):
    """Output verbosity levels."""
    QUIET = 0
    NORMAL = 1
    VERBOSE = 2
    DEBUG = 3


# ANSI color codes
class Color:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    
    @classmethod
    def disable(cls):
        """Disable colors (for non-terminal output)."""
        for attr in dir(cls):
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str):
                setattr(cls, attr, "")


# Check if terminal supports colors
def supports_color() -> bool:
    """Check if the terminal supports ANSI colors."""
    if not hasattr(sys.stdout, 'isatty'):
        return False
    if not sys.stdout.isatty():
        return False
    return True


# Disable colors if not supported
if not supports_color():
    Color.disable()


class CLIFormatter:
    """
    Formatted CLI output with colors and structure.
    """
    
    def __init__(self, level: OutputLevel = OutputLevel.NORMAL):
        """
        Initialize formatter.
        
        Args:
            level: Output verbosity level
        """
        self.level = level
    
    def _should_print(self, min_level: OutputLevel) -> bool:
        """Check if output should be printed based on level."""
        return self.level.value >= min_level.value
    
    def header(self, text: str, emoji: str = "🔬"):
        """Print a section header."""
        if self._should_print(OutputLevel.NORMAL):
            print(f"\n{emoji} {Color.BOLD}{text}{Color.RESET}")
    
    def subheader(self, text: str):
        """Print a subsection header."""
        if self._should_print(OutputLevel.NORMAL):
            print(f"   {Color.CYAN}{text}{Color.RESET}")
    
    def success(self, text: str):
        """Print success message."""
        if self._should_print(OutputLevel.QUIET):
            print(f"{Color.GREEN}✅ {text}{Color.RESET}")
    
    def error(self, text: str):
        """Print error message."""
        print(f"{Color.RED}❌ {text}{Color.RESET}", file=sys.stderr)
    
    def warning(self, text: str):
        """Print warning message."""
        if self._should_print(OutputLevel.NORMAL):
            print(f"{Color.YELLOW}⚠️  {text}{Color.RESET}")
    
    def info(self, text: str):
        """Print info message."""
        if self._should_print(OutputLevel.NORMAL):
            print(f"   {text}")
    
    def detail(self, text: str):
        """Print verbose detail."""
        if self._should_print(OutputLevel.VERBOSE):
            print(f"   {Color.GRAY}{text}{Color.RESET}")
    
    def debug(self, text: str):
        """Print debug message."""
        if self._should_print(OutputLevel.DEBUG):
            print(f"   {Color.DIM}[DEBUG] {text}{Color.RESET}")
    
    def grade(self, grade: str, score: float):
        """Print specificity grade with color."""
        color = self._grade_color(grade)
        if self._should_print(OutputLevel.QUIET):
            print(f"\n{color}{Color.BOLD}Grade: {grade} ({score:.1f}){Color.RESET}")
    
    def _grade_color(self, grade: str) -> str:
        """Get color for grade."""
        colors = {
            "A": Color.GREEN,
            "B": Color.CYAN,
            "C": Color.YELLOW,
            "D": Color.MAGENTA,
            "F": Color.RED
        }
        return colors.get(grade, Color.WHITE)
    
    def table_row(self, label: str, value: Any, color: Optional[str] = None):
        """Print a table-like row."""
        if self._should_print(OutputLevel.NORMAL):
            val_str = str(value)
            if color:
                val_str = f"{color}{val_str}{Color.RESET}"
            print(f"   {label:.<20} {val_str}")
    
    def divider(self):
        """Print a divider line."""
        if self._should_print(OutputLevel.NORMAL):
            print(f"   {Color.GRAY}{'─' * 40}{Color.RESET}")
    
    def blank(self):
        """Print blank line."""
        if self._should_print(OutputLevel.NORMAL):
            print()
    
    def spinner_start(self, text: str):
        """Print spinner start (simple version)."""
        if self._should_print(OutputLevel.NORMAL):
            print(f"   ⏳ {text}...", end="", flush=True)
    
    def spinner_end(self, success: bool = True):
        """Print spinner end."""
        if self._should_print(OutputLevel.NORMAL):
            if success:
                print(f" {Color.GREEN}✓{Color.RESET}")
            else:
                print(f" {Color.RED}✗{Color.RESET}")


def get_formatter(verbose: bool = False, quiet: bool = False) -> CLIFormatter:
    """
    Get CLI formatter based on flags.
    
    Args:
        verbose: Enable verbose output
        quiet: Enable quiet mode
        
    Returns:
        CLIFormatter instance
    """
    if quiet:
        level = OutputLevel.QUIET
    elif verbose:
        level = OutputLevel.VERBOSE
    else:
        level = OutputLevel.NORMAL
    
    return CLIFormatter(level)
