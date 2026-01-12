---
title: "primerlab tm-gradient"
description: "CLI reference for the primerlab tm-gradient command"
---
Simulate temperature gradients to find optimal annealing temperatures.

## Synopsis

```bash
primerlab tm-gradient --primers FILE [OPTIONS]
```

## Description

The `tm-gradient` command simulates primer binding efficiency across a temperature range using nearest-neighbor thermodynamics. It predicts the optimal annealing temperature for your primer set.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--primers, -p` | Yes | Path to primers JSON file |
| `--template, -t` | No | Optional template FASTA for context |
| `--min-temp` | No | Minimum temperature °C (default: 50.0) |
| `--max-temp` | No | Maximum temperature °C (default: 72.0) |
| `--step` | No | Temperature step °C (default: 0.5) |
| `--output, -o` | No | Output directory (default: tm_gradient_output) |
| `--format` | No | Report format: json, markdown, csv (default: json) |

## Examples

### Basic Usage

```bash
primerlab tm-gradient --primers primers.json
```

### Custom Temperature Range

```bash
primerlab tm-gradient \
  --primers primers.json \
  --min-temp 55 \
  --max-temp 68 \
  --step 0.5
```

### Markdown Report

```bash
primerlab tm-gradient \
  --primers primers.json \
  --output results/ \
  --format markdown
```

### CSV Export

```bash
primerlab tm-gradient \
  --primers primers.json \
  --format csv
```

## Input Format

### primers.json

```json
[
  {"name": "Gene1", "forward": "ATGCGATCGATCGATCGATCG", "reverse": "CGATCGATCGATCGATCGCAT"},
  {"name": "Gene2", "forward": "GCGCGCGCGCGCGCGCGCGC", "reverse": "ATATATATATATATATATATAT"}
]
```

## Output

### Console Output

```
🌡️ Tm Gradient Simulation (v0.4.3)
==================================================
📂 Loading primers: primers.json
🔬 Temperature range: 50.0°C - 72.0°C (step 0.5°C)

⏳ Simulating Tm gradient for 4 primers...

==================================================
🎯 Optimal Annealing Temperature: 58.5°C
   Recommended Range: 55.0°C - 62.0°C

📊 Per-Primer Results:
   Gene1_fwd: Tm=62.3°C, Optimal=57.3°C (Grade A)
   Gene1_rev: Tm=60.8°C, Optimal=55.8°C (Grade A)
   Gene2_fwd: Tm=68.5°C, Optimal=63.5°C (Grade B)
   Gene2_rev: Tm=52.1°C, Optimal=47.1°C (Grade C)

📁 Reports saved to: tm_gradient_output
   • tm_gradient.json
```

### Report Files

- `tm_gradient.json` - Full JSON data with efficiency curves
- `tm_gradient_report.md` - Markdown summary
- `tm_gradient.csv` - CSV data for analysis

## Thermodynamic Model

Uses Santa Lucia (1998) nearest-neighbor parameters:

- ΔH and ΔS for each dinucleotide pair
- Salt correction for Na+ concentration
- Two-state binding model

## Grading

| Grade | Score | Interpretation |
|-------|-------|----------------|
| A | ≥90 | Wide temperature tolerance |
| B | 80-89 | Good stability |
| C | 70-79 | Moderate sensitivity |
| D | 60-69 | Narrow window |
| F | &lt;60 | Redesign recommended |

## See Also

- [Tm Gradient Feature](../features/tm-gradient)
- [Tm Gradient Tutorial](../tutorials/tm-gradient)
