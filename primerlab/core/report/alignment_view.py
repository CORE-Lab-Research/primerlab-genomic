"""
Alignment View (v0.3.3)

ASCII visualization for primer-target alignments.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class AlignmentMatch:
    """Single alignment match info."""
    query_seq: str
    target_seq: str
    query_start: int
    query_end: int
    target_start: int
    target_end: int
    identity: float
    mismatches: int = 0
    gaps: int = 0
    orientation: str = "forward"  # forward or reverse


class AlignmentView:
    """
    Generate ASCII visualization of primer alignments.
    
    Examples:
        >>> view = AlignmentView()
        >>> print(view.format_alignment(primer, target))
        
        Position: 100-120
        Query:  5' ATGCGATCGATCGATCGATC 3'
                   ||||||||||||||||||||
        Target: 5' ATGCGATCGATCGATCGATC 3'
        
        Identity: 100% | Mismatches: 0 | Gaps: 0
    """
    
    # ANSI color codes
    COLORS = {
        "match": "\033[92m",      # Green
        "mismatch": "\033[91m",   # Red  
        "gap": "\033[93m",        # Yellow
        "reset": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m"
    }
    
    def __init__(self, use_colors: bool = True, line_width: int = 60):
        """
        Initialize alignment view.
        
        Args:
            use_colors: Use ANSI colors
            line_width: Max characters per line
        """
        self.use_colors = use_colors
        self.line_width = line_width
    
    def _colorize(self, text: str, color: str) -> str:
        """Add color to text if colors enabled."""
        if self.use_colors and color in self.COLORS:
            return f"{self.COLORS[color]}{text}{self.COLORS['reset']}"
        return text
    
    def format_alignment(self, match: AlignmentMatch) -> str:
        """
        Format a single alignment as ASCII art.
        
        Args:
            match: Alignment match data
            
        Returns:
            Formatted alignment string
        """
        lines = []
        
        # Header
        orient = "→" if match.orientation == "forward" else "←"
        lines.append(f"Position: {match.target_start}-{match.target_end} ({orient})")
        lines.append("")
        
        # Build match line
        query = match.query_seq.upper()
        target = match.target_seq.upper()
        match_line = ""
        
        for q, t in zip(query, target):
            if q == t:
                match_line += "|"
            elif q == "-" or t == "-":
                match_line += " "
            else:
                match_line += "×"
        
        # Format sequences with colors
        colored_query = self._format_seq_with_matches(query, target)
        
        # Orientation indicators
        if match.orientation == "forward":
            q_prefix = "Query:  5'"
            q_suffix = "3'"
            t_prefix = "Target: 5'"
            t_suffix = "3'"
        else:
            q_prefix = "Query:  3'"
            q_suffix = "5'"
            t_prefix = "Target: 3'"
            t_suffix = "5'"
        
        # Alignment display
        pad = " " * len("Query:  5'")
        lines.append(f"{q_prefix} {colored_query} {q_suffix}")
        lines.append(f"{pad} {match_line}")
        lines.append(f"{t_prefix} {target} {t_suffix}")
        lines.append("")
        
        # Stats
        identity_str = f"Identity: {match.identity:.1f}%"
        mismatch_str = f"Mismatches: {match.mismatches}"
        gap_str = f"Gaps: {match.gaps}"
        lines.append(f"{identity_str} | {mismatch_str} | {gap_str}")
        
        return "\n".join(lines)
    
    def _format_seq_with_matches(self, query: str, target: str) -> str:
        """Color query based on matches."""
        result = ""
        for q, t in zip(query, target):
            if q == t:
                result += self._colorize(q, "match")
            elif q == "-" or t == "-":
                result += self._colorize(q, "gap")
            else:
                result += self._colorize(q, "mismatch")
        return result
    
    def format_primer_pair(
        self,
        forward: Optional[AlignmentMatch],
        reverse: Optional[AlignmentMatch],
        product_size: Optional[int] = None
    ) -> str:
        """
        Format primer pair alignment summary.
        
        Args:
            forward: Forward primer alignment
            reverse: Reverse primer alignment
            product_size: Expected product size
            
        Returns:
            Formatted string
        """
        lines = []
        
        lines.append("=" * 50)
        lines.append(self._colorize("PRIMER PAIR ALIGNMENT", "bold"))
        lines.append("=" * 50)
        lines.append("")
        
        if forward:
            lines.append(self._colorize("▶ FORWARD PRIMER", "bold"))
            lines.append(self.format_alignment(forward))
            lines.append("")
        
        if reverse:
            lines.append(self._colorize("◀ REVERSE PRIMER", "bold"))
            lines.append(self.format_alignment(reverse))
            lines.append("")
        
        if product_size:
            lines.append(f"Expected Product: {product_size}bp")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def format_binding_diagram(
        self,
        target_length: int,
        forward_pos: Optional[Tuple[int, int]] = None,
        reverse_pos: Optional[Tuple[int, int]] = None,
        scale: int = 50
    ) -> str:
        """
        Generate ASCII binding site diagram.
        
        Args:
            target_length: Total target sequence length
            forward_pos: (start, end) of forward primer
            reverse_pos: (start, end) of reverse primer  
            scale: Width of diagram in characters
            
        Returns:
            ASCII diagram string
        """
        lines = []
        
        # Scale factor
        factor = target_length / scale
        
        # Target line
        target_line = ["─"] * scale
        
        # Mark forward primer
        if forward_pos:
            start = int(forward_pos[0] / factor)
            end = int(forward_pos[1] / factor)
            for i in range(max(0, start), min(scale, end + 1)):
                target_line[i] = "▶"
        
        # Mark reverse primer
        if reverse_pos:
            start = int(reverse_pos[0] / factor)
            end = int(reverse_pos[1] / factor)
            for i in range(max(0, start), min(scale, end + 1)):
                target_line[i] = "◀"
        
        # Build diagram
        lines.append("Binding Sites:")
        lines.append(f"5' {''.join(target_line)} 3'")
        lines.append(f"   0{' ' * (scale - 8)}{target_length}bp")
        
        # Legend
        lines.append("")
        lines.append("Legend: ▶ Forward  ◀ Reverse  ─ Target")
        
        return "\n".join(lines)


class OfftargetTable:
    """
    Generate off-target summary tables.
    """
    
    def __init__(self, use_colors: bool = True):
        """Initialize table generator."""
        self.use_colors = use_colors
    
    def _grade_color(self, grade: str) -> str:
        """Get color for grade."""
        colors = {
            "A": "\033[92m",  # Green
            "B": "\033[94m",  # Blue
            "C": "\033[93m",  # Yellow
            "D": "\033[91m",  # Red
            "F": "\033[91m",  # Red
        }
        if not self.use_colors:
            return ""
        return colors.get(grade, "")
    
    def format_summary(
        self,
        forward_hits: int,
        reverse_hits: int,
        forward_grade: str,
        reverse_grade: str,
        combined_grade: str,
        specificity_score: float
    ) -> str:
        """
        Format off-target summary table.
        
        Returns:
            Formatted table string
        """
        lines = []
        reset = "\033[0m" if self.use_colors else ""
        
        lines.append("┌─────────────────────────────────────┐")
        lines.append("│       OFF-TARGET SUMMARY            │")
        lines.append("├──────────────┬───────────┬──────────┤")
        lines.append("│    Primer    │   Hits    │  Grade   │")
        lines.append("├──────────────┼───────────┼──────────┤")
        
        # Forward
        fwd_color = self._grade_color(forward_grade)
        lines.append(f"│  Forward     │    {forward_hits:>3}    │  {fwd_color}{forward_grade}{reset}       │")
        
        # Reverse
        rev_color = self._grade_color(reverse_grade)
        lines.append(f"│  Reverse     │    {reverse_hits:>3}    │  {rev_color}{reverse_grade}{reset}       │")
        
        lines.append("├──────────────┴───────────┼──────────┤")
        
        # Combined
        comb_color = self._grade_color(combined_grade)
        lines.append(f"│  Combined Score: {specificity_score:>5.1f}  │  {comb_color}{combined_grade}{reset}       │")
        
        lines.append("└──────────────────────────┴──────────┘")
        
        return "\n".join(lines)
    
    def format_hits_table(
        self,
        hits: List[dict],
        max_rows: int = 10,
        title: str = "OFF-TARGET HITS"
    ) -> str:
        """
        Format detailed hits table.
        
        Args:
            hits: List of hit dictionaries
            max_rows: Maximum rows to show
            title: Table title
            
        Returns:
            Formatted table
        """
        lines = []
        
        lines.append(f"┌{'─' * 70}┐")
        lines.append(f"│ {title:<68} │")
        lines.append(f"├{'─' * 18}┬{'─' * 15}┬{'─' * 12}┬{'─' * 12}┬{'─' * 10}┤")
        lines.append(f"│ {'Subject':<16} │ {'Position':<13} │ {'Identity':<10} │ {'E-value':<10} │ {'Orient':<8} │")
        lines.append(f"├{'─' * 18}┼{'─' * 15}┼{'─' * 12}┼{'─' * 12}┼{'─' * 10}┤")
        
        for i, hit in enumerate(hits[:max_rows]):
            subject = str(hit.get("subject_id", "N/A"))[:16]
            pos = f"{hit.get('start', 0)}-{hit.get('end', 0)}"[:13]
            identity = f"{hit.get('identity', 0):.1f}%"[:10]
            evalue = f"{hit.get('evalue', 0):.1e}"[:10]
            orient = ("Fwd" if hit.get("orientation") == "forward" else "Rev")[:8]
            
            lines.append(f"│ {subject:<16} │ {pos:<13} │ {identity:<10} │ {evalue:<10} │ {orient:<8} │")
        
        if len(hits) > max_rows:
            lines.append(f"├{'─' * 70}┤")
            lines.append(f"│ ... and {len(hits) - max_rows} more hits{' ' * 47} │")
        
        lines.append(f"└{'─' * 70}┘")
        
        return "\n".join(lines)


def format_primer_alignment(
    primer_seq: str,
    target_seq: str,
    start: int,
    end: int,
    identity: float = 100.0,
    orientation: str = "forward"
) -> str:
    """
    Convenience function to format primer alignment.
    
    Args:
        primer_seq: Primer sequence
        target_seq: Target sequence at binding site
        start: Start position on target
        end: End position on target
        identity: Alignment identity %
        orientation: forward or reverse
        
    Returns:
        Formatted alignment string
    """
    match = AlignmentMatch(
        query_seq=primer_seq,
        target_seq=target_seq,
        query_start=1,
        query_end=len(primer_seq),
        target_start=start,
        target_end=end,
        identity=identity,
        orientation=orientation
    )
    
    view = AlignmentView()
    return view.format_alignment(match)
