---
title: "Sequence Handling"
description: "Feature documentation: Sequence Handling"
---
PrimerLab v0.1.6 introduces enhanced sequence handling for real-world genomic data.

## IUPAC Ambiguous Codes

IUPAC ambiguous nucleotide codes are automatically detected and handled:

| Code | Meaning | Bases |
|------|---------|-------|
| R | puRine | A or G |
| Y | pYrimidine | C or T |
| W | Weak | A or T |
| S | Strong | G or C |
| K | Keto | G or T |
| M | aMino | A or C |
| B | not A | C, G, or T |
| D | not C | A, G, or T |
| H | not G | A, C, or T |
| V | not T | A, C, or G |

### Behavior

When IUPAC codes are detected:

1. **Warning displayed** to user
2. **Codes converted to N** (masked)
3. **Regions excluded** from primer placement

```bash
$ primerlab stats sequence_with_iupac.fasta

📊 Sequence Statistics: TEST_IUPAC
=============================================
  Length:      500 bp
  GC Content:  48.20%
  ⚠️  IUPAC codes: ['R', 'Y'] (6 bp)
      → Will be converted to N during design
=============================================
```

## RNA Sequences

RNA sequences (containing Uracil) are automatically detected and converted:

| Detected | Converted To |
|----------|--------------|
| U (Uracil) | T (Thymine) |
| u (lowercase) | t (then uppercase) |

### Behavior

When RNA is detected:

1. **Warning displayed** to user
2. **U → T conversion** applied
3. **Design proceeds** with DNA sequence

```bash
$ primerlab stats rna_sequence.fasta

📊 Sequence Statistics: TEST_RNA
=============================================
  Length:      300 bp
  ⚠️  RNA detected (contains U)
      → Will be converted to T during design
=============================================
```

## Sequence Validation

PrimerLab validates sequences before design:

| Check | Requirement | Error Code |
|-------|-------------|------------|
| Length | ≥ 50 bp | ERR_SEQ_TOO_SHORT |
| Characters | A, T, G, C, N only | ERR_SEQ_INVALID_CHAR |
| Non-empty | Sequence provided | ERR_SEQ_EMPTY |

## Use `primerlab stats`

Always check your sequence before design:

```bash
primerlab stats input.fasta
```
