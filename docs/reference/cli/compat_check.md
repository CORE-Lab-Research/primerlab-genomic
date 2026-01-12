---
title: "primerlab multiplex"
description: "CLI reference for the primerlab multiplex command"
---
> Check multiplex compatibility of primer sets (v0.4.0)

## Synopsis

```bash
primerlab multiplex --primers <file.json> [options]
```

## Description

Analyzes a set of primer pairs for multiplex PCR compatibility by checking cross-dimer formation, Tm uniformity, and GC content consistency.

## Required Arguments

| Argument | Description |
|----------|-------------|
| `--primers`, `-p` | Path to JSON file containing primer pairs |

## Optional Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--config`, `-c` | - | Path to custom YAML config |
| `--output`, `-o` | `multiplex_output` | Output directory |
| `--format` | `markdown` | Report format (`markdown` or `json`) |

## Examples

### Basic Usage

```bash
# Analyze primers from JSON file
primerlab multiplex --primers my_primers.json

# Specify output directory
primerlab multiplex --primers primers.json --output results/

# Use custom configuration
primerlab multiplex --primers primers.json --config strict_config.yaml
```

### Input File Format

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
    "rev": "CTCCTTAATGTCACGCACGAT"
  }
]
```

**Note:** `tm_fwd`, `tm_rev`, `gc_fwd`, `gc_rev` are optional. If not provided, validation rules that depend on these values may flag warnings.

## Output Files

The command generates the following files in the output directory:

| File | Description |
|------|-------------|
| `multiplex_report.md` | Human-readable Markdown report |
| `multiplex_analysis.json` | Complete analysis in JSON format |
| `multiplex_analysis.xlsx` | Excel workbook with matrix (if openpyxl installed) |
| `idt_plate_order.csv` | IDT plate format for ordering |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Analysis complete, primers are compatible |
| 1 | Analysis complete, primers have compatibility issues |

## Integration with `run` Command

Use `--check-multiplex` flag with `primerlab run` to automatically check designed primers:

```bash
primerlab run pcr --config design.yaml --check-multiplex
```

## See Also

- [Multiplex Feature Guide](../features/multiplex)
- [Configuration Reference](../configuration/README)
