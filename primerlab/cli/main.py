import argparse
import sys
import logging
from pathlib import Path
from primerlab.core.logger import setup_logger
from primerlab.core.config_loader import load_and_merge_config
from primerlab.core.exceptions import PrimerLabException

# Version definition
__version__ = "0.1.3-dev"

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

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)  # Changed to 0 for better UX

    if args.command == "version":
        print(f"PrimerLab v{__version__}")
        sys.exit(0)

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
                export_formats = ["idt"]  # Default
                if args.export:
                    export_formats = [f.strip().lower() for f in args.export.split(",")]
                
                for fmt in export_formats:
                    if fmt in ["idt", "sigma", "thermo"]:
                        output_mgr.save_ordering_format(result, fmt)
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

                logger.info(f"Primers found: {list(result.primers.keys())}")
                if result.amplicons:
                    logger.info(f"Amplicon size: {result.amplicons[0].length} bp")
                logger.info("Workflow finished successfully.")
            else:
                logger.warning("Workflow returned no results.")

        except PrimerLabException as e:
            logger.error(f"Error: {e}")
            if args.debug:
                logger.exception("Traceback:")
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
