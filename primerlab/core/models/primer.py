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

    # Probe-only: chemistry type ("exo" / "fpg" / "taqman") and the 0-based index
    # of the abasic (THF / dR-biotin) residue WITHIN `sequence`.
    #
    # annotate_probe() computes this position but it used to be dropped before
    # serialisation, so downstream consumers (in-silico PCR, off-target checks)
    # had no way to know where the cleavage site sits — the only trace was the
    # bracket markup inside `labeled_sequence`, which had to be re-parsed. Keep
    # it as a first-class field so the position never has to be reconstructed.
    probe_type: Optional[str] = None
    thf_index: Optional[int] = None
    # Number of dT labels that had to replace a non-T base — each one is a
    # deliberate probe-target mismatch, so downstream mismatch checks must not
    # count them as target variation.
    probe_label_mismatches: int = 0
    probe_compliant: Optional[bool] = None

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
            "probe_type": self.probe_type,
            "thf_index": self.thf_index,
            "probe_label_mismatches": self.probe_label_mismatches,
            "probe_compliant": self.probe_compliant,
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
