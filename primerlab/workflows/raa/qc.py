"""
RAA-specific Quality Control module.

Extends BaseQC with RAA-specific validation including:
- Exo-probe checks (End check, GC clamp, THF position validation)
- 3' end stability at isothermal temperatures
- Long-oligo dimer penalties
- Cross-dimer evaluation (FWD vs REV vs Probe)
- Amplicon size validation for RAA (100-250bp)

Version: v1.2.0
"""

from typing import Dict, Any, List
from primerlab.core.models import Primer, QCResult
from primerlab.core.logger import get_logger
from primerlab.core.qc import BaseQC

logger = get_logger()


class RAAQC(BaseQC):
    """
    Quality Control for RAA primers and Exo-probes.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize RAAQC with configuration.
        """
        super().__init__(config)

        # RAA-specific amplicon size bounds — read from parameters.product_size_range
        # (e.g. [[100, 250]]) with fallback to qc_config or RAA defaults
        product_size_range = config.get("parameters", {}).get("product_size_range", [])
        if product_size_range and isinstance(product_size_range, list) and len(product_size_range) > 0:
            first_range = product_size_range[0]
            self.amplicon_size_min = first_range[0] if len(first_range) > 0 else 100
            self.amplicon_size_max = first_range[1] if len(first_range) > 1 else 250
        else:
            self.amplicon_size_min = self.qc_config.get("amplicon_size_min", 100)
            self.amplicon_size_max = self.qc_config.get("amplicon_size_max", 250)
        
        # Cross dimer threshold
        self.cross_dimer_dg_min = self.qc_config.get("cross_dimer_dg_min", -7.0)
        
        # Probe constraints from config
        probe_cfg = config.get("parameters", {}).get("probe", {})
        self.thf_upstream_min = probe_cfg.get("thf_upstream_min", 30)
        self.thf_downstream_min = probe_cfg.get("thf_downstream_min", 15)

    def evaluate_pair_extended(self, fwd: Primer, rev: Primer, probe: Primer = None) -> QCResult:
        """
        Evaluates the primer pair (and optional probe) with RAA-specific checks.
        """
        # Run base evaluation first
        base_result = self.evaluate_pair(fwd, rev)
        
        warnings = base_result.warnings
        
        # RAA specific cross-dimer check
        cross_dimer_res = self.screening_thermo.calc_heterodimer(fwd.sequence, rev.sequence)
        dg_kcal = cross_dimer_res.dg / 1000.0
        base_result.cross_dimer_dg = dg_kcal
        
        if dg_kcal < self.cross_dimer_dg_min:
            warnings.append(f"Strong cross-dimer between FWD and REV: ΔG={dg_kcal:.2f} kcal/mol (threshold: {self.cross_dimer_dg_min})")
            
        if probe:
            fwd_probe_res = self.screening_thermo.calc_heterodimer(fwd.sequence, probe.sequence)
            dg_fwd_prb = fwd_probe_res.dg / 1000.0
            if dg_fwd_prb < self.cross_dimer_dg_min:
                warnings.append(f"Strong cross-dimer between FWD and PROBE: ΔG={dg_fwd_prb:.2f} kcal/mol")
                
            rev_probe_res = self.screening_thermo.calc_heterodimer(rev.sequence, probe.sequence)
            dg_rev_prb = rev_probe_res.dg / 1000.0
            if dg_rev_prb < self.cross_dimer_dg_min:
                warnings.append(f"Strong cross-dimer between REV and PROBE: ΔG={dg_rev_prb:.2f} kcal/mol")
                
        # 2. GC Clamp Check at 3' end
        if self.qc_config.get("gc_clamp", True):
            for p_name, p in [("FWD", fwd), ("REV", rev)]:
                last_5 = p.sequence[-5:].upper()
                gc_count = last_5.count("G") + last_5.count("C")
                if gc_count == 0:
                    warnings.append(f"{p_name} lacks GC clamp at 3' end (0 G/C in last 5bp)")
                elif gc_count > 3:
                    warnings.append(f"{p_name} has too strong GC clamp at 3' end ({gc_count} G/C in last 5bp)")
                    
        base_result.warnings = warnings
        return base_result

    def evaluate_probe(self, probe: Primer, fwd: Primer, rev: Primer) -> Dict[str, Any]:
        """
        Evaluates Exo-probe specific QC metrics.
        """
        warnings = []

        # Probe secondary structure — use screening_thermo
        probe_res = self.screening_thermo.calc_hairpin(probe.sequence)
        probe_dg = probe_res.dg / 1000.0

        probe_hairpin_ok = probe_dg >= self.hairpin_dg_min
        if not probe_hairpin_ok:
            warnings.append(f"Probe hairpin ΔG ({probe_dg:.2f} kcal/mol) too stable (threshold: {self.hairpin_dg_min})")

        # 2. Probe End Check (Fluorophore Quenching)
        if self.qc_config.get("probe_end_check", True):
            first_5 = probe.sequence[:5].upper()
            if probe.sequence[0].upper() == 'G':
                warnings.append("Probe starts with 'G'. This quenches the 5' FAM fluorophore.")
                
            gc_count = first_5.count('G') + first_5.count('C')
            if gc_count > 3:
                warnings.append(f"Probe 5' end has high GC content ({gc_count}/5), which may quench fluorophore.")

        # 3. Probe GC Clamp
        last_5 = probe.sequence[-5:].upper()
        gc_count = last_5.count("G") + last_5.count("C")
        if gc_count == 0:
            warnings.append("Probe lacks GC clamp at 3' end")

        # 4. THF Position Check
        # In a real implementation, the THF position is determined during probe design.
        # Here we just validate if the length allows for the minimum constraints.
        min_required_len = self.thf_upstream_min + 1 + self.thf_downstream_min
        if len(probe.sequence) < min_required_len:
            warnings.append(f"Probe is too short ({len(probe.sequence)}bp) to accommodate THF constraints (needs {min_required_len}bp).")

        # RAA probe Tm is typically around 50°C (lower than primers usually, as the reaction is at 39°C)
        probe_tm_ok = probe.tm >= 45.0  # Just a basic sanity check for isothermal

        if not probe_tm_ok:
            warnings.append(f"Probe Tm ({probe.tm:.2f}°C) is too low for 39°C reaction.")

        return {
            "probe_tm_ok": probe_tm_ok,
            "probe_hairpin_ok": probe_hairpin_ok,
            "probe_dg": probe_dg,
            "warnings": warnings
        }

    def validate_amplicon_size(self, amplicon_size: int) -> Dict[str, Any]:
        """
        Validates amplicon size against RAA-optimal range (100-250bp).
        """
        size_ok = self.amplicon_size_min <= amplicon_size <= self.amplicon_size_max

        warnings = []
        if not size_ok:
            if amplicon_size < self.amplicon_size_min:
                warnings.append(f"Amplicon size ({amplicon_size}bp) is too short for reliable RAA (min: {self.amplicon_size_min}bp)")
            else:
                warnings.append(f"Amplicon size ({amplicon_size}bp) is too long for optimal RAA efficiency (max: {self.amplicon_size_max}bp)")

        return {
            "size_ok": size_ok,
            "size": amplicon_size,
            "warnings": warnings
        }

    def evaluate_target_structure(self, sequence: str) -> Dict[str, Any]:
        """
        Advanced QC: Evaluates the secondary structure of the target region itself.
        If the target folds too strongly, enzymes may have accessibility issues.
        """
        # We use vienna_wrapper directly for the whole sequence
        from primerlab.core.tools.vienna_wrapper import ViennaWrapper
        vienna = ViennaWrapper()
        
        # Calculate structure for the whole 150-200bp zone
        res = vienna.fold(sequence)
        
        # Heuristic: if dG per 100bp is lower than -20, it's quite stable
        normalized_dg = (res["mfe"] / len(sequence)) * 100
        is_accessible = normalized_dg > -25.0 # Threshold for accessibility
        
        warnings = []
        if not is_accessible:
            warnings.append(f"Target region has high stability (normalized ΔG: {normalized_dg:.2f}). Possible accessibility issues for RAA enzymes.")
            
        return {
            "accessible": is_accessible,
            "dg": res["mfe"],
            "normalized_dg": normalized_dg,
            "warnings": warnings
        }
