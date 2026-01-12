# primerlab probe-check

Check TaqMan probe binding efficiency and thermodynamics (v0.6.0).

## Usage

```bash
primerlab probe-check --probe <SEQUENCE> [OPTIONS]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--probe`, `-p` | Yes | Probe sequence (5'→3') |
| `--amplicon`, `-a` | No | Amplicon sequence for position analysis |
| `--min-temp` | No | Minimum temperature (default: 55°C) |
| `--max-temp` | No | Maximum temperature (default: 72°C) |
| `--output`, `-o` | No | Output file path |
| `--format` | No | Output format: `text` or `json` |

## Examples

### Basic probe check

```bash
primerlab probe-check --probe ATGCGATCGATCGATCGATCG
```

Output:

```
═══════════════════════════════════════════════════════
                   PROBE BINDING CHECK (v0.6.0)
═══════════════════════════════════════════════════════
Probe:    ATGCGATCGATCGATCGATCG
Length:   21 bp

Results:
  Binding Tm:     65.2°C
  Grade:          A
  Quality Score:  92/100
```

### With amplicon context

```bash
primerlab probe-check \
  --probe ATGCGATCGATCGATCGATCG \
  --amplicon ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCG
```

### JSON output

```bash
primerlab probe-check --probe ATGCGATCGATCGATCGATCG --format json
```

### Save to file

```bash
primerlab probe-check --probe ATGCGATCGATCGATCGATCG -o probe_result.txt
```

## Output Fields

| Field | Description |
|-------|-------------|
| Binding Tm | Melting temperature of probe-target hybrid |
| Grade | Quality grade (A-F) |
| Quality Score | Overall score (0-100) |
| Position | Probe position within amplicon (if provided) |

## See Also

- [melt-curve](melt-curve.md) - SYBR melt curve prediction
- [amplicon-qc](amplicon-qc.md) - Amplicon quality check
- [Probe Binding Feature](../features/probe-binding.md)
