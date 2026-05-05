from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class QCResult:
    hairpin_ok: bool
    homodimer_ok: bool
    heterodimer_ok: bool
    end_stability_ok: bool
    tm_balance_ok: bool

    hairpin_dg: float
    homodimer_dg: float
    heterodimer_dg: Optional[float]
    end_stability_dg: Optional[float]

    tm_diff: float
    cross_dimer_dg: Optional[float] = None # Added for RAA (v1.2.0)

    # Quality score fields (v0.1.4)
    quality_score: Optional[int] = None  # 0-100
    quality_category: Optional[str] = None  # Excellent, Good, Fair, Poor
    quality_category_emoji: Optional[str] = None  # ✅, ⚠️, ❌
    quality_penalties: Optional[Dict[str, int]] = None

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    # v1.2.5: For extra metadata (e.g. ViennaRNA)
    additional_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hairpin_ok": self.hairpin_ok,
            "homodimer_ok": self.homodimer_ok,
            "heterodimer_ok": self.heterodimer_ok,
            "end_stability_ok": self.end_stability_ok,
            "tm_balance_ok": self.tm_balance_ok,
            "hairpin_dg": round(self.hairpin_dg, 2) if self.hairpin_dg is not None else None,
            "homodimer_dg": round(self.homodimer_dg, 2) if self.homodimer_dg is not None else None,
            "heterodimer_dg": round(self.heterodimer_dg, 2) if self.heterodimer_dg is not None else None,
            "end_stability_dg": round(self.end_stability_dg, 2) if self.end_stability_dg is not None else None,
            "cross_dimer_dg": round(self.cross_dimer_dg, 2) if self.cross_dimer_dg is not None else None,
            "tm_diff": round(self.tm_diff, 2),
            "quality_score": self.quality_score,
            "quality_category": self.quality_category,
            "quality_category_emoji": self.quality_category_emoji,
            "quality_penalties": self.quality_penalties,
            "warnings": self.warnings,
            "errors": self.errors,
            "additional_metrics": self.additional_metrics
        }
