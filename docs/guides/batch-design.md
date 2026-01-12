# Batch Processing Guide

Design primers for multiple sequences in a single run.

## When to Use Batch Processing

- Designing primers for all exons of a gene
- Multi-gene panels
- High-throughput screening projects
- Genome-wide primer design

---

## Input Preparation

Create a multi-FASTA file with your target sequences:

```fasta
>BRCA1_exon1
ATGCGATCGATCGATCG...
>BRCA1_exon2
GCTAGCTAGCTAGCTAG...
>BRCA1_exon3
TACGTACGTACGTACGT...
```

---

## Running Batch Design

### Basic Usage

```bash
primerlab batch-run \
  --fasta genes.fasta \
  --config shared_config.yaml \
  --out batch_results/
```

### Parallel Processing

Speed up with multiple workers:

```bash
primerlab batch-run \
  --fasta genes.fasta \
  --config shared.yaml \
  --parallel 4
```

### Continue on Error

Skip failed sequences instead of stopping:

```bash
primerlab batch-run \
  --fasta genes.fasta \
  --config shared.yaml \
  --continue-on-error
```

---

## Shared Configuration

Create a config file for shared parameters:

```yaml
# shared_config.yaml
parameters:
  tm:
    opt: 60.0
  product_size:
    min: 150
    max: 300
  gc:
    min: 40.0
    max: 60.0

output:
  format: json
  include_rationale: true
```

All sequences will use these parameters.

---

## Output Structure

```
batch_results/
├── summary.json           # Overall statistics
├── summary.csv            # Tabular summary
├── BRCA1_exon1/
│   ├── primers.json
│   └── report.md
├── BRCA1_exon2/
│   ├── primers.json
│   └── report.md
└── BRCA1_exon3/
    ├── primers.json
    └── report.md
```

---

## Python API

```python
from primerlab import batch_design

results = batch_design(
    fasta_path="genes.fasta",
    config_path="shared_config.yaml",
    parallel=4,
    continue_on_error=True
)

# Process results
successful = 0
failed = 0

for seq_id, result in results.items():
    if result.success:
        successful += 1
        print(f"✅ {seq_id}: {len(result.primer_pairs)} pairs")
    else:
        failed += 1
        print(f"❌ {seq_id}: {result.error}")

print(f"\nTotal: {successful} successful, {failed} failed")
```

---

## Tips for Large Batches

### Memory Management

For large FASTA files (>1000 sequences), process in chunks:

```bash
# Split FASTA
split -l 200 large_genes.fasta chunk_

# Process each chunk
for chunk in chunk_*; do
  primerlab batch-run -f $chunk -c config.yaml -o results/
done
```

### Quality Control

After batch processing, review the summary:

```bash
# View success rate
cat batch_results/summary.json | jq '.success_rate'

# List failed sequences
cat batch_results/summary.json | jq '.failed[]'
```

---

## See Also

- [PCR Design](pcr-design) — Single sequence design
- [CLI Reference](../reference/cli) — All batch options
