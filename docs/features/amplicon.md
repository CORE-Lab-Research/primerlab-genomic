# Amplicon Analysis

Analysis tools for evaluating amplicon quality after primer design.

## Overview

The amplicon analysis module provides comprehensive quality assessment for PCR products including:

- **Secondary Structure**: Predicts potential problematic structures using ViennaRNA
- **GC Profile**: Analyzes GC content distribution across the amplicon
- **GC Clamp**: Evaluates G/C content at amplicon ends
- **Melting Temperature**: Predicts amplicon Tm using nearest-neighbor thermodynamics
- **Quality Score**: Combined 0-100 score with A-F grading

## CLI Usage

### Integrated with Primer Design

```bash
# Analyze amplicons after PCR primer design
primerlab run pcr --config design.yaml --amplicon-analysis
```

### Output

When `--amplicon-analysis` is enabled, the output includes:

- Amplicon quality scores in the JSON output
- Quality warnings in the report

## API Usage

```python
from primerlab.api.public import analyze_amplicon

# Analyze an amplicon sequence
sequence = "ATGCGATCGATCGATCGATCGATCGATCGATCGATCG..."

result = analyze_amplicon(sequence)

print(f"Quality Score: {result['quality_score']}/100 ({result['grade']})")
print(f"Amplicon Tm: {result['amplicon_tm']['tm']}°C")
print(f"Warnings: {result['warnings']}")
```

## Configuration

Default configuration file: `config/amplicon_default.yaml`

```yaml
amplicon_analysis:
  secondary_structure:
    enabled: true
    dg_warning_threshold: -3.0  # kcal/mol
    
  gc_profile:
    enabled: true
    window_size: 50
    ideal_min: 40.0
    ideal_max: 60.0
    
  gc_clamp:
    enabled: true
    region_size: 5
    min_gc: 1
    max_gc: 3
    
  quality_score:
    enabled: true
    weights:
      structure: 0.30
      gc_uniformity: 0.25
      gc_clamp: 0.20
      length: 0.15
      tm_sharpness: 0.10
```

## Quality Scoring

| Grade | Score Range | Interpretation |
|-------|-------------|----------------|
| A | 85-100 | Excellent amplicon quality |
| B | 70-84 | Good quality, minor issues |
| C | 55-69 | Acceptable, some concerns |
| D | 40-54 | Problematic, review recommended |
| F | 0-39 | Poor quality, redesign suggested |

## Warnings

The analyzer generates warnings for:

- Strong secondary structures (ΔG < -8 kcal/mol)
- Non-uniform GC content (>15% spread)
- Weak or strong GC clamps
- Amplicons outside optimal length range (100-500bp)
