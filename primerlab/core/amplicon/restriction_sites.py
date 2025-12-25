"""
Restriction Site Mapping for Amplicons.

Identifies common restriction enzyme recognition sites.
"""

from typing import List, Optional, Dict
from .models import RestrictionSite

# Common 6-cutter restriction enzymes
# Format: name -> (recognition_seq, cut_position_from_start)
DEFAULT_ENZYMES: Dict[str, tuple] = {
    "EcoRI": ("GAATTC", 1),    # G^AATTC
    "BamHI": ("GGATCC", 1),    # G^GATCC
    "HindIII": ("AAGCTT", 1),  # A^AGCTT
    "XhoI": ("CTCGAG", 1),     # C^TCGAG
    "NotI": ("GCGGCCGC", 2),   # GC^GGCCGC
    "SalI": ("GTCGAC", 1),     # G^TCGAC
    "PstI": ("CTGCAG", 5),     # CTGCA^G
    "SmaI": ("CCCGGG", 3),     # CCC^GGG
    "KpnI": ("GGTACC", 5),     # GGTAC^C
    "SacI": ("GAGCTC", 5),     # GAGCT^C
}


def find_restriction_sites(
    sequence: str,
    enzymes: Optional[List[str]] = None
) -> List[RestrictionSite]:
    """
    Find restriction enzyme recognition sites in sequence.
    
    Args:
        sequence: DNA sequence
        enzymes: List of enzyme names to search for (default: 6 common enzymes)
        
    Returns:
        List of RestrictionSite objects
    """
    seq = sequence.upper()
    
    # Use default enzymes if not specified
    if enzymes is None:
        enzymes = ["EcoRI", "BamHI", "HindIII", "XhoI", "NotI", "SalI"]
    
    sites = []
    
    for enzyme in enzymes:
        if enzyme not in DEFAULT_ENZYMES:
            continue
            
        recognition, cut_pos = DEFAULT_ENZYMES[enzyme]
        
        # Search for recognition site
        pos = 0
        while True:
            pos = seq.find(recognition, pos)
            if pos == -1:
                break
            
            sites.append(RestrictionSite(
                enzyme=enzyme,
                position=pos,
                recognition_seq=recognition,
                cut_position=cut_pos
            ))
            pos += 1
    
    # Sort by position
    sites.sort(key=lambda s: s.position)
    
    return sites


def get_available_enzymes() -> List[str]:
    """Return list of available enzyme names."""
    return list(DEFAULT_ENZYMES.keys())


def add_custom_enzyme(name: str, recognition_seq: str, cut_position: int):
    """Add a custom enzyme to the database."""
    DEFAULT_ENZYMES[name] = (recognition_seq.upper(), cut_position)
