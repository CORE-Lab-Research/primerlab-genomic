# CLI Reference

PrimerLab provides a comprehensive command-line interface for primer design workflows.

## Commands Overview

| Command | Description |
|---------|-------------|
| [`run`](run.md) | Run PCR/qPCR primer design workflow |
| [`insilico`](insilico.md) | In-silico PCR simulation **(v0.2.0)** |
| [`blast`](blast.md) | Off-target detection **(v0.3.0)** |
| [`check-compat`](compat_check.md) | Primer compatibility check **(v0.4.0)** |
| [`species-check`](species-check.md) | Species specificity check **(v0.4.2)** |
| [`tm-gradient`](tm-gradient.md) | Temperature gradient simulation **(v0.4.3)** |
| [`stats`](stats.md) | Analyze sequence before design |
| [`batch-run`](batch-run.md) | Run multiple designs in batch |
| [`compare`](compare.md) | Compare two primer designs |
| [`history`](history.md) | View and manage design history |
| [`plot`](plot.md) | Generate visualizations |
| [`validate`](validate.md) | Validate configuration file |
| [`init`](init.md) | Generate template config |
| [`preset`](preset.md) | Manage design presets |
| [`health`](health.md) | Check dependencies |

## Global Options

```bash
primerlab --version    # Show version
primerlab --help       # Show help
```

## Quick Examples

```bash
# Design PCR primers
primerlab run pcr --config my_config.yaml

# Check sequence stats
primerlab stats input.fasta

# Batch processing
primerlab batch-run --fasta genes.fasta --config shared.yaml

# Compare designs
primerlab compare result1.json result2.json
```
