---
title: "BLAST Command"
description: "CLI reference for the BLAST Command command"
---
Off-target primer specificity check using BLAST+ or Biopython fallback.

## Quick Start

```bash
# Basic usage with comma-separated primers
primerlab blast -p "ATGACCATGATTACG,GCAACTGTTGGGAAG" -d genome.fasta

# Using primer file (FASTA or JSON)
primerlab blast -p primers.fasta -d database.fasta

# With target filtering
primerlab blast -p primers.json -d genome.fasta --target my_gene
```

## Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| `--primers` | `-p` | Primer input (JSON, FASTA, or comma-separated) **required** |
| `--database` | `-d` | Path to FASTA or BLAST database **required** |
| `--target` | `-t` | Expected target sequence ID |
| `--output` | `-o` | Output directory (default: `blast_output`) |
| `--json` | | Output JSON only |
| `--mode` | | Alignment mode: `auto`, `blast`, `biopython` |

## Input Formats

### Comma-separated

```bash
primerlab blast -p "ATGACCATGATTACG,GCAACTGTTGGGAAG" -d db.fasta
```

### JSON File

```json
{
  "forward": "ATGACCATGATTACG",
  "reverse": "GCAACTGTTGGGAAG"
}
```

### FASTA File

```fasta
>forward_primer
ATGACCATGATTACG
>reverse_primer
GCAACTGTTGGGAAG
```

## Output

### Console

```
🔬 Off-target Check (v0.3.0)
   Database: genome.fasta
   Forward:  ATGACCATGATTACG
   Reverse:  GCAACTGTTGGGAAG

✅ Specificity Score: 95.0 (Grade: A)
   Forward: 2 off-targets
   Reverse: 1 off-target

✅ Primers are specific!

📁 Output: blast_output
   • blast_result.json
   • specificity_report.md
```

### JSON Output (`blast_result.json`)

```json
{
  "forward": {
    "offtargets": 2,
    "score": 92.5
  },
  "reverse": {
    "offtargets": 1,
    "score": 97.5
  },
  "combined_score": 95.0,
  "grade": "A",
  "is_specific": true
}
```

## Scoring

| Grade | Score | Interpretation |
|-------|-------|----------------|
| A | 90-100 | Excellent specificity |
| B | 80-89 | Good specificity |
| C | 70-79 | Acceptable |
| D | 60-69 | Low specificity |
| F | &lt;60 | Poor specificity |

## Alignment Modes

- **auto** (default): Uses BLAST+ if installed, otherwise Biopython
- **blast**: Force BLAST+ (requires installation)
- **biopython**: Force Biopython pairwise aligner

## Integration with Design

Use `--blast` flag after primer design:

```bash
# Design and check in one command (if config has offtarget enabled)
primerlab run --config my_config.yaml --blast --blast-db genome.fasta
```

Or enable in config:

```yaml
offtarget:
  enabled: true
  database: /path/to/genome.fasta
  mode: auto
```

## See Also

- [In-silico PCR](insilico) - Validate primers against template
- [PCR Workflow](../workflows/pcr) - Full primer design pipeline
