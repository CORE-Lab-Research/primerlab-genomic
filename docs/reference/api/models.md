---
title: "Models Reference"
description: "Python API reference for Models Reference"
---
Data classes used throughout PrimerLab.

## Module

```python
from primerlab.core.models import (
    Primer,
    PrimerPair,
    Amplicon,
    QCResult
)
from primerlab.core.models.blast import BlastResult, BlastHit
from primerlab.core.insilico import BindingSite, InsilicoPCRResult
```

---

## Primer

Single primer representation.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `sequence` | str | Primer sequence (5'→3') |
| `length` | int | Primer length |
| `tm` | float | Melting temperature (°C) |
| `gc_content` | float | GC percentage |
| `name` | str | Primer name/ID |
| `direction` | str | "forward" or "reverse" |

### Example

```python
from primerlab.core.models import Primer

primer = Primer(
    sequence="ATGGTGAGCAAGGGCGAGGAG",
    name="GFP_F1",
    direction="forward"
)

print(f"Sequence: {primer.sequence}")
print(f"Length: {primer.length} bp")
print(f"Tm: {primer.tm:.1f}°C")
print(f"GC: {primer.gc_content:.1f}%")
```

---

## PrimerPair

Forward + Reverse primer pair.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `forward` | Primer | Forward primer |
| `reverse` | Primer | Reverse primer |
| `amplicon_size` | int | Product size (bp) |
| `tm_diff` | float | Tm difference |
| `score` | float | Overall QC score |
| `probe` | Primer | TaqMan probe (qPCR only) |

### Example

```python
pair = result.primers[0]

print(f"Forward: {pair.forward.sequence}")
print(f"Reverse: {pair.reverse.sequence}")
print(f"Amplicon: {pair.amplicon_size} bp")
print(f"Tm difference: {pair.tm_diff:.1f}°C")
print(f"Score: {pair.score:.1f}")
```

---

## Amplicon

Predicted PCR product.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `sequence` | str | Amplicon sequence |
| `size` | int | Length in bp |
| `start` | int | Start position on template |
| `end` | int | End position on template |
| `gc_content` | float | GC percentage |

### Example

```python
amplicon = insilico_result.products[0]

print(f"Size: {amplicon.size} bp")
print(f"Position: {amplicon.start}-{amplicon.end}")
print(f"Sequence: {amplicon.sequence[:50]}...")
```

---

## BindingSite

Primer binding site analysis result.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `position` | int | Binding position |
| `mismatches` | int | Number of mismatches |
| `mismatch_positions` | List[int] | Positions of mismatches |
| `three_prime_dg` | float | 3' end ΔG (kcal/mol) |
| `estimated_tm` | float | Corrected Tm |
| `is_valid` | bool | Passes binding criteria |
| `validation_notes` | List[str] | Warnings/notes |

### Example

```python
from primerlab.core.insilico import analyze_binding

binding = analyze_binding(primer_seq, target_seq)

print(f"Position: {binding.position}")
print(f"Mismatches: {binding.mismatches}")
print(f"3' ΔG: {binding.three_prime_dg:.2f} kcal/mol")
print(f"Valid: {binding.is_valid}")

if binding.validation_notes:
    for note in binding.validation_notes:
        print(f"  Warning: {note}")
```

---

## BlastResult

Off-target detection result.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `primer_id` | str | Primer identifier |
| `hits` | List[BlastHit] | List of BLAST hits |
| `score` | float | Specificity score (0-100) |
| `grade` | str | Letter grade (A-F) |
| `offtarget_count` | int | Number of off-targets |
| `is_specific` | bool | Passes specificity threshold |

### BlastHit Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `subject_id` | str | Hit sequence ID |
| `identity` | float | Percent identity |
| `alignment_length` | int | Alignment length |
| `mismatches` | int | Number of mismatches |
| `evalue` | float | E-value |

### Example

```python
blast_result = offtarget_check(primer, database)

print(f"Specificity Score: {blast_result.score:.1f}")
print(f"Grade: {blast_result.grade}")
print(f"Off-targets: {blast_result.offtarget_count}")

for hit in blast_result.hits[:5]:
    print(f"  {hit.subject_id}: {hit.identity:.1f}% identity")
```

---

## QCResult

Quality control assessment.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `passed` | bool | Overall QC pass |
| `hairpin_dg` | float | Hairpin ΔG |
| `homodimer_dg` | float | Self-dimer ΔG |
| `heterodimer_dg` | float | Cross-dimer ΔG |
| `gc_clamp` | bool | Has GC clamp |
| `warnings` | List[str] | QC warnings |

### Example

```python
qc = primer_pair.qc_result

print(f"QC Passed: {qc.passed}")
print(f"Hairpin ΔG: {qc.hairpin_dg:.2f} kcal/mol")
print(f"Homodimer ΔG: {qc.homodimer_dg:.2f} kcal/mol")
print(f"GC Clamp: {'Yes' if qc.gc_clamp else 'No'}")

for warning in qc.warnings:
    print(f"  ⚠ {warning}")
```

---

## See Also

- [Public API](public)
- [In-silico API](insilico)
- [Report API](report)
