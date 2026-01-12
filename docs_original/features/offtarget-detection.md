# Off-target Detection

**v0.3.0** - BLAST-based specificity analysis.

## Overview

PrimerLab checks primer specificity using BLAST alignment against reference databases.

## Features

- **Dual Backend**: BLAST+ or Biopython fallback
- **Parallel Processing**: Multi-threaded for speed (v0.3.2)
- **Caching**: Skip redundant alignments
- **Scoring**: A-F grades based on off-target count

## CLI Usage

### Standalone

```bash
primerlab blast -p primers.json -d genome.fasta
```

### Integrated with Design

```bash
primerlab run pcr --config my_config.yaml --blast --blast-db genome.fasta
```

### Config-based

```yaml
# my_config.yaml
offtarget:
  enabled: true
  database: /path/to/genome.fasta
  mode: auto  # auto, blast, biopython
```

## Scoring System

| Grade | Score | Off-targets | Risk |
|-------|-------|-------------|------|
| A | 90-100 | 0-2 | Minimal |
| B | 80-89 | 3-5 | Low |
| C | 70-79 | 6-10 | Moderate |
| D | 60-69 | 11-20 | High |
| F | <60 | >20 | Severe |

## Output

```json
{
  "forward": {
    "offtargets": 2,
    "score": 95.0
  },
  "reverse": {
    "offtargets": 1,
    "score": 97.5
  },
  "combined_score": 96.25,
  "grade": "A"
}
```

## Backend Selection

| Mode | Description |
|------|-------------|
| `auto` | BLAST+ if available, else Biopython |
| `blast` | Force BLAST+ (faster, requires install) |
| `biopython` | Pure Python (slower, always available) |

## See Also

- [BLAST Command](../cli/blast.md) - Detailed CLI options
- [In-silico PCR](../cli/insilico.md) - Template validation
