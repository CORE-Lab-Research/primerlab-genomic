# Nested & Semi-Nested PCR

Learn how to design primers for Nested and Semi-Nested PCR to increase specificity and sensitivity.

## Overview

Nested PCR involves two rounds of amplification:

1. **Outer Round**: Amplifies a larger region using "Outer Primers".
2. **Inner Round**: Amplifies a smaller target within the first product using "Inner Primers".

This technique is useful for:

- Low-abundance templates
- High-background noise (non-specific amplification)
- Long-range amplification

---

## Nested PCR

Design distinct primer pairs for both rounds.

### Configuration

Add a `nested` section to your configuration:

```yaml
# nested_config.yaml
input:
  sequence_path: ./target.fasta

parameters:
  # Outer parameters (Round 1)
  tm:
    opt: 58.0
  product_size:
    min: 400
    max: 600

nested:
  enabled: true
  # Inner parameters (Round 2)
  inner_product_size:
    min: 150
    max: 250
  inner_tm_opt: 60.0  # Optional: higher Tm for inner primers
```

### Running the Design

```bash
primerlab run pcr --config nested_config.yaml --nested
```

### Output Example

The output will clearly separate outer and inner primers:

```text
Outer Primers (First Round)
  Forward: ATGCGATCGATCGATCG (Tm: 58.2°C)
  Reverse: GCTAGCTAGCTAGCTAG (Tm: 58.0°C)
  Product: 520 bp

Inner Primers (Second Round)
  Forward: TCGATCGATCGATCGAT (Tm: 60.1°C)
  Reverse: AGCTAGCTAGCTAGCTA (Tm: 60.3°C)
  Product: 185 bp
```

---

## Semi-Nested PCR

Semi-nested PCR uses one of the outer primers (usually Forward) also as an inner primer, combined with a new inner primer. This saves reagent costs while still improving specificity.

### Configuration

Set `mode` to `semi`:

```yaml
nested:
  enabled: true
  mode: semi  # Options: 'full' (default), 'semi'
  shared_primer: forward # Options: 'forward' (default), 'reverse'
```

### Running the Design

```bash
primerlab run pcr --config semi_nested.yaml --nested
```

---

## Best Practices

1. **Tm Differences**: Some protocols recommend designing inner primers with a slightly lower Tm than outer primers to prevent outer primer binding in the second round, although standard equal Tm often works well.
2. **Product Size**: Ensure the inner product is significantly smaller than the outer product to easily distinguish them on a gel if carryover occurs.
3. **Contamination**: Nested PCR is very sensitive. Use separate areas for setting up Round 1 and Round 2 reactions.
