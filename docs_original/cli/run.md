# primerlab run

Run a primer design workflow.

## Synopsis

```bash
primerlab run <workflow> [options]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `workflow` | Yes | Workflow type: `pcr`, `qpcr`, or `crispr` |

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | Path to configuration YAML file |
| `--out` | `-o` | Override output directory |
| `--debug` | | Enable debug logging |
| `--dry-run` | | Validate config without running |
| `--export` | `-e` | Export formats (comma-separated) |
| `--mask` | `-m` | Region masking mode |
| `--quiet` | `-q` | Suppress warnings (v0.1.6) |
| `--validate` | `-V` | Run in-silico PCR validation (v0.2.3) |
| `--blast` | | Run off-target check (v0.3.1) |
| `--blast-db` | | Path to BLAST database |
| `--report` | `-R` | Generate enhanced report (v0.3.3) |
| `--report-format` | | Report format: markdown, html, json |
| `--report-output` | | Report output path |

## Examples

### Basic PCR Design

```bash
primerlab run pcr --config my_pcr.yaml
```

### qPCR with TaqMan Probe

```bash
primerlab run qpcr --config my_qpcr.yaml
```

### With Masking

```bash
# Auto-detect lowercase and N-masked regions
primerlab run pcr --config my_pcr.yaml --mask auto
```

### Export to Multiple Formats

```bash
primerlab run pcr --config my_pcr.yaml --export idt,benchling
```

### Quiet Mode (v0.1.6)

```bash
# Suppress warnings for scripted pipelines
primerlab run pcr --config my_pcr.yaml --quiet
```

### Dry Run

```bash
# Validate config without running
primerlab run pcr --config my_pcr.yaml --dry-run
```

### With In-silico Validation (v0.2.3)

```bash
# Design + validate primers against template
primerlab run pcr --config my_pcr.yaml --validate
```

### With BLAST Off-target Check (v0.3.1)

```bash
# Design + check off-targets
primerlab run pcr --config my_pcr.yaml --blast --blast-db genome.fasta
```

### With Report Generation (v0.3.3)

```bash
# Generate enhanced HTML report
primerlab run pcr --config my_pcr.yaml --report --report-format html --report-output report.html
```

## Mask Modes

| Mode | Description |
|------|-------------|
| `auto` | Detect both lowercase and N-masked regions |
| `lowercase` | Only detect lowercase (RepeatMasker) regions |
| `n` | Only detect N-masked regions |
| `none` | No masking (default) |

## Export Formats

| Format | Description |
|--------|-------------|
| `idt` | IDT ordering format |
| `sigma` | Sigma-Aldrich format |
| `thermo` | Thermo Fisher format |
| `benchling` | Benchling CSV import |
| `xlsx` | Excel spreadsheet |
