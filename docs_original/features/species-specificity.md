# Species Specificity Check

Analyze primer specificity across multiple species to detect cross-reactivity.

## Overview

The species specificity module helps ensure your primers target only the intended species and don't cross-react with related organisms.

**Key Features:**

- Multi-species FASTA loading
- Primer binding site detection across species
- Cross-reactivity scoring (0-100 scale)
- Specificity matrix visualization
- Off-target species warnings

## CLI Usage

### Basic Usage

```bash
primerlab species-check \
  --primers primers.json \
  --target target_species.fasta \
  --output ./species_output
```

### With Off-target Species

```bash
primerlab species-check \
  --primers primers.json \
  --target human.fasta \
  --offtargets mouse.fasta,rat.fasta,chimp.fasta \
  --output ./species_output
```

### Excel Report

```bash
primerlab species-check \
  --primers primers.json \
  --target target.fasta \
  --offtargets offtarget1.fasta,offtarget2.fasta \
  --format excel \
  --output ./species_output
```

## API Usage

```python
from primerlab.api.public import check_species_specificity_api

# Define primers
primers = [
    {"name": "Gene1", "forward": "ATGC...", "reverse": "GCTA..."},
    {"name": "Gene2", "forward": "TACG...", "reverse": "CGTA..."},
]

# Define templates
target_seq = "ATGCGATC..." # Target species sequence
offtarget_seqs = {
    "Mouse": "ATGCGGTC...",
    "Rat": "ATGCGCTC...",
}

# Run check
result = check_species_specificity_api(
    primers=primers,
    target_template=target_seq,
    target_name="Human",
    offtarget_templates=offtarget_seqs
)

print(f"Score: {result['overall_score']}/100 ({result['grade']})")
print(f"Specific: {result['is_specific']}")
```

## Configuration

Default config: `config/species_check_default.yaml`

```yaml
species_check:
  min_match_percent: 70.0   # Min match % to consider binding
  max_mismatches: 5         # Max mismatches allowed
  offtarget_threshold: 80.0 # % binding to flag as problematic
```

## Output Files

| File | Description |
|------|-------------|
| `species_analysis.json` | Full analysis data |
| `species_report.md` | Human-readable report |
| `species_analysis.xlsx` | Excel with matrix |

## Scoring

| Grade | Score | Interpretation |
|-------|-------|----------------|
| A | 90-100 | Excellent - highly specific |
| B | 80-89 | Good - minor off-target |
| C | 70-79 | Acceptable - some cross-reactivity |
| D | 60-69 | Poor - significant cross-reactivity |
| F | 0-59 | Fail - major cross-reactivity |

## Warnings

The module generates warnings for:

- Primers with >80% binding to off-target species
- Primers with weak binding to target species
- Multiple off-target binding sites
