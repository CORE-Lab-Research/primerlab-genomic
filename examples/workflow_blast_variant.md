# End-to-End BLAST + Variant Workflow

Complete workflow demonstrating primer design → off-target check → variant analysis.

## Prerequisites

```bash
# Ensure dependencies are installed
pip install primerlab-genomic

# On Linux/WSL, Biopython is included as fallback for BLAST
# For best performance, install BLAST+:
sudo apt install ncbi-blast+
```

## Step 1: Design Primers

```bash
# Create a basic PCR config
primerlab init --workflow pcr -o my_config.yaml

# Edit the config with your sequence (or provide via command)
primerlab run --config my_config.yaml --output design_output
```

## Step 2: Off-target Check

```bash
# Check primer specificity against a database
primerlab blast \
  -p design_output/result.json \
  -d examples/blast/test_db.fasta \
  -o blast_output

# Or use comma-separated primers directly
primerlab blast \
  -p "ATGACCATGATTACG,GCAACTGTTGGGAAG" \
  -d genome.fasta
```

### Output Files

- `blast_output/blast_result.json` - Machine-readable results
- `blast_output/specificity_report.md` - Human-readable report

## Step 3: Variant Check (Optional)

```bash
# Check for SNPs in primer binding sites
primerlab blast \
  -p primers.fasta \
  -d genome.fasta \
  --variants variants.vcf \
  --maf-threshold 0.01
```

## Step 4: Integrated Workflow

Enable automatic off-target checking in your config:

```yaml
# my_config.yaml
offtarget:
  enabled: true
  database: /path/to/genome.fasta
  mode: auto
  evalue: 10.0
  identity: 70.0
```

Then run:

```bash
primerlab run --config my_config.yaml --blast
```

## Using the Python API

```python
from primerlab.api.public import design_pcr_primers, check_offtargets

# Design primers
result = design_pcr_primers(sequence)

# Check off-targets
fwd = result.primers["forward"].sequence
rev = result.primers["reverse"].sequence

offtarget_result = check_offtargets(
    forward_primer=fwd,
    reverse_primer=rev,
    database="genome.fasta"
)

print(f"Specificity: {offtarget_result['grade']}")
print(f"Score: {offtarget_result['specificity_score']}")
```

## Interpreting Results

| Grade | Score | Meaning |
|-------|-------|---------|
| A | 90-100 | Excellent - highly specific |
| B | 80-89 | Good - minor off-targets |
| C | 70-79 | Acceptable - some off-targets |
| D | 60-69 | Low - consider redesign |
| F | <60 | Poor - redesign recommended |

## Troubleshooting

### No alignment method available

Install BLAST+ or ensure Biopython is installed:

```bash
# BLAST+
sudo apt install ncbi-blast+

# Biopython (fallback)
pip install biopython
```

### VCF parsing errors

Ensure your VCF is version 4.x and tab-delimited:

```
##fileformat=VCFv4.2
#CHROM POS ID REF ALT QUAL FILTER INFO
chr1 100 rs001 A G 100 PASS AF=0.1
```
