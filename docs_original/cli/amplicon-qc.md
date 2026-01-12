# primerlab amplicon-qc

Validate qPCR amplicon quality and characteristics (v0.6.0).

## Usage

```bash
primerlab amplicon-qc --amplicon <SEQUENCE> [OPTIONS]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--amplicon`, `-a` | Yes | Amplicon sequence or FASTA file path |
| `--min-length` | No | Minimum length (default: 70 bp) |
| `--max-length` | No | Maximum length (default: 150 bp) |
| `--output`, `-o` | No | Output file path |
| `--format` | No | Output format: `text` or `json` |

## Examples

### Basic amplicon QC

```bash
primerlab amplicon-qc --amplicon ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG
```

Output:

```
═══════════════════════════════════════════════════════
                   AMPLICON QC (v0.6.0)
═══════════════════════════════════════════════════════
Length:           97 bp
GC Content:       50.5%
Amplicon Tm:      73.7°C

Validation:
  Length OK:      ✅
  GC OK:          ✅
  Structure OK:   ✅

Quality Score:    95/100
Grade:            A
```

### Custom length range

```bash
primerlab amplicon-qc \
  --amplicon ATGCGATCGATCGATCGATCG \
  --min-length 50 \
  --max-length 200
```

### From FASTA file

```bash
primerlab amplicon-qc --amplicon amplicon.fasta
```

### JSON output

```bash
primerlab amplicon-qc --amplicon ATGCGATCGATCGATCGATCG --format json -o result.json
```

## Validation Criteria

| Criterion | Optimal Range | Description |
|-----------|---------------|-------------|
| Length | 70-150 bp | qPCR optimal amplicon size |
| GC Content | 40-60% | Balanced base composition |
| Secondary Structure | ΔG > -3 kcal/mol | Minimal self-folding |

## Output Fields

| Field | Description |
|-------|-------------|
| Length | Amplicon length in bp |
| GC Content | Percentage of G+C bases |
| Amplicon Tm | Predicted melting temperature |
| Length OK | Passes length validation |
| GC OK | Passes GC content validation |
| Structure OK | Passes secondary structure check |
| Quality Score | Overall score (0-100) |
| Grade | Quality grade (A-F) |

## See Also

- [probe-check](probe-check.md) - TaqMan probe binding
- [melt-curve](melt-curve.md) - SYBR melt curve prediction
- [qPCR Advanced Tutorial](../tutorials/qpcr-advanced.md)
