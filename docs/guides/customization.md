# Customization Guide

Learn how to customize PrimerLab parameters for your specific research needs.

## Overview

PrimerLab's design can be customized at three levels:

1. **Presets** — Pre-configured parameter sets
2. **Config Files** — YAML-based configuration
3. **CLI Overrides** — Command-line parameter adjustments

---

## Customizable Parameters

### Primer Properties

| Parameter | Config Path | Range | Description |
|-----------|-------------|:-----:|-------------|
| **Length** | `parameters.primer_size` | 15-40 bp | Primer length in base pairs |
| **Tm** | `parameters.tm` | 45-75°C | Melting temperature |
| **GC Content** | `parameters.gc` | 20-80% | Guanine-Cytosine percentage |

```yaml
parameters:
  primer_size:
    min: 18
    opt: 22
    max: 28
  tm:
    min: 58.0
    opt: 60.0
    max: 62.0
  gc:
    min: 40.0
    max: 60.0
```

### Amplicon Properties

| Parameter | Config Path | Typical Values |
|-----------|-------------|----------------|
| **Product Size** | `parameters.product_size_range` | `[[100, 300]]` |
| **Max Poly-X** | `parameters.max_poly_x` | 3-5 |
| **Max Self-Comp** | `parameters.max_self_complementarity` | 4-8 |

```yaml
parameters:
  product_size_range: [[150, 250]]
  max_poly_x: 4
  max_self_complementarity: 6
```

### QC Thresholds

| Parameter | Config Path | Recommended |
|-----------|-------------|:-----------:|
| **Hairpin ΔG** | `qc.hairpin_dg_min` | -2 to -4 kcal/mol |
| **Dimer ΔG** | `qc.dimer_dg_min` | -5 to -8 kcal/mol |
| **Tm Difference** | `qc.tm_diff_max` | 2-5°C |

```yaml
qc:
  mode: standard  # strict, standard, relaxed
  hairpin_dg_min: -3.0
  dimer_dg_min: -6.0
  tm_diff_max: 3.0
```

---

## Overriding Presets

Start with a preset and override specific values:

```yaml
preset: diagnostic_pcr

# Your overrides
parameters:
  tm:
    opt: 62.0  # Higher than default 60°C
  product_size_range: [[100, 300]]  # Larger than default 80-200

qc:
  mode: standard  # Relax from default strict
```

---

## Application-Specific Recommendations

### 🧬 Clinical Diagnostics

```yaml
preset: diagnostic_pcr

parameters:
  primer_size:
    opt: 22
  tm:
    min: 58.0
    opt: 60.0
    max: 62.0
  product_size_range: [[80, 150]]

qc:
  mode: strict
```

**Key Points**:

- Short amplicons (80-150 bp) for rapid cycling
- Strict QC to avoid false positives
- Tight Tm range for reproducibility

---

### 🔬 Gene Cloning

```yaml
preset: cloning_pcr

parameters:
  primer_size:
    min: 28
    opt: 32
    max: 40
  tm:
    opt: 64.0
  product_size_range: [[500, 2500]]

cloning:
  add_restriction_overhang: true
  common_sites:
    - EcoRI
    - BamHI
```

**Key Points**:

- Longer primers to accommodate restriction sites
- Higher Tm for added 5' tails
- Configure restriction sites in `cloning` section

---

### 🌿 Environmental DNA (eDNA)

```yaml
preset: dna_barcoding

parameters:
  tm:
    min: 48.0
    opt: 52.0
    max: 56.0
  gc:
    min: 30.0
    max: 70.0

qc:
  mode: relaxed
```

**Key Points**:

- Lower Tm for degraded templates
- Wide GC range for diverse taxa
- Relaxed QC for challenging samples

---

### 📊 qPCR / TaqMan

```yaml
workflow: qpcr
mode: taqman

parameters:
  tm:
    opt: 60.0
  product_size_range: [[70, 150]]

probe:
  tm:
    min: 68.0
    opt: 70.0
    max: 72.0
  exclude_5_g: true
```

**Key Points**:

- Probe Tm should be ~10°C higher than primers
- Avoid G at 5' end of probe (quenches fluorophore)
- Small amplicons for efficient amplification

---

## Creating Custom Config Files

### Step 1: Start from Template

```bash
# Generate a template config
primerlab init --workflow pcr --output my_config.yaml
```

### Step 2: Edit Parameters

Open `my_config.yaml` and modify as needed.

### Step 3: Validate

```bash
primerlab validate my_config.yaml
```

### Step 4: Run

```bash
primerlab run pcr --config my_config.yaml
```

---

## CLI Quick Overrides

Override without editing config:

```bash
# Override Tm
primerlab run pcr --config base.yaml --tm-opt 62

# Override product size
primerlab run pcr --config base.yaml --product-min 100 --product-max 250

# Override QC mode
primerlab run pcr --config base.yaml --qc-mode relaxed
```

---

## See Also

- [Presets Reference](../reference/presets.md)
- [Configuration Reference](../reference/config.md)
- [Understanding Results](../concepts/understanding-results.md)
