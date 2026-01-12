# Troubleshooting

Common issues and solutions for PrimerLab.

## Debug Mode

Enable verbose logging:

```bash
primerlab run pcr --config my_config.yaml --debug
```

Check system status:

```bash
primerlab health
```

---

## Common Errors

### Configuration Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Config file not found` | Wrong path | Check file path exists |
| `Invalid workflow type` | Typo in workflow | Use `pcr` or `qpcr` |
| `Missing required field` | Incomplete config | Add missing field |

**Example fix:**

```yaml
# Wrong
workflow: PCR  # Case matters!

# Correct
workflow: pcr
```

---

### Sequence Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid sequence characters` | Non-ATCG bases | Use IUPAC codes or clean sequence |
| `Sequence too short` | < 50 bp | Provide longer template |
| `File not found` | Wrong path | Verify `sequence_path` |

---

### Primer3 Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `No primers found` | Constraints too strict | Relax parameters |
| `primer3-py not installed` | Missing dependency | `pip install primer3-py` |

**Relaxing constraints:**

```yaml
parameters:
  tm:
    min: 55.0  # Lower from 58.0
    max: 65.0  # Raise from 62.0
  gc:
    min: 35    # Lower from 40
    max: 65    # Raise from 60
```

---

## Warning Meanings

### Thermodynamic Warnings

| Warning | Meaning | Action |
|---------|---------|--------|
| `Hairpin ΔG too stable` | Primer may form hairpin | Consider alternative primer |
| `Homodimer ΔG too stable` | Primer may self-dimerize | Check with different parameters |
| `3' end too stable` | May cause mispriming | Generally OK, monitor specificity |

### QC Warnings

| Warning | Meaning | Action |
|---------|---------|--------|
| `Tm difference > 3°C` | Primers have different Tm | May reduce efficiency |
| `No GC clamp` | No G/C at 3' end | Usually OK for standard PCR |
| `Low complexity region` | Repetitive sequence | Check for mispriming |

---

## Off-target Warnings

| Grade | Meaning | Action |
|-------|---------|--------|
| A | Excellent specificity | ✅ Safe to use |
| B | Good specificity | ✅ Safe to use |
| C | Moderate specificity | ⚠️ Verify experimentally |
| D | Poor specificity | ⚠️ Consider alternatives |
| F | Very poor specificity | ❌ Do not use |

---

## FAQ

### "No primers found"

1. Check if sequence is too short (< 200 bp)
2. Relax Tm range (try 55-65°C)
3. Relax product size range
4. Try `qc: mode: relaxed`

### "ViennaRNA not found"

ViennaRNA is optional. Without it:

- Secondary structure checks are skipped
- Warning is shown but design continues

To install (Linux/WSL):

```bash
sudo apt install viennarna
```

### "BLAST database not found"

Off-target check requires a BLAST database:

```bash
# Create database
makeblastdb -in genome.fasta -dbtype nucl -out genome_db

# Use in config
offtarget:
  database: "/path/to/genome_db"
```

---

## Log Files

Output directory contains:

| File | Content |
|------|---------|
| `result.json` | Design results |
| `report.md` | Human-readable report |
| `audit.json` | Reproducibility log |

---

## Getting Help

1. Check this troubleshooting guide
2. Run `primerlab health` to verify installation
3. Use `--debug` flag for verbose output
4. Open an issue on [GitHub](https://github.com/engkinandatama/primerlab-genomic/issues)
