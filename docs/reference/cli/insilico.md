---
title: "primerlab insilico"
description: "CLI reference for the primerlab insilico command"
---
**v0.2.4** - In-silico PCR Simulation

Validate primers against a template sequence by simulating PCR amplification.

## Usage

```bash
primerlab insilico -p <primers> -t <template> [options]
```

## Arguments

| Argument | Short | Required | Description |
|----------|-------|----------|-------------|
| `--primers` | `-p` | ✅ | Path to primers file (JSON or FASTA) |
| `--template` | `-t` | ✅ | Path to template FASTA file |
| `--output` | `-o` | ❌ | Output directory (default: `insilico_output`) |
| `--config` | `-c` | ❌ | Optional config file for parameters |
| `--json` | | ❌ | Output results as JSON only |
| `--circular` | | ❌ | Treat template as circular (v0.2.4) |

## Primer File Formats

### JSON Format

```json
{
  "forward": "ATGGTGAGCAAGGGCGAGGAG",
  "reverse": "TTACTTGTACAGCTCGTCCATGCC"
}
```

### FASTA Format

```fasta
>Forward_primer
ATGGTGAGCAAGGGCGAGGAG
>Reverse_primer
TTACTTGTACAGCTCGTCCATGCC
```

## Examples

### Basic Usage

```bash
primerlab insilico -p primers.json -t template.fasta
```

### With Custom Output Directory

```bash
primerlab insilico -p primers.json -t template.fasta -o results/
```

### JSON Output for Pipelines

```bash
primerlab insilico -p primers.json -t template.fasta --json > result.json
```

### Using Example Files

```bash
primerlab insilico \
  -p examples/insilico/primers.json \
  -t examples/insilico/template.fasta
```

## Output Files

| File | Description |
|------|-------------|
| `insilico_result.json` | Complete results with binding data |
| `insilico_report.md` | Human-readable markdown report (v0.2.2) |
| `predicted_amplicons.fasta` | Predicted amplicon sequences |

## Console Output

```
============================================================
🧬 In-silico PCR Results
============================================================
Template: GFP_coding_sequence (720 bp)
Forward:  5'-ATGGTGAGCAAGGGCGAGGAG-3' (21 bp)
Reverse:  5'-TTACTTGTACAGCTCGTCCATGCC-3' (24 bp)
------------------------------------------------------------

✅ 1 product(s) predicted

🎯 PRIMARY: 720 bp
   Position: 0 → 720
   Likelihood: 100.0%

   Amplicon: ATGGTGAGCAAGGGCGAGGAG...GGCATGGACGAGCTGTACAAGTAA

------------------------------------------------------------
📁 Output directory: insilico_output
   • insilico_result.json
   • predicted_amplicons.fasta (1 sequences)
```

## What It Checks

- **Primer Binding Sites** - Finds all positions where primers can bind
- **3' End Match** - Verifies 3' stability (minimum 3bp perfect match)
- **5' Mismatch Tolerance** - Allows up to 2 mismatches at 5' end
- **Product Size** - Validates amplicon is within expected range
- **Multiple Products** - Detects potential non-specific amplification
- **Orientation** - Ensures primers face each other correctly

## Related Commands

- [`primerlab run`](run) - Design primers
- [`primerlab stats`](stats) - Sequence statistics
- [`primerlab validate`](validate) - Validate config files
