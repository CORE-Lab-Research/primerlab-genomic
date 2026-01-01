"""
Primer Dimer Matrix Analysis.

Performs NxN pairwise dimer analysis for a set of primers and generates
heatmap visualizations.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import primer3
from primerlab.core.logger import get_logger

logger = get_logger()


@dataclass
class DimerResult:
    """Result of dimer analysis between two primers."""
    primer1_name: str
    primer2_name: str
    primer1_seq: str
    primer2_seq: str
    dg: float  # ΔG in kcal/mol
    tm: float  # Dimer Tm in °C
    structure: str  # ASCII representation
    is_problematic: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "primer1": self.primer1_name,
            "primer2": self.primer2_name,
            "dg": self.dg,
            "tm": self.tm,
            "is_problematic": self.is_problematic,
        }


@dataclass
class DimerMatrixResult:
    """Complete NxN dimer matrix result."""
    primers: List[Dict[str, str]]  # [{name, sequence}, ...]
    matrix: List[List[float]]  # NxN ΔG values
    dimer_details: List[DimerResult] = field(default_factory=list)
    problematic_pairs: List[Tuple[str, str]] = field(default_factory=list)
    worst_dg: float = 0.0
    best_dg: float = 0.0
    grade: str = "A"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "primer_count": len(self.primers),
            "primers": [p["name"] for p in self.primers],
            "matrix": self.matrix,
            "problematic_pairs": self.problematic_pairs,
            "worst_dg": self.worst_dg,
            "best_dg": self.best_dg,
            "grade": self.grade,
        }


class DimerMatrixAnalyzer:
    """
    Analyzes dimer formation potential between all pairs of primers.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize analyzer.
        
        Args:
            config: Optional configuration with thresholds
        """
        self.config = config or {}
        self.dg_threshold = self.config.get("dg_threshold", -6.0)  # kcal/mol
        self.mv_conc = self.config.get("mv_conc", 50.0)  # mM
        self.dv_conc = self.config.get("dv_conc", 1.5)  # mM
        self.dntp_conc = self.config.get("dntp_conc", 0.6)  # mM
        self.dna_conc = self.config.get("dna_conc", 250.0)  # nM
    
    def analyze(self, primers: List[Dict[str, str]]) -> DimerMatrixResult:
        """
        Analyze all pairwise dimer interactions.
        
        Args:
            primers: List of {name: str, sequence: str} dicts
            
        Returns:
            DimerMatrixResult with NxN matrix
        """
        n = len(primers)
        logger.info(f"Analyzing {n}x{n} dimer matrix for {n} primers")
        
        matrix = [[0.0] * n for _ in range(n)]
        dimer_details = []
        problematic_pairs = []
        
        worst_dg = 0.0
        best_dg = 0.0
        
        for i in range(n):
            for j in range(i, n):  # Upper triangular + diagonal
                p1 = primers[i]
                p2 = primers[j]
                
                dimer = self._analyze_pair(p1, p2)
                dimer_details.append(dimer)
                
                # Fill matrix symmetrically
                matrix[i][j] = dimer.dg
                matrix[j][i] = dimer.dg
                
                # Track extremes
                if dimer.dg < worst_dg:
                    worst_dg = dimer.dg
                if dimer.dg > best_dg:
                    best_dg = dimer.dg
                
                # Track problematic pairs
                if dimer.is_problematic and i != j:
                    problematic_pairs.append((p1["name"], p2["name"]))
        
        # Calculate grade
        grade = self._calculate_grade(worst_dg, len(problematic_pairs), n)
        
        result = DimerMatrixResult(
            primers=primers,
            matrix=matrix,
            dimer_details=dimer_details,
            problematic_pairs=problematic_pairs,
            worst_dg=worst_dg,
            best_dg=best_dg,
            grade=grade,
        )
        
        logger.info(f"Dimer matrix analysis complete. Grade: {grade}")
        return result
    
    def _analyze_pair(
        self, 
        p1: Dict[str, str], 
        p2: Dict[str, str]
    ) -> DimerResult:
        """Analyze dimer formation between two primers."""
        try:
            result = primer3.calc_heterodimer(
                p1["sequence"],
                p2["sequence"],
                mv_conc=self.mv_conc,
                dv_conc=self.dv_conc,
                dntp_conc=self.dntp_conc,
                dna_conc=self.dna_conc,
            )
            
            dg = result.dg if hasattr(result, 'dg') else 0.0
            tm = result.tm if hasattr(result, 'tm') else 0.0
            structure = result.ascii_structure if hasattr(result, 'ascii_structure') else ""
            
        except Exception as e:
            logger.warning(f"Dimer calc failed for {p1['name']}-{p2['name']}: {e}")
            dg = 0.0
            tm = 0.0
            structure = ""
        
        is_problematic = dg < self.dg_threshold
        
        return DimerResult(
            primer1_name=p1["name"],
            primer2_name=p2["name"],
            primer1_seq=p1["sequence"],
            primer2_seq=p2["sequence"],
            dg=dg,
            tm=tm,
            structure=structure,
            is_problematic=is_problematic,
        )
    
    def _calculate_grade(
        self, 
        worst_dg: float, 
        problematic_count: int,
        total_primers: int
    ) -> str:
        """Calculate overall grade for the primer set."""
        if worst_dg >= -3.0 and problematic_count == 0:
            return "A"
        elif worst_dg >= -5.0 and problematic_count <= 1:
            return "B"
        elif worst_dg >= -6.0 and problematic_count <= 2:
            return "C"
        elif worst_dg >= -8.0:
            return "D"
        else:
            return "F"
    
    def generate_heatmap_svg(
        self, 
        result: DimerMatrixResult,
        width: int = 500,
        height: int = 500,
    ) -> str:
        """
        Generate SVG heatmap visualization.
        
        Args:
            result: DimerMatrixResult from analyze()
            width: SVG width
            height: SVG height
            
        Returns:
            SVG string
        """
        n = len(result.primers)
        if n == 0:
            return "<svg></svg>"
        
        # Calculate cell size
        margin = 80
        cell_size = min((width - margin) // n, (height - margin) // n)
        actual_width = margin + cell_size * n
        actual_height = margin + cell_size * n
        
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{actual_width}" height="{actual_height}">',
            '<style>',
            '  .cell-text { font-family: monospace; font-size: 10px; }',
            '  .label { font-family: sans-serif; font-size: 11px; }',
            '  .title { font-family: sans-serif; font-size: 14px; font-weight: bold; }',
            '</style>',
            f'<text x="{actual_width // 2}" y="20" class="title" text-anchor="middle">Primer Dimer Matrix (ΔG kcal/mol)</text>',
        ]
        
        # Draw cells
        for i in range(n):
            for j in range(n):
                x = margin + j * cell_size
                y = margin + i * cell_size
                dg = result.matrix[i][j]
                
                # Color based on ΔG
                color = self._dg_to_color(dg)
                
                svg_parts.append(
                    f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
                    f'fill="{color}" stroke="#333" stroke-width="0.5"/>'
                )
                
                # Value text (only if cell is big enough)
                if cell_size >= 30:
                    text_x = x + cell_size // 2
                    text_y = y + cell_size // 2 + 4
                    svg_parts.append(
                        f'<text x="{text_x}" y="{text_y}" class="cell-text" '
                        f'text-anchor="middle">{dg:.1f}</text>'
                    )
        
        # Draw row labels (left)
        for i, primer in enumerate(result.primers):
            y = margin + i * cell_size + cell_size // 2 + 4
            name = primer["name"][:8]  # Truncate long names
            svg_parts.append(
                f'<text x="{margin - 5}" y="{y}" class="label" text-anchor="end">{name}</text>'
            )
        
        # Draw column labels (top, rotated)
        for j, primer in enumerate(result.primers):
            x = margin + j * cell_size + cell_size // 2
            name = primer["name"][:8]
            svg_parts.append(
                f'<text x="{x}" y="{margin - 5}" class="label" text-anchor="end" '
                f'transform="rotate(-45 {x} {margin - 5})">{name}</text>'
            )
        
        # Legend
        legend_y = actual_height - 30
        svg_parts.extend([
            f'<text x="{margin}" y="{legend_y}" class="label">Good (≥0)</text>',
            f'<rect x="{margin + 70}" y="{legend_y - 12}" width="15" height="15" fill="#4CAF50"/>',
            f'<text x="{margin + 100}" y="{legend_y}" class="label">Moderate</text>',
            f'<rect x="{margin + 170}" y="{legend_y - 12}" width="15" height="15" fill="#FFC107"/>',
            f'<text x="{margin + 200}" y="{legend_y}" class="label">Problematic (&lt;-6)</text>',
            f'<rect x="{margin + 300}" y="{legend_y - 12}" width="15" height="15" fill="#F44336"/>',
        ])
        
        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)
    
    def _dg_to_color(self, dg: float) -> str:
        """Convert ΔG value to color."""
        if dg >= 0:
            return "#4CAF50"  # Green - excellent
        elif dg >= -3:
            return "#8BC34A"  # Light green - good
        elif dg >= -5:
            return "#FFC107"  # Yellow - moderate
        elif dg >= -6:
            return "#FF9800"  # Orange - warning
        elif dg >= -8:
            return "#F44336"  # Red - problematic
        else:
            return "#9C27B0"  # Purple - severe


def analyze_dimer_matrix(
    primers: List[Dict[str, str]],
    dg_threshold: float = -6.0,
) -> DimerMatrixResult:
    """
    Analyze dimer matrix for a set of primers.
    
    Args:
        primers: List of {name: str, sequence: str} dicts
        dg_threshold: ΔG threshold for problematic dimers
        
    Returns:
        DimerMatrixResult with NxN matrix and analysis
    """
    analyzer = DimerMatrixAnalyzer({"dg_threshold": dg_threshold})
    return analyzer.analyze(primers)
