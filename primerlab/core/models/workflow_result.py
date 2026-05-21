from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from .primer import Primer
from .amplicon import Amplicon
from .qc import QCResult
from .metadata import RunMetadata

@dataclass
class WorkflowResult:
    workflow: str
    primers: Dict[str, Primer]
    amplicons: List[Amplicon]
    metadata: RunMetadata

    qc: Optional[QCResult] = None
    score: Optional[float] = None # Added for Reranking (v1.2.0)
    visual_map: Optional[str] = None # Quick access (v1.2.0)

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    # v0.1.3: Alternative primer candidates
    alternatives: List[Dict[str, Any]] = field(default_factory=list)

    # Transparency logs (v1.2.5)
    ranking_details: List[Dict[str, Any]] = field(default_factory=list)

    # In-silico validation summary
    insilico_validation: Optional[Dict[str, Any]] = None

    # Internal diagnostics
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    def to_dict(self) -> Dict[str, Any]:
        res = {
            "workflow": self.workflow,
            "primers": {k: v.to_dict() for k, v in self.primers.items()},
            "amplicons": [a.to_dict() for a in self.amplicons],
            "qc": self.qc.to_dict() if self.qc else None,
            "score": self.score,
            "visual_map": self.visual_map,
            "metadata": self.metadata.to_dict(),
            "warnings": self.warnings,
            "errors": self.errors,
            "alternatives": self.alternatives,
            "ranking_details": self.ranking_details
        }
        if self.insilico_validation is not None:
            res["insilico_validation"] = self.insilico_validation
        return res
