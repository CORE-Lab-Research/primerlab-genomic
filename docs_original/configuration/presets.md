# Presets

Pre-configured parameter sets for common PCR applications.

## Available Presets

| Preset | Use Case | Product Size | Tm Range |
|--------|----------|--------------|----------|
| `long_range` | Long amplicons (3-10kb) | 3000-10000 bp | 62-68°C |
| `dna_barcoding` | Species ID (COI, ITS) | 400-700 bp | 50-60°C |
| `rt_pcr` | Gene expression | 80-200 bp | 58-62°C |

## Usage

```yaml
workflow: pcr

# Use a preset for optimized defaults
preset: long_range

input:
  sequence_path: "my_gene.fasta"

output:
  directory: "output/"
```

---

## long_range

For amplifying long DNA fragments (3-10+ kb).

| Parameter | Value |
|-----------|-------|
| Primer size | 25-35 bp (opt: 28) |
| Product size | 3000-10000 bp |
| Tm | 62-68°C (opt: 65) |
| QC mode | strict |

**Notes:**

- Requires specialized polymerases (LA Taq, LongAmp)
- Extension time: 1 min per kb
- Use hot-start to prevent mispriming

---

## dna_barcoding

For DNA barcoding applications (COI, rbcL, ITS).

| Parameter | Value |
|-----------|-------|
| Primer size | 20-28 bp (opt: 23) |
| Product size | 400-700 bp |
| Tm | 50-60°C (opt: 55) |
| GC | 35-70% (broader for diverse taxa) |
| QC mode | relaxed |

**Notes:**

- More permissive for diverse templates
- Slightly lower Tm for degenerate primers

---

## rt_pcr

For Reverse Transcription PCR (gene expression).

| Parameter | Value |
|-----------|-------|
| Primer size | 18-24 bp (opt: 20) |
| Product size | 80-200 bp |
| Tm | 58-62°C (opt: 60) |
| QC mode | standard |

**Notes:**

- Short amplicons for efficient cDNA amplification
- Tighter Tm match (±2°C)
- Consider exon-spanning primers

---

## Custom Override

Presets can be combined with custom parameters:

```yaml
workflow: pcr
preset: long_range

parameters:
  # Override specific values
  tm:
    opt: 66.0  # Override preset Tm

output:
  directory: "custom_output/"
```

---

## See Also

- [PCR Configuration](pcr.md)
- [qPCR Configuration](qpcr.md)
