"""
Example: Running RAA Workflow for Influenza A (MP Segment)
This script demonstrates the Multi-Candidate Ranking and Deep QC logic.
"""

import os
import json
import yaml
from primerlab.workflows.raa.workflow import run_raa_workflow
from primerlab.core.logger import get_logger

logger = get_logger()

# 1. Mock Influenza A MP Segment (approx 200bp Golden Zone)
# This is a conserved region from the Matrix protein gene.
flu_sequence = (
    "AGCATGGTGCAGATGGTATGATCATTCTGAAACGTCATCAAGTAGAAACAGATGGTCCTG"
    "CAGCTGTAGCAGCAGCATTGGCTGTAGCAGCAGCATTGGCTGTAGCAGCAGCATTGGCTG"
    "TAGCAGCAGCATTGGCTGTAGCAGCAGCATTGGCTGTAGCAGCAGCATTGGCTGTAGCAG"
    "CAGCATTGGCTGTAGCAGCA"
)

# 2. Load Default RAA Configuration
config_path = os.path.join(os.getcwd(), "primerlab", "config", "raa_default.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# 3. Update Input
config["input"] = {
    "sequence": flu_sequence,
    "type": "dna"
}

# 4. Optional: Customize search depth (Multi-candidate)
config["parameters"]["num_candidates"] = 100 # Process top 100 triplets

try:
    logger.info("Starting RAA Analysis for Influenza A Example...")
    result = run_raa_workflow(config)
    
    # 5. Print Results
    print("\n" + "="*50)
    print("RAA DESIGN RESULTS (Top Candidate)")
    print("="*50)
    
    if result.primers:
        fwd = result.primers["forward"]
        rev = result.primers["reverse"]
        probe = result.primers.get("probe")
        
        print(f"Forward: {fwd.sequence} (Tm: {fwd.tm:.1f}C)")
        print(f"Reverse: {rev.sequence} (Tm: {rev.tm:.1f}C)")
        if probe:
            print(f"Probe:   {probe.sequence} (Tm: {probe.tm:.1f}C)")
            if "probe_annotation" in result.primers:
                print(f"Annotated Probe: {result.primers['probe_annotation']['annotated_sequence']}")
        
        print(f"\nAmplicon Size: {result.amplicons[0].length} bp")
        
        if result.qc:
            print(f"\nQC Warnings: {result.qc.warnings}")
            print(f"Cross-Dimer dG: {result.qc.cross_dimer_dg:.2f} kcal/mol")
    else:
        print("No valid candidates found.")

    # 6. Save results to JSON
    output_file = "raa_flu_result.json"
    with open(output_file, "w") as f:
        json.dump(result.to_dict(), f, indent=2)
    print(f"\nFull results saved to: {output_file}")

except Exception as e:
    logger.error(f"Execution failed: {e}")
