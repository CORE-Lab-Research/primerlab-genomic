---
title: "Auto Parameter Suggestion"
description: "Feature documentation: Auto Parameter Suggestion"
---
Smart parameter recommendations when primer design fails.

## Overview

When Primer3 fails to find suitable primers, PrimerLab analyzes the failure and suggests parameter adjustments.

## How It Works

1. **Analyze Failure** — Parse Primer3 error messages
2. **Identify Cause** — Determine which constraint failed
3. **Suggest Fix** — Recommend specific parameter changes

## Example Output

```
❌ Design failed: No primers found

💡 Suggestions:
  • Tm constraint too tight - try relaxing to 55-65°C
  • Consider increasing product_size_range to 150-800 bp
  • GC content may be limiting - try 35-65%
```

## Common Suggestions

| Failure Reason | Suggested Action |
|----------------|------------------|
| Tm out of range | Widen Tm constraints |
| GC content issues | Widen GC range |
| No products in size | Increase product size range |
| Probe Tm issues | Adjust probe Tm range |

## Automatic in CLI

Suggestions appear automatically when design fails:

```bash
$ primerlab run pcr --config strict.yaml

🔬 PrimerLab v0.1.6
...
❌ Design failed

💡 Auto-suggestions:
  1. Relax Tm range: 55.0 - 65.0 (current: 59.0 - 61.0)
  2. Increase product size: 100 - 800 bp
```

## Applying Suggestions

Edit your config based on suggestions:

```yaml
# Before (too strict)
tm: {min: 59.0, opt: 60.0, max: 61.0}

# After (relaxed)
tm: {min: 55.0, opt: 60.0, max: 65.0}
```
