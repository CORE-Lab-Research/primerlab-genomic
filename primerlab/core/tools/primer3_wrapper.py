import primer3
from typing import Dict, Any, List
from primerlab.core.exceptions import ToolExecutionError, PrimerLabException
from primerlab.core.logger import get_logger

logger = get_logger()

# Helper function for the worker process (must be top-level for multiprocessing on Windows)
def _run_p3_process(seq_args, global_args, queue):
    try:
        res = primer3.bindings.design_primers(
            seq_args=seq_args,
            global_args=global_args
        )
        queue.put({"success": True, "data": res})
    except Exception as e:
        queue.put({"success": False, "error": str(e)})

class Primer3Wrapper:
    """
    Wrapper for primer3-py bindings.

    Provides helper methods (_build_p3_settings, _build_seq_args, etc.) that
    are separately testable without triggering a real Primer3 subprocess.
    """

    def _build_p3_settings(self, params: dict, workflow_type: str = 'pcr') -> dict:
        """
        Build the Primer3 global_args dict from a PrimerLab parameters dict.
        
        Separated from design_primers() so it can be unit-tested without
        triggering a real Primer3 subprocess.
        
        Args:
            params: The 'parameters' sub-dict from the full config.
            workflow_type: 'pcr' or 'qpcr' — affects defaults.
        
        Returns:
            Dict of Primer3 global_args.
        """
        default_num_candidates = 30 if workflow_type == 'qpcr' else 50

        # Task 4.4 and 4.5: pick_only support
        pick_left = 1
        pick_right = 1
        pick_internal = 1 if workflow_type == 'qpcr' else 0
        
        pick_only = params.get('pick_only', None)
        if pick_only == 'left':
            pick_right = 0
            pick_internal = 0
        elif pick_only == 'right':
            pick_left = 0
            pick_internal = 0
        elif pick_only == 'probe':
            pick_left = 0
            pick_right = 0
            pick_internal = 1

        p3_settings = {
            'PRIMER_TASK': 'pick_sequencing_primers' if workflow_type == 'sequencing' else (
                'pick_discriminative_primers' if workflow_type == 'discriminative' else 'generic'
            ),
            'PRIMER_PICK_LEFT_PRIMER': pick_left,
            'PRIMER_PICK_RIGHT_PRIMER': pick_right,
            'PRIMER_PICK_INTERNAL_OLIGO': pick_internal,
            'PRIMER_NUM_RETURN': params.get('num_candidates', default_num_candidates),

            # Size
            'PRIMER_OPT_SIZE': params.get('primer_size', {}).get('opt', 20),
            'PRIMER_MIN_SIZE': params.get('primer_size', {}).get('min', 18),
            'PRIMER_MAX_SIZE': params.get('primer_size', {}).get('max', 27),

            # Tm
            'PRIMER_OPT_TM': params.get('tm', {}).get('opt', 60.0),
            'PRIMER_MIN_TM': params.get('tm', {}).get('min', 57.0),
            'PRIMER_MAX_TM': params.get('tm', {}).get('max', 63.0),
            'PRIMER_PAIR_MAX_DIFF_TM': params.get('max_tm_diff', 5.0),

            # GC — Task 3.4
            'PRIMER_OPT_GC_PERCENT': params.get('gc', {}).get('opt', 50.0),
            'PRIMER_MIN_GC': params.get('gc', {}).get('min', 20.0),
            'PRIMER_MAX_GC': params.get('gc', {}).get('max', 80.0),

            # Poly-X and Ns — Tasks 3.1, 3.2
            'PRIMER_MAX_POLY_X': params.get('max_poly_x', 4),
            'PRIMER_MAX_NS_ACCEPTED': params.get('max_ns', 0),
        }

        if workflow_type == 'sequencing':
            p3_settings['PRIMER_SEQUENCING_LEAD'] = params.get('sequencing_lead', 50)
            p3_settings['PRIMER_SEQUENCING_SPACING'] = params.get('sequencing_spacing', 500)
            p3_settings['PRIMER_SEQUENCING_ACCURACY'] = params.get('sequencing_accuracy', 20)

        # Task 4.6 - Mispriming and Repeat Libraries
        if 'mispriming_library' in params:
            import os
            lib_path = params['mispriming_library']
            if os.path.exists(lib_path):
                p3_settings['PRIMER_MISPRIMING_LIBRARY'] = lib_path
                logger.info(f"Using mispriming library: {lib_path}")
            else:
                from primerlab.core.exceptions import PrimerLabException
                logger.error(f"Mispriming library not found: {lib_path}")
                raise PrimerLabException(f"Mispriming library not found: {lib_path}", "ERR_P3_LIB_NOT_FOUND")

        if 'repeat_library' in params:
            import os
            lib_path = params['repeat_library']
            if os.path.exists(lib_path):
                p3_settings['PRIMER_INTERNAL_MIPO_LIBRARY'] = lib_path
                logger.info(f"Using repeat library: {lib_path}")
            else:
                from primerlab.core.exceptions import PrimerLabException
                logger.error(f"Repeat library not found: {lib_path}")
                raise PrimerLabException(f"Repeat library not found: {lib_path}", "ERR_P3_LIB_NOT_FOUND")

        return p3_settings

    def _apply_thermo_settings(self, p3_settings: dict, thermo_params: dict) -> dict:
        """Apply thermodynamics config to p3_settings. Mutates and returns dict."""
        tm_method = thermo_params.get('tm_method', 'santalucia')
        p3_settings['PRIMER_TM_FORMULA'] = 1 if tm_method.lower() == 'santalucia' else 0

        salt_corr = thermo_params.get('salt_corrections', 'santalucia')
        p3_settings['PRIMER_SALT_CORRECTIONS'] = (
            1 if salt_corr.lower() == 'santalucia' else
            (2 if salt_corr.lower() == 'owczarzy' else 0)
        )

        p3_settings['PRIMER_SALT_MONOVALENT'] = thermo_params.get('salt_monovalent', 50.0)
        p3_settings['PRIMER_SALT_DIVALENT']   = thermo_params.get('salt_divalent', 1.5)
        p3_settings['PRIMER_DNTP_CONC']       = thermo_params.get('dntp_conc', 0.6)
        p3_settings['PRIMER_DNA_CONC']        = thermo_params.get('dna_conc', 50.0)
        return p3_settings

    def _apply_qc_method_settings(self, p3_settings: dict, params: dict) -> dict:
        """Apply Task 3.8 qc_method (threshold vs any) settings. Mutates and returns dict."""
        qc_method = params.get('qc_method', 'threshold')
        
        # Pull from 'qc' block if available, otherwise fallback to 'parameters'
        qc_cfg = params.get('qc', {})
        if not qc_cfg:
            # Try to find it in the root if params is the full config
            pass 

        if qc_method == 'threshold':
            # Default Tm thresholds for RAA (higher due to high salt/Mg)
            p3_settings.update({
                'PRIMER_MAX_SELF_ANY_TH':        params.get('max_self_any_th', 45.0),
                'PRIMER_MAX_SELF_END_TH':        params.get('max_self_end_th', 45.0),
                'PRIMER_PAIR_MAX_COMPL_ANY_TH':  params.get('max_pair_compl_any_th', 45.0),
                'PRIMER_PAIR_MAX_COMPL_END_TH':  params.get('max_pair_compl_end_th', 45.0),
                'PRIMER_MAX_HAIRPIN_TH':         params.get('max_hairpin_th', 45.0),
            })
        else:
            # Score-based thresholds
            p3_settings.update({
                'PRIMER_MAX_SELF_ANY':       params.get('max_self_any', 8.00),
                'PRIMER_MAX_SELF_END':       params.get('max_self_end', 3.00),
                'PRIMER_PAIR_MAX_COMPL_ANY': params.get('max_pair_compl_any', 8.00),
                'PRIMER_PAIR_MAX_COMPL_END': params.get('max_pair_compl_end', 3.00),
            })
        return p3_settings

    def _apply_weights(self, p3_settings: dict, weights: dict) -> dict:
        """Apply Task 3.10 primer weight settings. Mutates and returns dict."""
        weight_map = {
            'tm_gt':         'PRIMER_WT_TM_GT',
            'tm_lt':         'PRIMER_WT_TM_LT',
            'size_gt':       'PRIMER_WT_SIZE_GT',
            'size_lt':       'PRIMER_WT_SIZE_LT',
            'gc_percent_gt': 'PRIMER_WT_GC_PERCENT_GT',
            'gc_percent_lt': 'PRIMER_WT_GC_PERCENT_LT',
            'end_stability': 'PRIMER_WT_END_STABILITY',
        }
        for key, p3_key in weight_map.items():
            if key in weights:
                p3_settings[p3_key] = weights[key]
        return p3_settings

    def _build_seq_args(self, sequence: str, params: dict) -> dict:
        """
        Build the Primer3 seq_args dict from sequence and parameters.
        Handles target/excluded/included regions and forced positions.
        
        Separated from design_primers() so it can be unit-tested independently.
        """
        seq_args = {'SEQUENCE_TEMPLATE': sequence}

        # Target Region
        target_region = params.get('target_region')
        if target_region:
            start  = target_region.get('start', 0)
            length = target_region.get('length', 100)
            
            # Critical Fix: Ensure target is within current window
            if start >= len(sequence):
                logger.warning(f"Target region start ({start}) is outside current window ({len(sequence)}bp). Skipping target.")
            else:
                if start + length > len(sequence):
                    length = len(sequence) - start
                    logger.warning(f"Target region adjusted to fit window: {start},{length}")
                
                if length > 0:
                    seq_args['SEQUENCE_TARGET'] = [[start, length]]
                    logger.info(f"Target region set: position {start}, length {length}")

        # Excluded Regions
        excluded_regions = params.get('excluded_regions', [])
        if excluded_regions:
            formatted_regions = []
            for r in excluded_regions:
                if isinstance(r, (list, tuple)):
                    formatted_regions.append(list(r))
                elif isinstance(r, dict):
                    formatted_regions.append([r['start'], r['length']])
            if formatted_regions:
                seq_args['SEQUENCE_EXCLUDED_REGION'] = formatted_regions
                logger.info(f"Excluded regions: {len(formatted_regions)}")

        # Included Region — Task 3.5
        included_region = params.get('included_region')
        if included_region:
            start  = included_region.get('start', 0)
            length = included_region.get('length', len(sequence) - start)
            seq_args['SEQUENCE_INCLUDED_REGION'] = [start, length]
            logger.info(f"Included region set: position {start}, length {length}")

        # Forced Positions — Task 3.6
        forced_map = {
            'force_left_start':  'SEQUENCE_FORCE_LEFT_START',
            'force_left_end':    'SEQUENCE_FORCE_LEFT_END',
            'force_right_start': 'SEQUENCE_FORCE_RIGHT_START',
            'force_right_end':   'SEQUENCE_FORCE_RIGHT_END',
            'existing_forward':  'SEQUENCE_PRIMER',
            'existing_reverse':  'SEQUENCE_PRIMER_REVCOMP',
        }
        for cfg_key, p3_key in forced_map.items():
            val = params.get(cfg_key)
            if val is not None:
                seq_args[p3_key] = val

        return seq_args

    # Built-in restriction enzyme recognition sequences (5'→3' sense strand)
    RESTRICTION_SITES: Dict[str, str] = {
        # Type II enzymes (most common in cloning)
        'EcoRI':   'GAATTC',
        'EcoRV':   'GATATC',
        'BamHI':   'GGATCC',
        'BglII':   'AGATCT',
        'HindIII': 'AAGCTT',
        'NcoI':    'CCATGG',
        'NdeI':    'CATATG',
        'NheI':    'GCTAGC',
        'NotI':    'GCGGCCGC',
        'SalI':    'GTCGAC',
        'SpeI':    'ACTAGT',
        'XbaI':    'TCTAGA',
        'XhoI':    'CTCGAG',
        'SmaI':    'CCCGGG',   # isoschizomer of XmaI (blunt-end cutter)
        'KpnI':    'GGTACC',
        'SacI':    'GAGCTC',
        'PstI':    'CTGCAG',
        'SphI':    'GCATGC',
        'AvaI':    'CYCGRG',
        'ClaI':    'ATCGAT',
        'MluI':    'ACGCGT',
        'AgeI':    'ACCGGT',
        'BspEI':   'TCCGGA',
    }

    # GC clamp added between restriction site and primer to ensure cutting efficiency
    CLAMP = 'GC'

    def _apply_restriction_overhangs(
        self,
        p3_data: Dict[str, Any],
        add_sites: List[str],
        num_pairs: int
    ) -> Dict[str, Any]:
        """
        Task 4.10: Appends restriction site overhangs to the 5' end of
        primer sequences in raw Primer3 output.

        For each primer pair, prepend:
        - site[0] recognition sequence (+ GC clamp) to LEFT primers
        - site[1] recognition sequence (+ GC clamp) to RIGHT primers
        - If only one site given, applies to both ends

        Args:
            p3_data: Raw dict output from Primer3.
            add_sites: List of restriction enzyme names (e.g. ['EcoRI', 'BamHI']).
            num_pairs: Number of primer pairs returned.

        Returns:
            Modified p3_data with overhang-appended sequences.
        """
        if not add_sites:
            return p3_data

        # Resolve enzyme names (case-insensitive lookup)
        site_lookup = {k.upper(): v for k, v in self.RESTRICTION_SITES.items()}

        left_site_name  = add_sites[0].upper()
        right_site_name = add_sites[1].upper() if len(add_sites) > 1 else left_site_name

        left_recog  = site_lookup.get(left_site_name)
        right_recog = site_lookup.get(right_site_name)

        if not left_recog:
            logger.warning(f"Unknown restriction enzyme: {add_sites[0]}. Overhang not added to left primer.")
        if not right_recog:
            logger.warning(f"Unknown restriction enzyme: {add_sites[-1]}. Overhang not added to right primer.")

        for i in range(num_pairs):
            left_key  = f'PRIMER_LEFT_{i}_SEQUENCE'
            right_key = f'PRIMER_RIGHT_{i}_SEQUENCE'

            if left_recog and left_key in p3_data:
                original = p3_data[left_key]
                overhang = left_recog + self.CLAMP
                p3_data[left_key] = overhang + original
                p3_data[f'PRIMER_LEFT_{i}_OVERHANG'] = overhang
                logger.debug(
                    f"Pair {i} LEFT: added {add_sites[0]} overhang "
                    f"({overhang}) → {p3_data[left_key]}"
                )

            if right_recog and right_key in p3_data:
                original = p3_data[right_key]
                # Right primer overhang: reverse complement of recognition site
                # so it will appear as the correct site on the sense strand after PCR
                rc_map = str.maketrans('ATCG', 'TAGC')
                rc_recog = right_recog.translate(rc_map)[::-1]
                overhang = rc_recog + self.CLAMP
                p3_data[right_key] = overhang + original
                p3_data[f'PRIMER_RIGHT_{i}_OVERHANG'] = overhang
                logger.debug(
                    f"Pair {i} RIGHT: added {add_sites[-1]} RC overhang "
                    f"({overhang}) → {p3_data[right_key]}"
                )

        enzyme_summary = f"{add_sites[0]}" + (f" / {add_sites[1]}" if len(add_sites) > 1 else "")
        logger.info(
            f"Restriction site overhangs added: {enzyme_summary} "
            f"({num_pairs} pair(s) modified)"
        )
        return p3_data

    def check_existing_primers(self, forward: str, reverse: str, target: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates existing primers against a target sequence using Primer3.
        
        Args:
            forward: Forward primer sequence.
            reverse: Reverse primer sequence.
            target: Template DNA sequence.
            settings: Dictionary of Primer3 settings (thermodynamics, salt, etc.).
            
        Returns:
            Raw dictionary output from primer3.
        """
        seq_args = {
            'SEQUENCE_ID': 'check_run',
            'SEQUENCE_TEMPLATE': target,
            'SEQUENCE_PRIMER': forward,
            'SEQUENCE_PRIMER_REVCOMP': reverse
        }
        
        p3_settings = dict(settings)
        p3_settings['PRIMER_TASK'] = 'check_primers'
        
        logger.info(f"Checking existing primer pair against target...")
        try:
            return primer3.bindings.design_primers(seq_args, p3_settings)
        except Exception as e:
            logger.error(f"Failed to check primers: {str(e)}")
            raise PrimerLabException(f"Primer3 check failed: {str(e)}", "ERR_P3_CHECK")

    def design_primers(self, sequence: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs primer3 design with provided configuration.

        Args:
            sequence: The template DNA sequence.
            config: The full workflow configuration dictionary.

        Returns:
            Raw dictionary output from primer3.
        """
        params = config.get("parameters", {})
        workflow_type = config.get('workflow', 'pcr')

        # Build global settings via helper (testable)
        p3_settings = self._build_p3_settings(params, workflow_type)

        # Product Size Range
        if workflow_type == 'qpcr':
            default_range = [[70, 150]]
        else:
            default_range = [[75, 300]]
        p3_settings['PRIMER_PRODUCT_SIZE_RANGE'] = params.get('product_size_range', default_range)

        # Thermodynamics — Task 1.4
        thermo_params = params.get('thermodynamics', {})
        if thermo_params:
            self._apply_thermo_settings(p3_settings, thermo_params)

        # Probe Design (RAA/qPCR)
        probe_params = params.get('probe')
        if probe_params and probe_params.get('enabled', True):
            # Enforce internal oligo picking
            p3_settings['PRIMER_PICK_INTERNAL_OLIGO'] = 1
            
            # Map parameters dynamically from config
            p3_settings.update({
                'PRIMER_INTERNAL_OPT_SIZE':     probe_params.get('size', {}).get('opt', 20),
                'PRIMER_INTERNAL_MIN_SIZE':     probe_params.get('size', {}).get('min', 18),
                'PRIMER_INTERNAL_MAX_SIZE':     probe_params.get('size', {}).get('max', 35 if workflow_type != 'raa' else 60),
                'PRIMER_INTERNAL_OPT_TM':       probe_params.get('tm', {}).get('opt', 65.0),
                'PRIMER_INTERNAL_MIN_TM':       probe_params.get('tm', {}).get('min', 54.0),
                'PRIMER_INTERNAL_MAX_TM':       probe_params.get('tm', {}).get('max', 85.0),
                'PRIMER_INTERNAL_MIN_GC':       probe_params.get('gc', {}).get('min', 20.0),
                'PRIMER_INTERNAL_MAX_GC':       probe_params.get('gc', {}).get('max', 80.0),
                'PRIMER_INTERNAL_MAX_POLY_X':   probe_params.get('max_poly_x', 5),
            })

            # Loosen constraints for long RAA probes (otherwise P3 will reject them as "too stable")
            if p3_settings['PRIMER_INTERNAL_MAX_SIZE'] > 35:
                p3_settings.update({
                    'PRIMER_INTERNAL_MAX_SELF_ANY': 12.0,
                    'PRIMER_INTERNAL_MAX_SELF_END': 8.0,
                    'PRIMER_INTERNAL_MAX_HAIRPIN': 45.0, # Use TH-based or loose score
                })

            # Ensure probe salt matches primer salt (Critical for RAA)
            if thermo_params:
                p3_settings.update({
                    'PRIMER_INTERNAL_SALT_MONOVALENT': thermo_params.get('salt_monovalent', 50.0),
                    'PRIMER_INTERNAL_SALT_DIVALENT':   thermo_params.get('salt_divalent', 14.0 if workflow_type == 'raa' else 1.5),
                    'PRIMER_INTERNAL_DNTP_CONC':       thermo_params.get('dntp_conc', 0.8 if workflow_type == 'raa' else 0.6),
                    'PRIMER_INTERNAL_DNA_CONC':        thermo_params.get('dna_conc', 480.0 if workflow_type == 'raa' else 50.0),
                })
                
                # Task 4.7 Mishybridization library for probes
                if 'mishyb_library_path' in probe_params:
                    import os
                    lib_path = probe_params['mishyb_library_path']
                    if os.path.exists(lib_path):
                        p3_settings['PRIMER_INTERNAL_MISHYB_LIBRARY'] = lib_path
                        logger.info(f"Using probe mishybridization library: {lib_path}")
                    else:
                        from primerlab.core.exceptions import PrimerLabException
                        logger.error(f"Probe mishybridization library not found: {lib_path}")
                        raise PrimerLabException(f"Probe mishybridization library not found: {lib_path}", "ERR_P3_LIB_NOT_FOUND")

        # QC method — Task 3.8
        self._apply_qc_method_settings(p3_settings, params)

        # Must-Match ends — Task 3.7
        if 'must_match_five_prime' in params:
            p3_settings['PRIMER_MUST_MATCH_FIVE_PRIME'] = params['must_match_five_prime']
        if 'must_match_three_prime' in params:
            p3_settings['PRIMER_MUST_MATCH_THREE_PRIME'] = params['must_match_three_prime']

        # Primer Weights — Task 3.10
        weights = params.get('weights', {})
        if weights:
            self._apply_weights(p3_settings, weights)

        # Build sequence args via helper (testable)
        seq_args = self._build_seq_args(sequence, params)

        # Remove SEQUENCE_TEMPLATE from global settings (lives only in seq_args)
        p3_settings.pop('SEQUENCE_TEMPLATE', None)

        logger.info(f"Calling Primer3 binding with {len(p3_settings)} settings...")

        # Synchronous call (direct) to avoid IPC deadlocks in HPC
        import primer3
        
        logger.info(f"Executing Primer3 directly...")
        try:
            data = primer3.bindings.design_primers(seq_args, p3_settings)
        except Exception as e:
            logger.error(f"Primer3 execution failed: {str(e)}")
            raise ToolExecutionError(f"Primer3 failed: {str(e)}", "ERR_TOOL_P3_FAILED")

        # Check result
        if data:
            # Check if any primers were actually returned
            num_returned = data.get('PRIMER_LEFT_NUM_RETURNED', 0)
            if num_returned == 0:
                # Extract explanations
                left_explain = data.get('PRIMER_LEFT_EXPLAIN', 'N/A')
                right_explain = data.get('PRIMER_RIGHT_EXPLAIN', 'N/A')
                pair_explain = data.get('PRIMER_PAIR_EXPLAIN', 'N/A')

                error_msg = (
                    "Primer3 failed to find any primers.\n"
                    "Reasons:\n"
                    f"- Left Primer: {left_explain}\n"
                    f"- Right Primer: {right_explain}\n"
                    f"- Pair: {pair_explain}\n\n"
                    "Suggestion: Try relaxing constraints (e.g., wider Tm range, lower GC content) or using a different region."
                )

                # v0.1.5: Include structured details for Auto Parameter Suggestion
                raise ToolExecutionError(
                    error_msg, 
                    "ERR_TOOL_P3_NO_PRIMERS",
                    details={
                        "left_explain": left_explain,
                        "right_explain": right_explain,
                        "pair_explain": pair_explain,
                        "config_params": p3_settings
                    }
                )

            logger.info(f"Primer3 returned {num_returned} pairs.")

            # Task 4.10 — Restriction site overhang addition (cloning)
            add_sites = params.get('add_sites', [])
            if add_sites:
                data = self._apply_restriction_overhangs(data, add_sites, num_returned)

            return data
        else:
            raise ToolExecutionError("Primer3 returned no data.", "ERR_TOOL_P3_NO_DATA")
