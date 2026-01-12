---
title: "primerlab batch-run"
description: "CLI reference for the primerlab batch-run command"
---
Run multiple primer designs in batch mode.

## Synopsis

```bash
primerlab batch-run [options]
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--configs` | `-c` | Directory with configs OR comma-separated paths |
| `--fasta` | `-f` | Multi-FASTA file with multiple sequences |
| `--config` | | Shared config for multi-FASTA mode |
| `--output` | `-o` | Output directory (default: ./batch_output) |
| `--export` | `-e` | Export format for summary (default: xlsx) |
| `--continue-on-error` | | Continue if some designs fail |

## Modes

### Mode 1: Multiple Config Files

```bash
# From directory
primerlab batch-run --configs ./configs/ --output ./results/

# From specific files
primerlab batch-run --configs config1.yaml,config2.yaml --output ./results/
```

### Mode 2: Multi-FASTA with Shared Config

```bash
primerlab batch-run --fasta genes.fasta --config shared.yaml --output ./results/
```

## Examples

### Batch from Directory

```bash
primerlab batch-run \
  --configs ./project_configs/ \
  --output ./batch_results/ \
  --continue-on-error
```

### Multi-FASTA Mode

```bash
primerlab batch-run \
  --fasta examples/multi_sequences.fasta \
  --config examples/pcr_standard.yaml \
  --output ./batch_results/
```

## Output

- Individual results per sequence
- `batch_summary.xlsx` - Combined Excel summary
- Console summary with success/fail stats
