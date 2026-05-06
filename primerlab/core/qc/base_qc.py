"""
Base Quality Control module for PrimerLab.

This module contains the shared QC functionality used by all workflow-specific
QC modules (PCR, qPCR, etc.). It follows the architecture rule that core modules
must be workflow-agnostic and reusable.

Version: v0.3.6
"""

from typing import Dict, Any, List, Optional
from primerlab.core.models import Primer, QCResult
from primerlab.core.logger import get_logger
from primerlab.core.tools.vienna_wrapper import ViennaWrapper
from primerlab.core.tools.thermocalc_wrapper import ThermocalcWrapper

logger = get_logger()


class BaseQC:
    """
    Base Quality Control class for primer pair evaluation.
    
    Provides shared functionality for:
    - Primer3 ThermoAnalysis for individual primer/probe QC
      (hairpin, homodimer, heterodimer, end-stability)
    - ViennaRNA remains available for amplicon secondary structure (separate module)
    - Tm balance checking
    - Configurable thresholds per QC mode (strict/standard/relaxed)
    
    Workflow-specific QC modules should extend this class and add
    their specific validation logic.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize BaseQC with configuration.
        
        Args:
            config: Full workflow configuration dict containing 'qc' section
        """
        self.config = config
        self.qc_config = config.get("qc", {})

        # Common QC thresholds
        self.tm_diff_max = self.qc_config.get("tm_diff_max", 5.0)
        self.hairpin_dg_min = self.qc_config.get("hairpin_dg_min", -3.0)
        self.dimer_dg_min = self.qc_config.get("dimer_dg_min", -6.0)
        # end_stability: primer 3' end should be moderately stable
        # Too stable (< dg_min) = non-specific priming risk
        # Too weak (> dg_max) = primer won't bind at all
        self.end_stability_dg_min = self.qc_config.get("end_stability_dg_min", -6.0)
        self.end_stability_dg_max = self.qc_config.get("end_stability_dg_max", -1.0)

        # Initialize wrappers
        self.vienna = ViennaWrapper()
        
        # Initialize ThermocalcWrapper using parameters.thermodynamics config
        # NOTE on two-condition design:
        # - self.thermo = actual reaction conditions → used for Tm calculations
        # - self.screening_thermo = standard screening conditions → used for dimer/hairpin QC
        #
        # This is intentional: dimer/hairpin screening should always be performed
        # under standard conditions (Mg 1.5mM) to allow cross-assay comparison.
        # Extremely high Mg²⁺ (e.g., 14mM in RAA) will cause false extreme ΔG values
        # (e.g., -300 kcal/mol) that don't reflect structural risk in a meaningful way.
        thermo_config = config.get("parameters", {}).get("thermodynamics", {})
        self.thermo = ThermocalcWrapper(
            mv_conc=thermo_config.get("salt_monovalent", 50.0),
            dv_conc=thermo_config.get("salt_divalent", 1.5),
            dntp_conc=thermo_config.get("dntp_conc", 0.6),
            dna_conc=thermo_config.get("dna_conc", 50.0),
            tm_method=thermo_config.get("tm_method", "santalucia"),
            salt_corrections=thermo_config.get("salt_corrections", "santalucia")
        )
        
        # Screening thermo: standard conditions for dimer/hairpin QC
        # Fixed at typical PCR conditions regardless of workflow-specific buffer
        self.screening_thermo = ThermocalcWrapper(
            mv_conc=50.0,
            dv_conc=1.5,
            dntp_conc=0.6,
            dna_conc=250.0,
            tm_method="santalucia",
            salt_corrections="santalucia"
        )

    def check_tm_balance(self, fwd: Primer, rev: Primer) -> Dict[str, Any]:
        """
        Check melting temperature balance between primers.
        
        Args:
            fwd: Forward primer
            rev: Reverse primer
            
        Returns:
            Dict with tm_balance_ok, tm_diff, and warnings
        """
        tm_diff = abs(fwd.tm - rev.tm)
        tm_balance_ok = tm_diff <= self.tm_diff_max

        warnings = []
        if not tm_balance_ok:
            msg = f"Tm difference ({tm_diff:.2f}°C) exceeds limit ({self.tm_diff_max}°C)"
            warnings.append(msg)

        return {
            "tm_balance_ok": tm_balance_ok,
            "tm_diff": tm_diff,
            "warnings": warnings
        }

    def check_hairpin(self, fwd: Primer, rev: Primer) -> Dict[str, Any]:
        """
        Check hairpin formation using Primer3 ThermoAnalysis.
        
        Args:
            fwd: Forward primer
            rev: Reverse primer
            
        Returns:
            Dict with hairpin_ok, fwd_dg, rev_dg, and warnings
        """
        warnings = []

        # Use screening_thermo (standard conditions) for structural QC.
        # Actual reaction conditions (self.thermo) are only used for Tm.
        fwd_res = self.screening_thermo.calc_hairpin(fwd.sequence)
        rev_res = self.screening_thermo.calc_hairpin(rev.sequence)

        fwd_dg = fwd_res.dg / 1000.0
        rev_dg = rev_res.dg / 1000.0
        
        fwd.hairpin_dg = fwd_dg
        rev.hairpin_dg = rev_dg

        fwd_hairpin_ok = fwd_dg >= self.hairpin_dg_min
        rev_hairpin_ok = rev_dg >= self.hairpin_dg_min

        hairpin_ok = fwd_hairpin_ok and rev_hairpin_ok

        if not fwd_hairpin_ok:
            warnings.append(f"Forward primer hairpin ΔG ({fwd_dg:.2f} kcal/mol) too stable")
        if not rev_hairpin_ok:
            warnings.append(f"Reverse primer hairpin ΔG ({rev_dg:.2f} kcal/mol) too stable")

        return {
            "hairpin_ok": hairpin_ok,
            "fwd_dg": fwd_dg,
            "rev_dg": rev_dg,
            "warnings": warnings
        }

    def check_homodimer(self, fwd: Primer, rev: Primer) -> Dict[str, Any]:
        """
        Check homodimer formation using Primer3 ThermoAnalysis.
        
        Args:
            fwd: Forward primer
            rev: Reverse primer
            
        Returns:
            Dict with homodimer_ok, fwd_homo_dg, rev_homo_dg, and warnings
        """
        warnings = []

        # Use screening_thermo (standard conditions) for structural QC
        fwd_res = self.screening_thermo.calc_homodimer(fwd.sequence)
        rev_res = self.screening_thermo.calc_homodimer(rev.sequence)

        fwd_dg = fwd_res.dg / 1000.0
        rev_dg = rev_res.dg / 1000.0

        # Update Primer objects
        fwd.homodimer_dg = fwd_dg
        rev.homodimer_dg = rev_dg

        fwd_homo_ok = fwd_dg >= self.dimer_dg_min
        rev_homo_ok = rev_dg >= self.dimer_dg_min

        homodimer_ok = fwd_homo_ok and rev_homo_ok

        if not fwd_homo_ok:
            warnings.append(f"Forward primer homodimer ΔG ({fwd_dg:.2f} kcal/mol) too stable")
        if not rev_homo_ok:
            warnings.append(f"Reverse primer homodimer ΔG ({rev_dg:.2f} kcal/mol) too stable")

        return {
            "homodimer_ok": homodimer_ok,
            "fwd_homo_dg": fwd_dg,
            "rev_homo_dg": rev_dg,
            "warnings": warnings
        }

    def check_heterodimer(self, fwd: Primer, rev: Primer) -> Dict[str, Any]:
        """
        Check heterodimer formation between primers using Primer3 ThermoAnalysis.
        
        Args:
            fwd: Forward primer
            rev: Reverse primer
            
        Returns:
            Dict with heterodimer_ok, hetero_dg, and warnings
        """
        warnings = []

        # Use screening_thermo (standard conditions) for structural QC
        hetero_res = self.screening_thermo.calc_heterodimer(fwd.sequence, rev.sequence)
        hetero_dg = hetero_res.dg / 1000.0

        # Update Primer objects
        fwd.heterodimer_dg = hetero_dg
        rev.heterodimer_dg = hetero_dg

        heterodimer_ok = hetero_dg >= self.dimer_dg_min

        if not heterodimer_ok:
            warnings.append(f"Heterodimer (Fwd+Rev) ΔG ({hetero_dg:.2f} kcal/mol) too stable")

        return {
            "heterodimer_ok": heterodimer_ok,
            "hetero_dg": hetero_dg,
            "warnings": warnings
        }
        
    def check_end_stability(self, fwd: Primer, rev: Primer) -> Dict[str, Any]:
        """
        Check 3' end stability of primers.
        
        The 3' end ΔG should be in an optimal window:
        - Too stable (ΔG < dg_min): risk of non-specific/false priming
        - Too weak   (ΔG > dg_max): primer won't bind efficiently
        
        Args:
            fwd: Forward primer
            rev: Reverse primer
            
        Returns:
            Dict with end_stability_ok, fwd_end_dg, rev_end_dg, and warnings
        """
        warnings = []
        
        fwd_res = self.thermo.calc_end_stability(fwd.sequence)
        rev_res = self.thermo.calc_end_stability(rev.sequence)
        
        fwd_end_dg = fwd_res.dg / 1000.0
        rev_end_dg = rev_res.dg / 1000.0
        
        fwd.end_stability_dg = fwd_end_dg
        rev.end_stability_dg = rev_end_dg
        
        # Check both bounds: too stable (non-specific priming) OR too weak (no binding)
        fwd_end_ok = self.end_stability_dg_min <= fwd_end_dg <= self.end_stability_dg_max
        rev_end_ok = self.end_stability_dg_min <= rev_end_dg <= self.end_stability_dg_max
        
        end_stability_ok = fwd_end_ok and rev_end_ok
        
        if fwd_end_dg < self.end_stability_dg_min:
            warnings.append(
                f"Forward primer 3' end ΔG ({fwd_end_dg:.2f}) too stable "
                f"(< {self.end_stability_dg_min}) — risk of non-specific priming"
            )
        elif fwd_end_dg > self.end_stability_dg_max:
            warnings.append(
                f"Forward primer 3' end ΔG ({fwd_end_dg:.2f}) too weak "
                f"(> {self.end_stability_dg_max}) — primer may not bind efficiently"
            )
            
        if rev_end_dg < self.end_stability_dg_min:
            warnings.append(
                f"Reverse primer 3' end ΔG ({rev_end_dg:.2f}) too stable "
                f"(< {self.end_stability_dg_min}) — risk of non-specific priming"
            )
        elif rev_end_dg > self.end_stability_dg_max:
            warnings.append(
                f"Reverse primer 3' end ΔG ({rev_end_dg:.2f}) too weak "
                f"(> {self.end_stability_dg_max}) — primer may not bind efficiently"
            )
            
        return {
            "end_stability_ok": end_stability_ok,
            "fwd_end_dg": fwd_end_dg,
            "rev_end_dg": rev_end_dg,
            "warnings": warnings
        }

    def evaluate_pair(self, fwd: Primer, rev: Primer) -> QCResult:
        """
        Evaluate a primer pair against all QC thresholds.
        
        This is the main entry point for checking a primer pair.
        
        Args:
            fwd: Forward primer
            rev: Reverse primer
            
        Returns:
            QCResult with all evaluation results
        """
        all_warnings = []
        errors = []

        # 1. Tm Balance
        tm_result = self.check_tm_balance(fwd, rev)
        all_warnings.extend(tm_result["warnings"])

        # 2. Hairpin
        hairpin_result = self.check_hairpin(fwd, rev)
        all_warnings.extend(hairpin_result["warnings"])

        # 3. Homodimer
        homodimer_result = self.check_homodimer(fwd, rev)
        all_warnings.extend(homodimer_result["warnings"])

        # 4. Heterodimer
        heterodimer_result = self.check_heterodimer(fwd, rev)
        all_warnings.extend(heterodimer_result["warnings"])

        # 5. End Stability
        end_stability_result = self.check_end_stability(fwd, rev)
        all_warnings.extend(end_stability_result["warnings"])

        # Construct Result
        result = QCResult(
            hairpin_ok=hairpin_result["hairpin_ok"],
            homodimer_ok=homodimer_result["homodimer_ok"],
            heterodimer_ok=heterodimer_result["heterodimer_ok"],
            end_stability_ok=end_stability_result["end_stability_ok"],
            tm_balance_ok=tm_result["tm_balance_ok"],
            hairpin_dg=min(hairpin_result["fwd_dg"], hairpin_result["rev_dg"]),
            homodimer_dg=min(homodimer_result["fwd_homo_dg"], homodimer_result["rev_homo_dg"]),
            heterodimer_dg=heterodimer_result["hetero_dg"],
            end_stability_dg=min(end_stability_result["fwd_end_dg"], end_stability_result["rev_end_dg"]),
            tm_diff=tm_result["tm_diff"],
            warnings=all_warnings,
            errors=errors
        )

        return result
