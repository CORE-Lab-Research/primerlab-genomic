"""
Batch Species-Check Module.

Provides batch processing, caching, and parallel analysis for species-check.
"""

from .batch_loader import (
    load_primers_from_directory,
    load_multi_fasta_templates,
    BatchInput,
)
from .cache import (
    AlignmentCache,
    get_cache,
)
from .parallel import (
    run_parallel_species_check,
    BatchSpeciesResult,
)

__all__ = [
    # Batch loader
    "load_primers_from_directory",
    "load_multi_fasta_templates",
    "BatchInput",
    # Cache
    "AlignmentCache",
    "get_cache",
    # Parallel
    "run_parallel_species_check",
    "BatchSpeciesResult",
]
