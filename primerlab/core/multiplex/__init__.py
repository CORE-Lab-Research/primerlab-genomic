"""
Core Multiplex module exports.

This module provides multiplex analysis functionality including
data models, dimer calculation, scoring, and validation.
"""

from primerlab.core.multiplex.models import (
    MultiplexPair,
    DimerResult,
    CompatibilityMatrix,
    MultiplexResult,
    score_to_grade,
    grade_to_emoji,
)
from primerlab.core.multiplex.dimer import DimerEngine
from primerlab.core.multiplex.scoring import MultiplexScorer, MULTIPLEX_CONFIG
from primerlab.core.multiplex.validator import MultiplexValidator

__all__ = [
    # Models
    "MultiplexPair",
    "DimerResult",
    "CompatibilityMatrix",
    "MultiplexResult",
    # Engine
    "DimerEngine",
    # Scoring
    "MultiplexScorer",
    "MULTIPLEX_CONFIG",
    # Validation
    "MultiplexValidator",
    # Utilities
    "score_to_grade",
    "grade_to_emoji",
]
