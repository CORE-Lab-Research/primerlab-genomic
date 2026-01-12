# Species Specificity Check Tutorial

This tutorial walks you through using PrimerLab's species specificity check to validate primer cross-reactivity.

## Overview

When designing primers for molecular diagnostics or research, ensuring species specificity is critical. Primers that bind to multiple species can cause false positives or contamination issues.

## Prerequisites

- PrimerLab v0.4.2 or later
- Primer sequences (JSON format)
- Target species FASTA template
- (Optional) Off-target species FASTA files

## Step 1: Prepare Your Primers

Create a JSON file with your primer pairs:

```json
[
  {
    "name": "Gene1",
    "forward": "ATGCGATCGATCGATCGATCG",
    "reverse": "CGATCGATCGATCGATCGCAT"
  },
  {
    "name": "Gene2",
    "forward": "GATCGATCGATCGATCGATCG",
    "reverse": "CGATCGATCGATCGATCGATC"
  }
]
```

Save as `primers.json`.

## Step 2: Prepare Templates

### Target Species (Required)

Create a FASTA file with your target species template:

```
>Human_Target
ATGCGATCGATCGATCGATCG...
```

### Off-target Species (Optional)

Create FASTA file(s) with species you want to check against:

```
>Mouse_Homolog
ATGCGGTCGATCGATCGATCG...
>Rat_Homolog
ATGCGCTCGATCGATCGATCG...
```

## Step 3: Run Species Check

### Basic Check

```bash
primerlab species-check \
  --primers primers.json \
  --target human.fasta \
  --output ./results
```

### With Off-targets

```bash
primerlab species-check \
  --primers primers.json \
  --target human.fasta \
  --offtargets mouse.fasta,rat.fasta \
  --output ./results
```

## Step 4: Interpret Results

### Console Output

```
🧬 Species Specificity Check (v0.4.2)
==================================================
📂 Loading primers: primers.json
🎯 Loading target: human.fasta
🔬 Loaded off-target: Mouse_Homolog
🔬 Loaded off-target: Rat_Homolog

⏳ Analyzing species specificity...

==================================================
🏁 Specificity Score: 92.0/100 (Grade A)
   Status: ✅ SPECIFIC
   Primers: 2 | Species: 3
```

### Score Interpretation

| Grade | Score | Meaning |
|-------|-------|---------|
| A | 90-100 | Excellent - highly species-specific |
| B | 80-89 | Good - minor cross-reactivity possible |
| C | 70-79 | Acceptable - some cross-reactivity |
| D | 60-69 | Poor - significant cross-reactivity |
| F | <60 | Fail - primers bind to multiple species |

### Output Files

| File | Description |
|------|-------------|
| `species_analysis.json` | Complete analysis data |
| `species_report.md` | Human-readable summary |
| `species_analysis.xlsx` | Excel matrix (if `--format excel`) |

## Step 5: Using the API

```python
from primerlab.api.public import check_species_specificity_api

result = check_species_specificity_api(
    primers=[{"name": "P1", "forward": "ATGC...", "reverse": "GCAT..."}],
    target_template="ATGCGATCG...",
    target_name="Human",
    offtarget_templates={"Mouse": "ATGCGGTC..."}
)

if result['is_specific']:
    print("✅ Primers are species-specific!")
else:
    print("⚠️ Cross-reactivity detected")
    for warning in result['warnings']:
        print(f"  - {warning}")
```

## Best Practices

1. **Include close relatives**: Check against phylogenetically close species
2. **Use complete genes**: Longer templates catch more binding sites
3. **Review warnings**: Even "specific" primers may have weak cross-binding
4. **Consider Grade B acceptable**: Perfect specificity (A) isn't always required

## Troubleshooting

### No binding detected to target

- Check primer orientation (forward vs reverse)
- Verify sequence quality (no ambiguous bases)
- Lower `min_match_percent` in config

### Too many off-target warnings

- Redesign primers to avoid conserved regions
- Target species-specific SNP sites
- Lengthen primers for more specificity

## Next Steps

- [Species Specificity Documentation](../../features/species-specificity.md)
- [Example Files](../../examples/species_check/)
