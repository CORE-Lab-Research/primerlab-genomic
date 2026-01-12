# Tutorial: Batch Species-Check

Learn how to run species-check on multiple primer files efficiently.

## Prerequisites

- PrimerLab v0.4.3+
- Directory with primer JSON files
- Target and off-target FASTA files

## Step 1: Organize Primer Files

Create a directory with primer JSON files:

```
primers/
├── gene1_primers.json
├── gene2_primers.json
├── gene3_primers.json
└── ...
```

Each JSON file should have the standard format:

```json
[
  {"name": "Gene1", "forward": "ATGC...", "reverse": "GCTA..."}
]
```

## Step 2: Run Batch Analysis

### Using CLI

```bash
primerlab species-check \
  --primers-dir primers/ \
  --target target_human.fasta \
  --offtargets mouse.fasta,rat.fasta \
  --parallel 4 \
  --output batch_results/
```

### Options

| Option | Description |
|--------|-------------|
| `--primers-dir` | Directory with primer JSON files |
| `--parallel` | Number of threads (default: 4) |
| `--no-cache` | Disable alignment caching |

## Step 3: Using Python API

```python
from primerlab.api import batch_species_check_api

result = batch_species_check_api(
    primer_dir="primers/",
    target_name="Human",
    target_template=human_sequence,
    offtarget_templates={"Mouse": mouse_seq, "Rat": rat_seq},
    max_workers=4
)

print(f"Pass rate: {result['pass_rate']}%")
print(f"Passed: {result['passed']}/{result['total_files']}")
```

## Step 4: Interpret Results

### Summary Output

```
📊 Batch Analysis Complete
   Total Files: 10
   Passed: 8 (80%)
   Failed: 2 (20%)
   Avg Score: 87.5
```

### CSV Report

The CSV output includes:

- Filename
- Score (0-100)
- Grade (A-F)
- Is_Specific (True/False)
- Warnings

## Performance Tips

1. **Use Caching**: SQLite cache stores alignments for reuse
2. **Parallel Threads**: Match to CPU cores (default: 4)
3. **Organize by Project**: Keep related primers in same directory

## Troubleshooting

### Memory Issues

Reduce `--parallel` value for large primer sets.

### Slow Performance

Enable caching (default) for repeated analyses.

## See Also

- [Species Specificity Tutorial](species-check.md)
- [Tm Gradient Tutorial](tm-gradient.md)
