import primer3
from typing import Dict, Any, List
from primerlab.core.exceptions import ToolExecutionError
from primerlab.core.logger import get_logger

logger = get_logger()


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

        p3_settings = {
            'PRIMER_TASK': 'generic',
            'PRIMER_PICK_LEFT_PRIMER': 1,
            'PRIMER_PICK_RIGHT_PRIMER': 1,
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
        if qc_method == 'threshold':
            p3_settings.update({
                'PRIMER_MAX_SELF_ANY_TH':        params.get('max_self_any_th', 47.0),
                'PRIMER_MAX_SELF_END_TH':        params.get('max_self_end_th', 47.0),
                'PRIMER_PAIR_MAX_COMPL_ANY_TH':  params.get('max_pair_compl_any_th', 47.0),
                'PRIMER_PAIR_MAX_COMPL_END_TH':  params.get('max_pair_compl_end_th', 47.0),
                'PRIMER_MAX_HAIRPIN_TH':         params.get('max_hairpin_th', 47.0),
            })
        else:
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
            start  = max(target_region.get('start', 0), 0)
            length = target_region.get('length', 100)
            if start + length > len(sequence):
                length = len(sequence) - start
                logger.warning(f"Target region adjusted to fit sequence: {start},{length}")
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
        }
        for cfg_key, p3_key in forced_map.items():
            if cfg_key in params:
                seq_args[p3_key] = params[cfg_key]

        return seq_args

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

        # Probe Design (qPCR)
        probe_params = params.get('probe')
        if probe_params:
            p3_settings.update({
                'PRIMER_PICK_INTERNAL_OLIGO':   1,
                'PRIMER_INTERNAL_OPT_SIZE':     probe_params.get('size', {}).get('opt', 20),
                'PRIMER_INTERNAL_MIN_SIZE':     probe_params.get('size', {}).get('min', 18),
                'PRIMER_INTERNAL_MAX_SIZE':     probe_params.get('size', {}).get('max', 27),
                'PRIMER_INTERNAL_OPT_TM':       probe_params.get('tm', {}).get('opt', 70.0),
                'PRIMER_INTERNAL_MIN_TM':       probe_params.get('tm', {}).get('min', 68.0),
                'PRIMER_INTERNAL_MAX_TM':       probe_params.get('tm', {}).get('max', 72.0),
                'PRIMER_INTERNAL_MIN_GC':       probe_params.get('gc', {}).get('min', 30.0),
                'PRIMER_INTERNAL_MAX_GC':       probe_params.get('gc', {}).get('max', 80.0),
            })
            if thermo_params:
                p3_settings.update({
                    'PRIMER_INTERNAL_SALT_MONOVALENT': thermo_params.get('salt_monovalent', 50.0),
                    'PRIMER_INTERNAL_SALT_DIVALENT':   thermo_params.get('salt_divalent', 1.5),
                    'PRIMER_INTERNAL_DNTP_CONC':       thermo_params.get('dntp_conc', 0.6),
                    'PRIMER_INTERNAL_DNA_CONC':        thermo_params.get('dna_conc', 50.0),
                })

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

        # Use multiprocessing to enforce timeout and allow killing stuck processes
        import multiprocessing

        timeout_seconds = config.get("advanced", {}).get("timeout", 30)

        # Helper function for the worker process
        def _run_p3(seq_args, global_args, queue):
            try:
                res = primer3.bindings.design_primers(
                    seq_args=seq_args,
                    global_args=global_args
                )
                queue.put({"success": True, "data": res})
            except Exception as e:
                queue.put({"success": False, "error": str(e)})

        # Create a Queue to get results
        queue = multiprocessing.Queue()

        # Create and start the process
        p = multiprocessing.Process(
            target=_run_p3, 
            args=(seq_args, p3_settings, queue)
        )
        p.start()

        # Wait for the process with timeout
        p.join(timeout_seconds)

        if p.is_alive():
            # If still alive after timeout, kill it!
            logger.error(f"Primer3 process timed out ({timeout_seconds}s). Terminating...")
            p.terminate()
            p.join() # Clean up

            raise ToolExecutionError(
                f"Primer3 execution timed out after {timeout_seconds} seconds. "
                "This usually means the constraint combination is too strict for your sequence. "
                "Try: (1) Using a longer target sequence, (2) Relaxing probe Tm constraints "
                "(e.g., min: 65.0 instead of 68.0), or (3) Increasing timeout in config (advanced.timeout).", 
                "ERR_TOOL_P3_TIMEOUT"
            )

        # Check result
        if not queue.empty():
            result_wrapper = queue.get()
            if result_wrapper["success"]:
                data = result_wrapper["data"]

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
                return data
            else:
                raise ToolExecutionError(f"Primer3 failed: {result_wrapper['error']}", "ERR_TOOL_P3_001")
        else:
            # Should not happen if process exited cleanly without putting to queue
            raise ToolExecutionError("Primer3 process exited without returning result.", "ERR_TOOL_P3_CRASH")
