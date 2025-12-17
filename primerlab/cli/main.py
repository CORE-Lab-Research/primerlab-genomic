import argparse
import sys
import logging
from pathlib import Path
from primerlab.core.logger import setup_logger
from primerlab.core.config_loader import load_and_merge_config
from primerlab.core.exceptions import PrimerLabException

# Version definition
__version__ = "0.1.5"


def _run_health_check():
    """
    Check all dependencies and show system info.
    Per v0.1.3 quick patches - helps debugging installation issues.
    """
    import platform
    
    print(f"\n🔬 PrimerLab Health Check v{__version__}")
    print("=" * 45)
    
    # Python version
    py_version = platform.python_version()
    if py_version >= "3.10":
        print(f"✅ Python {py_version}")
    else:
        print(f"⚠️ Python {py_version} (recommend 3.10+)")
    
    # Primer3-py
    try:
        import primer3
        print(f"✅ primer3-py (installed)")
    except ImportError:
        print("❌ primer3-py NOT FOUND (required)")
    
    # ViennaRNA
    try:
        from primerlab.core.tools.vienna_wrapper import ViennaWrapper
        vienna = ViennaWrapper()
        if vienna.is_available:  # Property, not method
            print(f"✅ ViennaRNA (available)")
        else:
            print("⚠️ ViennaRNA not found (optional, install for secondary structure QC)")
    except Exception as e:
        print(f"⚠️ ViennaRNA check failed: {e}")
    
    # PyYAML
    try:
        import yaml
        print(f"✅ PyYAML (installed)")
    except ImportError:
        print("❌ PyYAML NOT FOUND (required)")
    
    # Rich
    try:
        import rich
        version = getattr(rich, "__version__", "installed")
        print(f"✅ Rich {version}")
    except ImportError:
        print("⚠️ Rich not found (optional, for colorized output)")
    
    # tqdm
    try:
        import tqdm
        version = getattr(tqdm, "__version__", "installed")
        print(f"✅ tqdm {version}")
    except ImportError:
        print("⚠️ tqdm not found (optional, for progress bars)")
    
    # Biopython (optional)
    try:
        import Bio
        print(f"✅ Biopython {Bio.__version__}")
    except ImportError:
        print("⚠️ Biopython not found (optional, for advanced sequence parsing)")
    
    print("\n" + "=" * 45)
    print("Health check complete.\n")

def main():
    parser = argparse.ArgumentParser(
        description="PrimerLab: Automated Primer Design Framework",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument("--version", action="version", version=f"PrimerLab v{__version__}")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # --- VERSION Command ---
    subparsers.add_parser("version", help="Show version info")

    # --- RUN Command ---
    run_parser = subparsers.add_parser("run", help="Run a specific workflow")
    run_parser.add_argument("workflow", choices=["pcr", "qpcr", "crispr"], help="Workflow to run")
    run_parser.add_argument("--config", "-c", type=str, help="Path to user config YAML file")
    run_parser.add_argument("--out", "-o", type=str, help="Override output directory")
    run_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    run_parser.add_argument("--dry-run", action="store_true", help="Validate config without running workflow")
    run_parser.add_argument("--export", "-e", type=str, 
                           help="Export formats: comma-separated (e.g., --export idt,sigma,thermo)")

    # --- BATCH-GENERATE Command ---
    batch_parser = subparsers.add_parser("batch-generate", help="Generate multiple configs from CSV")
    batch_parser.add_argument("--input", "-i", type=str, required=True, help="Input CSV file")
    batch_parser.add_argument("--output", "-o", type=str, default="./configs", help="Output directory for configs")
    batch_parser.add_argument("--workflow", "-w", type=str, choices=["pcr", "qpcr"], default="pcr", help="Workflow type")

    # --- INIT Command (v0.1.3) ---
    init_parser = subparsers.add_parser("init", help="Generate a template configuration file")
    init_parser.add_argument("--workflow", "-w", type=str, choices=["pcr", "qpcr"], default="pcr", 
                            help="Workflow type (default: pcr)")
    init_parser.add_argument("--output", "-o", type=str, default="config.yaml", 
                            help="Output filename (default: config.yaml)")

    # --- HEALTH Command (v0.1.3) ---
    subparsers.add_parser("health", help="Check all dependencies and show system info")

    # --- VALIDATE Command (v0.1.5) ---
    validate_parser = subparsers.add_parser("validate", help="Validate a configuration file")
    validate_parser.add_argument("config", type=str, help="Path to config YAML file to validate")
    validate_parser.add_argument("--workflow", "-w", type=str, choices=["pcr", "qpcr"], default="pcr",
                                help="Workflow type (default: pcr)")

    # --- PRESET Command (v0.1.5) ---
    preset_parser = subparsers.add_parser("preset", help="Manage and view presets")
    preset_subparsers = preset_parser.add_subparsers(dest="preset_action", help="Preset actions")
    
    # preset list
    preset_subparsers.add_parser("list", help="List all available presets")
    
    # preset show <name>
    preset_show = preset_subparsers.add_parser("show", help="Show details of a specific preset")
    preset_show.add_argument("name", type=str, help="Name of preset to show")

    # --- COMPARE Command (v0.1.5) ---
    compare_parser = subparsers.add_parser("compare", help="Compare two primer design results")
    compare_parser.add_argument("result_a", type=str, help="Path to first result.json")
    compare_parser.add_argument("result_b", type=str, help="Path to second result.json")
    compare_parser.add_argument("--labels", "-l", type=str, default="A,B",
                               help="Labels for comparison (default: A,B)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)  # Changed to 0 for better UX

    if args.command == "version":
        print(f"PrimerLab v{__version__}")
        sys.exit(0)

    # --- HEALTH Command Handler ---
    if args.command == "health":
        _run_health_check()
        sys.exit(0)

    # --- VALIDATE Command Handler (v0.1.5) ---
    if args.command == "validate":
        logger = setup_logger(level=logging.INFO)
        logger.info(f"🔍 Validating configuration: {args.config}")
        
        try:
            config = load_and_merge_config(
                workflow=args.workflow,
                user_config_path=args.config
            )
            print("\n✅ Configuration is valid!")
            print(f"   Workflow: {args.workflow.upper()}")
            print(f"   Output: {config['output']['directory']}")
            
            params = config.get('parameters', {})
            if params.get('tm'):
                print(f"   Tm Range: {params['tm'].get('min', '?')} - {params['tm'].get('max', '?')} °C")
            if params.get('product_size_range'):
                ranges = params['product_size_range']
                print(f"   Product Size: {ranges[0][0]} - {ranges[0][1]} bp")
            if params.get('primer_naming'):
                print(f"   Primer Naming: custom pattern configured")
            
            sys.exit(0)
        except PrimerLabException as e:
            print(f"\n❌ Configuration Error: {e.message}")
            print(f"   Error Code: {e.code}")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected Error: {e}")
            sys.exit(1)

    # --- PRESET Command Handler (v0.1.5) ---
    if args.command == "preset":
        from pathlib import Path
        import yaml
        
        preset_dir = Path(__file__).parent.parent / "config"
        
        if args.preset_action == "list":
            print("\n📋 Available Presets:\n")
            preset_files = list(preset_dir.glob("*_default.yaml"))
            
            # Filter out workflow defaults, show only special presets
            presets = [p.stem.replace("_default", "") for p in preset_files 
                      if p.stem not in ["pcr_default", "qpcr_default"]]
            
            if presets:
                for preset in sorted(presets):
                    print(f"  • {preset}")
                print(f"\nUse 'primerlab preset show <name>' for details.")
            else:
                print("  No custom presets found.")
                print("  Built-in workflows: pcr, qpcr")
            
            sys.exit(0)
        
        elif args.preset_action == "show":
            preset_name = args.name
            preset_file = preset_dir / f"{preset_name}_default.yaml"
            
            if not preset_file.exists():
                print(f"\n❌ Preset '{preset_name}' not found.")
                print("   Use 'primerlab preset list' to see available presets.")
                sys.exit(1)
            
            print(f"\n📄 Preset: {preset_name}\n")
            print("-" * 40)
            
            with open(preset_file, 'r') as f:
                content = f.read()
                print(content)
            
            sys.exit(0)
        
        else:
            print("Usage: primerlab preset [list|show <name>]")
            sys.exit(1)

    if args.command == "run":
        # 1. Setup Logging
        log_level = logging.DEBUG if args.debug else logging.INFO
        logger = setup_logger(level=log_level)
        
        logger.info(f"Starting PrimerLab v{__version__}")
        logger.info(f"Workflow: {args.workflow.upper()}")

        # Early check for unimplemented workflows
        if args.workflow == "crispr":
            logger.error("CRISPR workflow is not yet implemented. Please use 'pcr' or 'qpcr'.")
            sys.exit(2)

        try:
            # 2. Prepare CLI Overrides
            overrides = {}
            if args.out:
                overrides["output"] = {"directory": args.out}
            if args.debug:
                overrides["advanced"] = {"debug": True}

            # 3. Load Configuration
            config = load_and_merge_config(
                workflow=args.workflow,
                user_config_path=args.config,
                cli_overrides=overrides
            )
            
            logger.info("Configuration loaded successfully.")
            logger.debug(f"Final Config: {config}")
            
            # Check for dry-run mode
            if args.dry_run:
                logger.info("✅ Dry-run complete. Configuration is valid.")
                logger.info(f"   Workflow: {args.workflow}")
                logger.info(f"   Output: {config['output']['directory']}")
                params = config.get('parameters', {})
                if params.get('tm'):
                    logger.info(f"   Tm Range: {params['tm'].get('min', '?')} - {params['tm'].get('max', '?')} °C")
                if params.get('product_size'):
                    logger.info(f"   Product Size: {params['product_size'].get('min', '?')} - {params['product_size'].get('max', '?')} bp")
                sys.exit(0)

            # 4. Run Workflow
            logger.info("Initializing workflow engine...")
            
            result = None
            if args.workflow == "pcr":
                from primerlab.workflows.pcr import run_pcr_workflow
                result = run_pcr_workflow(config)
            elif args.workflow == "qpcr":
                from primerlab.workflows.qpcr import run_qpcr_workflow
                result = run_qpcr_workflow(config)
            
            if result is not None:
                # 5. Save Output
                from primerlab.core.output import OutputManager
                
                out_dir = config["output"]["directory"]
                output_mgr = OutputManager(out_dir, args.workflow)
                
                output_mgr.save_json(result)
                output_mgr.save_csv(result)
                
                # Export vendor formats (v0.1.3)
                # Priority: CLI --export flag > config output.export_formats > default ["idt"]
                export_formats = ["idt"]  # Default
                
                # Check config for export_formats
                config_formats = config.get("output", {}).get("export_formats", [])
                if config_formats:
                    export_formats = [f.strip().lower() for f in config_formats]
                
                # CLI flag overrides config
                if args.export:
                    export_formats = [f.strip().lower() for f in args.export.split(",")]
                
                for fmt in export_formats:
                    if fmt in ["idt", "sigma", "thermo"]:
                        output_mgr.save_ordering_format(result, fmt)
                    elif fmt == "xlsx":
                        # v0.1.4: Excel export
                        output_mgr.save_excel(result)
                    elif fmt == "idt_bulk":
                        # v0.1.4: IDT bulk order with plate positions
                        output_mgr.save_idt_bulk_order(result)
                    elif fmt == "html":
                        # v0.1.4: HTML report
                        output_mgr.save_html(result)
                    elif fmt == "benchling":
                        # v0.1.5: Benchling CSV export
                        output_mgr.save_benchling_csv(result)
                    elif fmt in ["json", "csv"]:
                        # json and csv are saved by default, no extra action needed
                        pass
                    else:
                        logger.warning(f"Unknown export format: {fmt}")
                
                # 6. Generate Report
                if args.workflow == "qpcr":
                    from primerlab.workflows.qpcr.report import qPCRReportGenerator
                    report_gen = qPCRReportGenerator()
                else:
                    from primerlab.workflows.pcr.report import ReportGenerator
                    report_gen = ReportGenerator()
                
                report_content = report_gen.generate_report(result)
                
                # Save report
                report_path = output_mgr.run_dir / "report.md"
                with open(report_path, "w") as f:
                    f.write(report_content)
                logger.info(f"Report saved to: {report_path}")

                if config.get("advanced", {}).get("debug"):
                    output_mgr.save_debug_data(result.raw, "primer3_raw.json")
                    output_mgr.save_debug_data(config, "final_config.json")

                # 7. Print colorized summary (v0.1.3)
                try:
                    from primerlab.cli.console import print_primer_summary, print_qc_status, print_success
                    print_primer_summary(result)
                    print_qc_status(result)
                    print_success(f"Workflow finished! Output: {output_mgr.run_dir}")
                except ImportError:
                    # Fallback if rich not available
                    logger.info(f"Primers found: {list(result.primers.keys())}")
                    if result.amplicons:
                        logger.info(f"Amplicon size: {result.amplicons[0].length} bp")
                    logger.info("Workflow finished successfully.")
            else:
                logger.warning("Workflow returned no results.")

        except PrimerLabException as e:
            logger.error(f"Error: {e}")
            
            # v0.1.5: Auto Parameter Suggestion for design failures
            if hasattr(e, 'error_code') and e.error_code == "ERR_TOOL_P3_NO_PRIMERS":
                try:
                    from primerlab.core.suggestion import suggest_relaxed_parameters, format_suggestions_for_cli
                    suggestion_result = suggest_relaxed_parameters(config, getattr(e, 'details', None))
                    print(format_suggestions_for_cli(suggestion_result))
                except Exception as suggestion_error:
                    logger.debug(f"Could not generate suggestions: {suggestion_error}")
            
            if args.debug:
                logger.exception("Traceback:")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected Error: {e}")
            logger.exception("Traceback:")
            sys.exit(1)

    # --- COMPARE Command Handler (v0.1.5) ---
    if args.command == "compare":
        logger = setup_logger(level=logging.INFO)
        logger.info(f"🔬 PrimerLab Primer Comparison v{__version__}")
        
        try:
            from primerlab.core.comparison import compare_primers, format_comparison_for_cli, load_result_json
            
            # Parse labels
            labels = tuple(args.labels.split(",")[:2])
            if len(labels) < 2:
                labels = ("A", "B")
            
            # Load results
            result_a = load_result_json(args.result_a)
            result_b = load_result_json(args.result_b)
            
            # Compare
            comparison = compare_primers(result_a, result_b, labels)
            
            # Display
            print(format_comparison_for_cli(comparison, labels))
            
            sys.exit(0)
            
        except FileNotFoundError as e:
            logger.error(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected Error: {e}")
            logger.exception("Traceback:")
            sys.exit(1)

    if args.command == "batch-generate":
        logger = setup_logger(level=logging.INFO)
        logger.info(f"Starting PrimerLab Batch Generator v{__version__}")
        
        try:
            from primerlab.cli.batch_generator import generate_configs_from_csv
            
            generated = generate_configs_from_csv(
                csv_path=args.input,
                output_dir=args.output,
                workflow=args.workflow
            )
            
            logger.info(f"✅ Successfully generated {len(generated)} config files")
            for f in generated:
                print(f"  - {f}")
            
        except FileNotFoundError as e:
            logger.error(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected Error: {e}")
            sys.exit(1)

    if args.command == "init":
        # Generate template configuration file (v0.1.3)
        logger = setup_logger(level=logging.INFO)
        logger.info(f"Generating template config for {args.workflow.upper()} workflow...")
        
        templates = {
            "pcr": '''# PrimerLab Configuration - PCR Workflow
# Generated by: primerlab init

workflow: pcr

input:
  # Provide EITHER sequence directly OR a file path
  sequence: "YOUR_SEQUENCE_HERE"
  # sequence_path: "path/to/sequence.fasta"

parameters:
  # Primer constraints
  primer_size:
    min: 18
    opt: 20
    max: 27
  
  # Melting temperature (°C)
  tm:
    min: 57.0
    opt: 60.0
    max: 63.0
  
  # GC content (%)
  gc:
    min: 40.0
    max: 60.0
  
  # Amplicon size (bp)
  product_size_range: [[100, 300]]
  
  # Multi-candidate options (v0.1.3)
  # num_candidates: 50  # Number of primers to evaluate

output:
  directory: "./output_pcr"

# QC settings
qc:
  # mode: standard  # strict, standard, relaxed
  hairpin_dg_min: -3.0
  dimer_dg_min: -6.0
''',
            "qpcr": '''# PrimerLab Configuration - qPCR Workflow
# Generated by: primerlab init

workflow: qpcr

input:
  sequence: "YOUR_SEQUENCE_HERE"
  # sequence_path: "path/to/sequence.fasta"

parameters:
  primer_size:
    min: 18
    opt: 20
    max: 25
  
  tm:
    min: 57.0
    opt: 60.0
    max: 63.0
  
  gc:
    min: 40.0
    max: 60.0
  
  # qPCR-specific: smaller amplicon
  product_size_range: [[70, 150]]
  
  # Probe settings (for TaqMan)
  probe:
    size:
      min: 18
      opt: 20
      max: 25
    tm:
      min: 65.0
      opt: 68.0
      max: 72.0
  
  # Multi-candidate options
  # num_candidates: 30

output:
  directory: "./output_qpcr"

qc:
  hairpin_dg_min: -3.0
  dimer_dg_min: -6.0
'''
        }
        
        template = templates.get(args.workflow, templates["pcr"])
        output_file = Path(args.output)
        
        if output_file.exists():
            logger.warning(f"File {args.output} already exists. Overwrite? (y/n)")
            response = input().strip().lower()
            if response != 'y':
                logger.info("Aborted.")
                sys.exit(0)
        
        with open(output_file, "w") as f:
            f.write(template)
        
        logger.info(f"✅ Created config file: {output_file}")
        logger.info(f"   Edit the file to add your sequence, then run:")
        logger.info(f"   primerlab run {args.workflow} --config {output_file}")

if __name__ == "__main__":
    main()
