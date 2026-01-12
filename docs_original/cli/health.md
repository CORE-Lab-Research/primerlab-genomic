# primerlab health

Check all dependencies and system status.

## Synopsis

```bash
primerlab health
```

## Output

```
🔬 PrimerLab Health Check v0.1.6
=============================================
✅ Python 3.12.3
✅ primer3-py (installed)
✅ ViennaRNA (available)
✅ PyYAML (installed)
✅ Rich installed
✅ tqdm 4.67.1
⚠️ Biopython not found (optional)

---------------------------------------------
📡 Checking for updates...
✅ You are on the latest version (v0.1.6)

=============================================
Health check complete.
```

## Dependency Status

| Icon | Meaning |
|------|---------|
| ✅ | Installed and working |
| ⚠️ | Optional, not installed |
| ❌ | Required, not installed |

## Version Check (v0.1.6)

The health command now checks GitHub for newer releases and shows:

- Current version
- Latest available version
- Update instructions if newer version exists
