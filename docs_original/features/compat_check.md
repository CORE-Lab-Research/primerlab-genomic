# Multiplex Analysis

> **v0.4.0** - Check compatibility of primer sets for multiplex PCR

## Overview

PrimerLab's Multiplex Analysis feature evaluates whether multiple primer pairs can be used together in a single PCR reaction by checking for cross-dimer formation, Tm uniformity, and GC content consistency.

## Key Features

| Feature | Description |
|---------|-------------|
| **Cross-Dimer Detection** | Identifies problematic primer-dimer interactions between all primer combinations |
| **Compatibility Scoring** | 0-100 score with A-F grading based on dimer ΔG, Tm spread, and GC uniformity |
| **Validation Engine** | Configurable thresholds with strict/standard/relaxed presets |
| **Export Formats** | JSON, Markdown, Excel (with matrix), IDT plate ordering format |

## Quick Start

### Standalone Analysis

```bash
# Basic analysis
primerlab multiplex --primers my_primers.json --output results/

# With custom config
primerlab multiplex --primers primers.json --config my_config.yaml
```

### Integrated with Workflow

```bash
# Run PCR design with multiplex check
primerlab run pcr --config design.yaml --check-multiplex
```

## Input Format

Create a JSON file with your primer pairs:

```json
[
  {
    "name": "GAPDH",
    "fwd": "ATGGGGAAGGTGAAGGTCGG",
    "rev": "GGATCTCGCTCCTGGAAGATG",
    "tm_fwd": 60.5,
    "tm_rev": 61.2,
    "gc_fwd": 60.0,
    "gc_rev": 57.0
  },
  {
    "name": "ACTB",
    "fwd": "CATGTACGTTGCTATCCAGGC",
    "rev": "CTCCTTAATGTCACGCACGAT",
    "tm_fwd": 59.8,
    "tm_rev": 58.9,
    "gc_fwd": 52.0,
    "gc_rev": 48.0
  }
]
```

## Output Reports

| Format | File | Description |
|--------|------|-------------|
| Markdown | `multiplex_report.md` | Human-readable summary with score, issues, recommendations |
| JSON | `multiplex_analysis.json` | Complete data for programmatic use |
| Excel | `multiplex_analysis.xlsx` | Summary + Primer Details + Compatibility Matrix sheets |
| IDT Plate | `idt_plate_order.csv` | Ready for IDT plate ordering |

## Scoring System

### Grade Thresholds

| Score | Grade | Interpretation |
|-------|-------|----------------|
| 85-100 | A | Excellent compatibility |
| 70-84 | B | Good, minor considerations |
| 55-69 | C | Acceptable, some issues |
| 40-54 | D | Problematic, redesign recommended |
| 0-39 | F | Incompatible, redesign required |

### Component Weights (Standard Mode)

| Component | Weight | Description |
|-----------|--------|-------------|
| Dimer Score | 40% | Based on cross-dimer ΔG values |
| Tm Uniformity | 25% | Penalty for Tm spread across primers |
| GC Uniformity | 15% | Penalty for GC content variation |
| Count Penalty | 20% | Penalty for large primer sets (>2 pairs) |

## Configuration

### Preset Modes

```yaml
multiplex:
  mode: standard  # Options: strict, standard, relaxed
```

| Mode | Dimer ΔG Threshold | Tm Spread Max | Use Case |
|------|-------------------|---------------|----------|
| strict | -5.0 kcal/mol | 1.5°C | High-throughput, critical applications |
| standard | -6.0 kcal/mol | 2.0°C | General multiplex PCR |
| relaxed | -9.0 kcal/mol | 3.0°C | Exploratory, non-critical |

### Custom Thresholds

```yaml
multiplex:
  mode: standard
  dimer_dg_threshold: -7.0  # Override specific values
  tm_diff_max: 2.5
  
  scoring:
    dimer_weight: 0.45
    tm_weight: 0.25
    gc_weight: 0.15
    count_weight: 0.15
```

## API Usage

```python
from primerlab.api import check_multiplex_compatibility

primers = [
    {"name": "GAPDH", "fwd": "ATGC...", "rev": "GCTA...", "tm_fwd": 60.0, "tm_rev": 60.0},
    {"name": "ACTB", "fwd": "TTTT...", "rev": "AAAA...", "tm_fwd": 59.0, "tm_rev": 59.0},
]

result = check_multiplex_compatibility(primers)

print(f"Score: {result['score']}/100 (Grade {result['grade']})")
print(f"Compatible: {result['is_valid']}")
print(f"Warnings: {result['warnings']}")
```

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Score drops with more pairs | Count penalty + more dimer combinations | Split into smaller multiplex groups |
| Low Tm uniformity score | Large Tm spread across primers | Redesign outlier primers |
| Problematic dimers | Strong cross-dimer formation | Avoid complementary 3' ends |

### Recommendations

1. **Optimal set size**: 2-5 primer pairs per multiplex
2. **Tm target**: Keep all primers within 2°C of each other
3. **GC content**: Aim for 40-60% for all primers
4. **3' end design**: Avoid complementary sequences at 3' ends

## See Also

- [CLI Reference](../cli/multiplex.md)
- [Configuration Guide](../configuration/README.md)
- [Troubleshooting](../troubleshooting.md)
