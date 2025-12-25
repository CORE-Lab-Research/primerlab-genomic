"""
Main Amplicon Analyzer.

Combines all analysis modules into a unified interface.
"""

import logging
from typing import Optional, List, Dict

from .models import AmpliconAnalysisResult
from .secondary_structure import SecondaryStructureAnalyzer
from .gc_profile import calculate_gc_profile
from .gc_clamp import analyze_gc_clamp
from .tm_prediction import predict_amplicon_tm
from .restriction_sites import find_restriction_sites
from .quality_score import calculate_quality_score

logger = logging.getLogger(__name__)


class AmpliconAnalyzer:
    """
    Unified amplicon analysis engine.
    
    Performs comprehensive analysis including:
    - Secondary structure prediction
    - GC profile visualization
    - GC clamp analysis
    - Melting temperature prediction
    - Restriction site mapping
    - Overall quality scoring
    """
    
    def __init__(self, config: dict = None):
        """
        Initialize analyzer with configuration.
        
        Args:
            config: Configuration dict with amplicon_analysis section
        """
        self.config = config or {}
        self.analysis_config = self.config.get("amplicon_analysis", {})
        
        # Initialize sub-analyzers
        self.structure_analyzer = SecondaryStructureAnalyzer(config)
    
    def analyze(
        self,
        sequence: str,
        include_structure: bool = True,
        include_gc_profile: bool = True,
        include_gc_clamp: bool = True,
        include_tm: bool = True,
        include_restriction_sites: bool = False,  # Off by default
        include_quality_score: bool = True
    ) -> AmpliconAnalysisResult:
        """
        Perform comprehensive amplicon analysis.
        
        Args:
            sequence: Amplicon DNA sequence
            include_structure: Run secondary structure prediction
            include_gc_profile: Run GC profile analysis
            include_gc_clamp: Run GC clamp analysis
            include_tm: Run Tm prediction
            include_restriction_sites: Run restriction site mapping
            include_quality_score: Calculate overall quality score
            
        Returns:
            AmpliconAnalysisResult with all requested analyses
        """
        seq = sequence.upper()
        logger.info(f"Analyzing amplicon: {len(seq)}bp")
        
        result = AmpliconAnalysisResult(
            sequence=seq,
            length=len(seq)
        )
        
        # 1. Secondary structure
        if include_structure:
            ss_config = self.analysis_config.get("secondary_structure", {})
            if ss_config.get("enabled", True):
                logger.debug("Predicting secondary structure...")
                result.secondary_structure = self.structure_analyzer.predict(seq)
        
        # 2. GC profile
        if include_gc_profile:
            gc_config = self.analysis_config.get("gc_profile", {})
            if gc_config.get("enabled", True):
                logger.debug("Calculating GC profile...")
                result.gc_profile = calculate_gc_profile(
                    seq,
                    window_size=gc_config.get("window_size", 50),
                    step_size=gc_config.get("step_size", 10),
                    ideal_min=gc_config.get("ideal_min", 40.0),
                    ideal_max=gc_config.get("ideal_max", 60.0)
                )
        
        # 3. GC clamp
        if include_gc_clamp:
            clamp_config = self.analysis_config.get("gc_clamp", {})
            if clamp_config.get("enabled", True):
                logger.debug("Analyzing GC clamp...")
                result.gc_clamp = analyze_gc_clamp(
                    seq,
                    region_size=clamp_config.get("region_size", 5),
                    min_gc=clamp_config.get("min_gc", 1),
                    max_gc=clamp_config.get("max_gc", 3)
                )
        
        # 4. Tm prediction
        if include_tm:
            tm_config = self.analysis_config.get("tm_prediction", {})
            if tm_config.get("enabled", True):
                logger.debug("Predicting amplicon Tm...")
                result.amplicon_tm = predict_amplicon_tm(
                    seq,
                    na_concentration=tm_config.get("na_concentration", 50.0)
                )
        
        # 5. Restriction sites
        if include_restriction_sites:
            rs_config = self.analysis_config.get("restriction_sites", {})
            if rs_config.get("enabled", False):  # Off by default
                logger.debug("Mapping restriction sites...")
                enzymes = rs_config.get("enzymes")
                result.restriction_sites = find_restriction_sites(seq, enzymes)
        
        # 6. Quality score
        if include_quality_score:
            qs_config = self.analysis_config.get("quality_score", {})
            if qs_config.get("enabled", True):
                logger.debug("Calculating quality score...")
                
                length_config = qs_config.get("optimal_length", {})
                result.quality = calculate_quality_score(
                    seq,
                    structure=result.secondary_structure,
                    gc_profile=result.gc_profile,
                    gc_clamp=result.gc_clamp,
                    amplicon_tm=result.amplicon_tm,
                    optimal_length_min=length_config.get("min", 100),
                    optimal_length_max=length_config.get("max", 500),
                    weights=qs_config.get("weights")
                )
        
        logger.info(f"Analysis complete. Quality: {result.quality.score if result.quality else 'N/A'}")
        return result


def analyze_amplicon(sequence: str, config: dict = None) -> AmpliconAnalysisResult:
    """
    Convenience function for quick amplicon analysis.
    
    Args:
        sequence: Amplicon DNA sequence
        config: Optional configuration dict
        
    Returns:
        AmpliconAnalysisResult with all analyses
    """
    analyzer = AmpliconAnalyzer(config)
    return analyzer.analyze(sequence)
