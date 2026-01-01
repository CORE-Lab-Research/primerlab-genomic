"""
PCR Variants Module.

Provides engines for specialized PCR techniques:
- Nested PCR
- Semi-Nested PCR (v0.7.0+)
"""

from primerlab.core.variants.models import (
    NestedPrimerSet,
    NestedPCRResult,
)
from primerlab.core.variants.nested import (
    NestedPCREngine,
    design_nested_primers,
)

__all__ = [
    "NestedPrimerSet",
    "NestedPCRResult",
    "NestedPCREngine",
    "design_nested_primers",
]
