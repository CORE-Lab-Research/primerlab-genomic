---
title: "CLI Reference"
description: "Command-line interface reference for PrimerLab"
---

Complete command-line reference for PrimerLab Genomic v1.0.1.

## Installation Check

```bash
primerlab --version    # Show version
primerlab health       # Check dependencies
```

---

## Core Commands

### `run` - Design Primers

The main command for designing PCR or qPCR primers.

```bash
primerlab run <workflow> --config <config.yaml> [options]
```

**Workflows:** `pcr`, `qpcr`

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | Path to YAML configuration file |
| `--out` | `-o` | Override output directory |
| `--debug` | | Enable debug logging |
| `--dry-run` | | Validate config without running |
| `--export` | `-e` | Export formats: `idt`, `sigma`, `thermo`, `benchling`, `xlsx` |
| `--mask` | `-m` | Region masking: `auto`, `lowercase`, `n`, `none` |
| `--quiet` | `-q` | Suppress warnings |
| `--validate` | `-V` | Run in-silico PCR validation |
| `--blast` | | Run off-target check |
| `--blast-db` | | Path to BLAST database |
| `--report` | `-R` | Generate enhanced report |
| `--report-format` | | Format: `markdown`, `html`, `json` |

**Examples:**

```bash
# Basic PCR design
primerlab run pcr --config my_pcr.yaml

# qPCR with TaqMan probe
primerlab run qpcr --config my_qpcr.yaml

# PCR with masking and BLAST check
primerlab run pcr -c config.yaml --mask auto --blast --blast-db genome.fasta

# Export to IDT ordering format
primerlab run pcr -c config.yaml --export idt
```

---

### `batch-run` - Batch Processing

Design primers for multiple sequences in one command.

```bash
primerlab batch-run --fasta <sequences.fasta> --config <shared.yaml> [options]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--fasta` | `-f` | Input FASTA with multiple sequences |
| `--config` | `-c` | Shared configuration file |
| `--out` | `-o` | Output directory |
| `--parallel` | `-j` | Number of parallel workers |
| `--continue-on-error` | | Skip failed sequences |

**Example:**

```bash
primerlab batch-run -f genes.fasta -c shared.yaml -o batch_output/ -j 4
```

---

## Analysis Commands

### `insilico` - In-silico PCR

Simulate PCR amplification to validate primer binding.

```bash
primerlab insilico --primers <primers.json> --template <template.fasta> [options]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--primers` | `-p` | Primers file (JSON or FASTA) |
| `--template` | `-t` | Template sequence (FASTA) |
| `--output` | `-o` | Output directory |
| `--circular` | | Treat template as circular |
| `--json` | | Output JSON only |

**Primer formats:**

```json
{"forward": "ATGGTGAGCAAGGGCGAGGAG", "reverse": "TTACTTGTACAGCTCGTCCATGCC"}
```

**What it checks:**

- Primer binding sites with mismatch tolerance
- 3' end stability (minimum 3bp perfect match)
- Product size and orientation
- Multiple products (non-specific amplification)

---

### `blast` - Off-target Detection

Check primer specificity against a genome database.

```bash
primerlab blast --primers <primers> --database <genome.fasta> [options]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--primers` | `-p` | Primers (JSON, FASTA, or comma-separated) |
| `--database` | `-d` | FASTA or BLAST database |
| `--target` | `-t` | Expected target sequence ID |
| `--mode` | | `auto`, `blast`, or `biopython` |
| `--json` | | Output JSON only |

**Specificity Grades:**

| Grade | Score | Interpretation |
|-------|-------|----------------|
| A | 90-100 | Excellent |
| B | 80-89 | Good |
| C | 70-79 | Acceptable |
| D | 60-69 | Low |
| F | <60 | Poor |

---

### `check-compat` - Primer Compatibility

Analyze primer pairs for dimers and cross-reactivity.

```bash
primerlab check-compat --primers <primers.json> [options]
```

Checks for:

- Self-dimers
- Hetero-dimers (cross-dimers)
- Hairpin structures
- 3' complementarity

---

### `species-check` - Species Specificity

Verify primers are specific to target species.

```bash
primerlab species-check --primers <primers.json> --target-db <target.fasta> --background-db <background.fasta>
```

---

### `tm-gradient` - Temperature Gradient

Simulate PCR across annealing temperature range.

```bash
primerlab tm-gradient --primers <primers.json> --range 55-65 --step 1
```

---

### `probe-check` - TaqMan Probe Analysis

Validate TaqMan probe binding and thermodynamics.

```bash
primerlab probe-check --probe <probe.json> --template <template.fasta>
```

---

### `melt-curve` - Melt Curve Prediction

Predict SYBR Green melt curve for amplicon.

```bash
primerlab melt-curve --amplicon <amplicon.fasta> --output melt.svg
```

---

### `amplicon-qc` - Amplicon Quality Check

Validate amplicon characteristics.

```bash
primerlab amplicon-qc --amplicon <amplicon.fasta>
```

Checks: GC content, secondary structures, length constraints.

---

## Utility Commands

### `stats` - Sequence Statistics

Analyze sequence before design.

```bash
primerlab stats <input.fasta>
```

Output: length, GC%, repeat regions, complexity.

---

### `compare` - Compare Designs

Compare two primer design results.

```bash
primerlab compare <result1.json> <result2.json>
```

---

### `history` - Design History

View and manage design history (SQLite database).

```bash
primerlab history list              # List all designs
primerlab history show <id>         # Show specific design
primerlab history export <id> -o .  # Export design
primerlab history clear             # Clear history
```

---

### `plot` - Visualization

Generate GC profile and other plots.

```bash
primerlab plot gc <input.fasta> --output gc_plot.png
```

---

### `validate` - Config Validation

Validate configuration file syntax.

```bash
primerlab validate <config.yaml>
```

---

### `init` - Initialize Config

Generate template configuration file.

```bash
primerlab init pcr -o my_config.yaml     # PCR template
primerlab init qpcr -o my_config.yaml    # qPCR template
```

---

### `preset` - Manage Presets

Save and load configuration presets.

```bash
primerlab preset list                    # List available presets
primerlab preset save <name> -c config.yaml
primerlab preset apply <name> -o new_config.yaml
```

---

### `health` - Health Check

Verify all dependencies are installed.

```bash
primerlab health
```

Checks: Primer3, BLAST+ (optional), ViennaRNA (optional).

---

## Global Options

These options work with all commands:

| Option | Description |
|--------|-------------|
| `--help` | Show help message |
| `--version` | Show version |
| `--debug` | Enable debug logging |
| `--quiet` | Suppress non-essential output |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | Dependency missing |
| 4 | Input file error |
