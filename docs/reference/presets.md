# Presets Reference

PrimerLab includes optimized presets for common PCR applications. Presets provide pre-configured parameters that you can use as-is or customize.

## Viewing Presets

```bash
# List all available presets
primerlab preset list

# Show details of a specific preset
primerlab preset show long_range
```

---

## Available Presets

### Standard Presets

| Preset | Amplicon Size | Tm Range | QC Mode | Best For |
|--------|:-------------:|:--------:|:-------:|----------|
| `standard_pcr` | 100-1000 bp | 57-63°C | standard | General research |
| `diagnostic_pcr` | 80-200 bp | 58-62°C | strict | Clinical testing |
| `long_range` | 3000-10000 bp | 62-68°C | strict | Large gene fragments |
| `cloning_pcr` | 200-3000 bp | 58-68°C | standard | Molecular cloning |
| `sequencing_pcr` | 300-800 bp | 58-62°C | standard | Sanger sequencing |
| `dna_barcoding` | 400-700 bp | 50-60°C | relaxed | Species identification |
| `rt_pcr` | 80-150 bp | 58-62°C | strict | Reverse transcription |

---

## Preset Details

### `diagnostic_pcr`

High-specificity primers for clinical/diagnostic applications.

**Use Cases**: Pathogen detection, genetic testing, point-of-care

| Parameter | Value |
|-----------|-------|
| Primer Size | 20-28 bp (opt: 22) |
| Tm | 58-62°C (opt: 60°C) |
| GC% | 45-55% |
| Product Size | 80-200 bp |
| QC Mode | strict |

```yaml
preset: diagnostic_pcr
```

---

### `long_range`

Optimized for amplifying long DNA fragments (3-10+ kb).

**Use Cases**: Full-length gene amplification, large deletions, genomic regions

| Parameter | Value |
|-----------|-------|
| Primer Size | 25-35 bp (opt: 28) |
| Tm | 62-68°C (opt: 65°C) |
| GC% | 40-60% |
| Product Size | 3000-10000 bp |
| QC Mode | strict |

> **Note**: Requires specialized polymerases (e.g., LA Taq, LongAmp).

```yaml
preset: long_range
```

---

### `cloning_pcr`

Primers designed for molecular cloning with restriction sites.

**Use Cases**: Gene cloning, subcloning, expression vector construction, Gibson assembly

| Parameter | Value |
|-----------|-------|
| Primer Size | 25-40 bp (opt: 30) |
| Tm | 58-68°C (opt: 62°C) |
| GC% | 40-60% |
| Product Size | 200-3000 bp |
| QC Mode | standard |

```yaml
preset: cloning_pcr
```

---

### `dna_barcoding`

DNA barcoding applications (COI, rbcL, ITS, etc.).

**Use Cases**: Species identification, biodiversity surveys, phylogenetics

| Parameter | Value |
|-----------|-------|
| Primer Size | 20-28 bp (opt: 23) |
| Tm | 50-60°C (opt: 55°C) |
| GC% | 35-70% |
| Product Size | 400-700 bp |
| QC Mode | relaxed |

> **Note**: Relaxed mode allows for diverse templates across taxa.

```yaml
preset: dna_barcoding
```

---

### `rt_pcr`

Reverse transcription PCR for cDNA amplification.

**Use Cases**: Gene expression analysis, mRNA detection

| Parameter | Value |
|-----------|-------|
| Primer Size | 18-25 bp |
| Tm | 58-62°C |
| Product Size | 80-150 bp |
| QC Mode | strict |

```yaml
preset: rt_pcr
```

---

## Using Presets

### In Configuration File

```yaml
preset: diagnostic_pcr

input:
  sequence_path: ./my_gene.fasta

# Override specific parameters if needed
parameters:
  tm:
    opt: 62.0  # Override default 60°C
```

### Via CLI

```bash
# Use preset directly
primerlab run pcr --preset diagnostic_pcr --sequence gene.fasta
```

---

## Customizing Presets

Presets provide defaults, but you can override any parameter:

```yaml
preset: long_range

# Your overrides take precedence
parameters:
  product_size_range: [[5000, 15000]]  # Extend range
  tm:
    opt: 68.0  # Higher Tm for very long amplicons

qc:
  mode: relaxed  # Override strict to relaxed
```

---

## See Also

- [Configuration Reference](config.md)
- [Customization Guide](../guides/customization.md)
- [CLI Reference](cli.md)
