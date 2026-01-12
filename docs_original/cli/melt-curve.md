# primerlab melt-curve

Predict SYBR Green melt curve for amplicon analysis (v0.6.0).

## Usage

```bash
primerlab melt-curve --amplicon <SEQUENCE> [OPTIONS]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--amplicon`, `-a` | Yes | Amplicon sequence or FASTA file path |
| `--output`, `-o` | No | Output file path for plot |
| `--format` | No | Output format: `text`, `json`, `svg`, `png` |
| `--min-temp` | No | Minimum temperature (default: 65°C) |
| `--max-temp` | No | Maximum temperature (default: 95°C) |

## Examples

### Basic melt curve prediction

```bash
primerlab melt-curve --amplicon ATGCGATCGATCGATCGATCGATCGATCGATCG
```

Output:

```
═══════════════════════════════════════════════════════
                   MELT CURVE PREDICTION (v0.6.0)
═══════════════════════════════════════════════════════
Amplicon Length:  33 bp
Predicted Tm:     72.5°C
Tm Range:         70.0 - 75.0°C
Single Peak:      ✅ Yes
Quality Score:    95/100
Grade:            A
```

### Generate SVG plot

```bash
primerlab melt-curve \
  --amplicon ATGCGATCGATCGATCGATCGATCGATCGATCG \
  --format svg \
  --output melt_curve.svg
```

### Generate PNG plot

```bash
primerlab melt-curve \
  --amplicon ATGCGATCGATCGATCGATCGATCGATCGATCG \
  --format png \
  --output melt_curve.png
```

### From FASTA file

```bash
primerlab melt-curve --amplicon amplicon.fasta --format json
```

### JSON output

```bash
primerlab melt-curve --amplicon ATGCGATCGATCGATCGATCG --format json
```

## Output Fields

| Field | Description |
|-------|-------------|
| Predicted Tm | Primary melting temperature |
| Tm Range | Expected Tm variation |
| Single Peak | Whether curve shows single specific product |
| Quality Score | Overall score (0-100) |
| Grade | Quality grade (A-F) |

## Output Formats

| Format | Description |
|--------|-------------|
| `text` | Human-readable summary (default) |
| `json` | Full data as JSON |
| `svg` | Vector plot (no dependencies) |
| `png` | Raster plot (requires matplotlib) |

## See Also

- [probe-check](probe-check.md) - TaqMan probe binding
- [amplicon-qc](amplicon-qc.md) - Amplicon quality check
- [Melt Curve Feature](../features/melt-curve.md)
