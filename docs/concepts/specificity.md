# Specificity Analysis

Ensuring primers amplify only the intended target.

## Overview

PrimerLab provides two complementary specificity checks:

| Method | Purpose | Speed |
|--------|---------|:-----:|
| In-silico PCR | Validate against template | Fast |
| BLAST Off-target | Search genome-wide | Slower |

---

## In-silico PCR

Simulates PCR amplification on your template sequence.

### What It Checks

1. **Primer binding sites** — Where primers can anneal
2. **Mismatch tolerance** — 5' mismatches allowed, 3' must match
3. **Product prediction** — Expected amplicon size and sequence
4. **Multiple products** — Detects non-specific amplification

### Usage

```bash
primerlab insilico \
  --primers primers.json \
  --template target.fasta
```

### Binding Rules

| Position | Mismatches Allowed |
|----------|:------------------:|
| 3' end (last 3 bp) | 0 |
| Internal | 2 |
| 5' end | 2-3 |

### Interpreting Results

```
✅ 1 product predicted
   720 bp at position 100-820
   Likelihood: 100%

⚠️ 2 products predicted
   Product 1: 720 bp (target)
   Product 2: 450 bp (off-target)
```

---

## BLAST Off-target Detection

Searches entire genome for potential binding sites.

### What It Checks

1. **Sequence similarity** — Primers matching other genomic regions
2. **Potential amplicons** — Off-target primer pairs that could amplify
3. **Specificity score** — Overall confidence in primer specificity

### Usage

```bash
primerlab blast \
  --primers primers.json \
  --database genome.fasta
```

### Scoring

| Grade | Score | Interpretation |
|:-----:|:-----:|----------------|
| A | 90-100 | Excellent specificity |
| B | 80-89 | Good specificity |
| C | 70-79 | Acceptable |
| D | 60-69 | Low specificity |
| F | <60 | Poor - redesign recommended |

### Factors Affecting Score

- Number of off-target hits
- Similarity to off-target regions
- Position of mismatches (3' is critical)
- Potential for off-target amplification

---

## Species Specificity

For diagnostic applications, ensure primers don't cross-react.

### Use Cases

- Pathogen detection (detect bacteria, not host)
- GMO testing
- Environmental monitoring

### Configuration

```yaml
specificity:
  target_database: ./pathogen.fasta
  background_database: ./host.fasta
  min_specificity_score: 90
```

### Command

```bash
primerlab species-check \
  --primers primers.json \
  --target-db pathogen.fasta \
  --background-db host.fasta
```

---

## Best Practices

### For High Specificity

1. **Check both directions** — Forward and reverse independently
2. **Use appropriate database** — Include all potential cross-reactants
3. **Consider 3' end** — Most critical for specificity
4. **Test experimentally** — In-silico is predictive, not definitive

### Database Selection

| Application | Database |
|-------------|----------|
| Human gene amplification | Human genome |
| Bacterial detection | Host genome + related species |
| Universal primers | RefSeq microbial |

---

## Workflow Integration

Run specificity checks as part of design:

```bash
# Design with automatic validation
primerlab run pcr \
  --config config.yaml \
  --validate \
  --blast --blast-db genome.fasta
```

Or check existing primers:

```bash
# Standalone check
primerlab blast -p primers.json -d genome.fasta
primerlab insilico -p primers.json -t template.fasta
```

---

## See Also

- [CLI Reference](../reference/cli) — All specificity commands
- [Quality Control](../guides/quality-control) — Other QC checks
