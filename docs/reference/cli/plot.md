---
title: "primerlab plot"
description: "CLI reference for the primerlab plot command"
---
Generate visualizations from primer design results.

## Synopsis

```bash
primerlab plot <result> [options]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `result` | Yes | Path to result.json file |

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--sequence` | `-s` | Path to sequence file (required) |
| `--type` | `-t` | Plot type (default: gc-profile) |
| `--theme` | | Color theme: light, dark |
| `--output` | `-o` | Output path (PNG/SVG) |
| `--window` | `-w` | Sliding window size (default: 20) |

## Plot Types

| Type | Description |
|------|-------------|
| `gc-profile` | GC content across amplicon |

## Examples

### Basic GC Profile

```bash
primerlab plot result.json --sequence input.fasta
```

### Dark Theme

```bash
primerlab plot result.json --sequence input.fasta --theme dark
```

### Custom Window Size

```bash
primerlab plot result.json --sequence input.fasta --window 50
```

### Save to File

```bash
primerlab plot result.json --sequence input.fasta --output gc_profile.png
```

## Output

- Interactive plot displayed (if no --output)
- PNG/SVG file saved (if --output specified)
- Primer positions highlighted on plot
