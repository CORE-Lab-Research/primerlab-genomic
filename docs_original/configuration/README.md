# Configuration Reference

PrimerLab uses YAML configuration files to define primer design parameters.

## Sections

- [PCR Configuration](pcr.md)
- [qPCR Configuration](qpcr.md)
- [Presets](presets.md)

## Config Structure

```yaml
workflow: pcr  # or qpcr

input:
  sequence: "ATGC..."  # Inline sequence
  # OR
  sequence_path: "input.fasta"  # File path

parameters:
  primer_size: {min: 18, opt: 20, max: 24}
  tm: {min: 58.0, opt: 60.0, max: 62.0}
  # ... more parameters

output:
  directory: "output_dir"

qc:
  mode: standard  # or strict, relaxed

# Optional: Off-target check (v0.3.0+)
offtarget:
  enabled: true
  database: "/path/to/genome.fasta"
  mode: auto  # auto, blast, biopython

# Optional: Report generation (v0.3.3+)
report:
  format: html  # markdown, html, json
  output: "report.html"
```

## Generate Template

```bash
primerlab init --workflow pcr --output my_config.yaml
```

## Validate Config

```bash
primerlab validate my_config.yaml
```
