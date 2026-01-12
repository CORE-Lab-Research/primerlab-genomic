# Nested PCR Design Tutorial

Nested PCR is a two-step amplification technique that increases specificity. PrimerLab supports both **Nested PCR** and **Semi-Nested PCR** design.

## Concept

```
Outer PCR:
5'────[OUTER_FWD]═══════════════════════════[OUTER_REV]────3'

Inner PCR (Nested):
          5'────[INNER_FWD]═══════════[INNER_REV]────3'

Semi-Nested:
          5'────[INNER_FWD]═══════════════════[OUTER_REV]────3'
```

---

## CLI Usage

### Nested PCR Design

```bash
primerlab nested-design --sequence input.fasta --format json
```

**Options:**

| Option | Description |
|--------|-------------|
| `--sequence` | Input FASTA file |
| `--outer-size` | Outer product size (default: 400-800 bp) |
| `--inner-size` | Inner product size (default: 150-300 bp) |
| `--format` | Output format (json/text/csv) |

### Semi-Nested PCR Design

```bash
primerlab seminested-design --sequence input.fasta --format json
```

---

## Python API

```python
from primerlab.core.variants import NestedPCRDesigner

designer = NestedPCRDesigner()
result = designer.design(
    sequence="ATCGATCG...",
    outer_product_range=(400, 800),
    inner_product_range=(150, 300)
)

print(result.outer_primers)
print(result.inner_primers)
```

---

## Example Output

```json
{
  "outer_primers": {
    "forward": "ATCGATCGATCGATCGATCG",
    "reverse": "GCTAGCTAGCTAGCTAGCTA"
  },
  "inner_primers": {
    "forward": "TGCATGCATGCATGCATGCA",
    "reverse": "CGATCGATCGATCGATCGAT"
  },
  "outer_product_size": 650,
  "inner_product_size": 220
}
```

---

## Best Practices

1. **Outer primers** should flank the region of interest
2. **Inner primers** should bind within the outer amplicon
3. Maintain **3-5°C Tm difference** between outer and inner
4. Avoid **overlapping primer binding sites**

---

## See Also

- [PCR Workflow](pcr-walkthrough.md)
- [CLI Reference: nested-design](../cli/README.md)
