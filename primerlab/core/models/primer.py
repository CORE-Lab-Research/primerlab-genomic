from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import itertools

@dataclass
class Primer:
    id: str
    sequence: str
    tm: float
    gc: float
    length: int

    hairpin_dg: Optional[float] = None
    homodimer_dg: Optional[float] = None
    heterodimer_dg: Optional[float] = None
    end_stability_dg: Optional[float] = None

    start: Optional[int] = None
    end: Optional[int] = None

    warnings: List[str] = field(default_factory=list)

    # Degeneracy support (Phase 4)
    degeneracy_multiplier: int = 1
    possible_sequences: List[str] = field(default_factory=list)

    # Optional field for special labeling (e.g., RAA exo-probes)
    labeled_sequence: Optional[str] = None

    # Internal use only (Primer3 raw output)
    raw: Optional[Dict[str, Any]] = field(default=None, repr=False)

    def __post_init__(self):
        # Calculate degeneracy and possible sequences
        IUPAC_DICT = {
            'R': ['A', 'G'], 'Y': ['C', 'T'], 'S': ['G', 'C'], 'W': ['A', 'T'],
            'K': ['G', 'T'], 'M': ['A', 'C'], 'B': ['C', 'G', 'T'], 
            'D': ['A', 'G', 'T'], 'H': ['A', 'C', 'T'], 'V': ['A', 'C', 'G'],
            'N': ['A', 'C', 'G', 'T']
        }
        
        has_degenerate = any(c in IUPAC_DICT for c in self.sequence.upper())
        if has_degenerate:
            bases_lists = [IUPAC_DICT.get(c, [c]) for c in self.sequence.upper()]
            self.degeneracy_multiplier = 1
            for b in bases_lists:
                self.degeneracy_multiplier *= len(b)
                
            if self.degeneracy_multiplier > 256:
                if "High degeneracy (>256)" not in self.warnings:
                    self.warnings.append("High degeneracy (>256)")
            elif self.degeneracy_multiplier > 1:
                # Generate possible sequences if manageable
                seqs = [''.join(p) for p in itertools.product(*bases_lists)]
                self.possible_sequences = seqs

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary, excluding internal fields."""
        return {
            "id": self.id,
            "sequence": self.sequence,
            "labeled_sequence": self.labeled_sequence,
            "tm": f"{round(self.tm, 2)} °C",
            "gc": f"{round(self.gc, 2)} %",
            "length": self.length,
            "hairpin_dg": f"{round(self.hairpin_dg, 2)} kcal/mol" if self.hairpin_dg is not None else None,
            "homodimer_dg": f"{round(self.homodimer_dg, 2)} kcal/mol" if self.homodimer_dg is not None else None,
            "heterodimer_dg": f"{round(self.heterodimer_dg, 2)} kcal/mol" if self.heterodimer_dg is not None else None,
            "end_stability_dg": f"{round(self.end_stability_dg, 2)} kcal/mol" if self.end_stability_dg is not None else None,
            "start": self.start,
            "end": self.end,
            "degeneracy_multiplier": self.degeneracy_multiplier,
            "possible_sequences": self.possible_sequences,
            "warnings": self.warnings
        }
