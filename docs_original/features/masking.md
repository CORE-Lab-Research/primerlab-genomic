# Region Masking

Exclude specific regions from primer placement.

## Overview

Region masking prevents primers from being placed in:

- **Repeat regions** (detected as lowercase from RepeatMasker)
- **Unknown regions** (N-masked segments)
- **Custom exclusions** (BED file)

## Usage

Use the `--mask` flag with `primerlab run`:

```bash
# Auto-detect all masked regions
primerlab run pcr --config my.yaml --mask auto

# Only lowercase (RepeatMasker) regions
primerlab run pcr --config my.yaml --mask lowercase

# Only N-masked regions
primerlab run pcr --config my.yaml --mask n
```

## Mask Modes

| Mode | Description |
|------|-------------|
| `auto` | Detect both lowercase and N regions |
| `lowercase` | Only RepeatMasker-style lowercase |
| `n` | Only N-masked regions |
| `none` | No masking (default) |

## BED File Support

Define custom exclusion zones with a BED file:

```
# excluded_regions.bed
chr1    100    200    repeat_region
chr1    500    600    SNP_hotspot
```

## Example Output

```
🎭 Region Masking Report
========================
Mode: auto
Detected Regions: 3

  [50-75]     lowercase   (26 bp)
  [120-145]   N-masked    (26 bp)
  [200-250]   lowercase   (51 bp)

Total Masked: 103 bp (8.7% of sequence)
```

## How It Works

1. **Detection** — Identify masked regions in sequence
2. **Exclusion** — Mark regions as off-limits for primers
3. **Design** — Primer3 avoids placing primers in masked areas
4. **Report** — Show which regions were excluded
