# Off-target Analysis Tutorial

Check primer specificity with BLAST.

## Prerequisites

### Install BLAST

```bash
# Ubuntu/Debian
sudo apt install ncbi-blast+

# macOS
brew install blast

# Verify
blastn -version
```

### Create database

```bash
# From genome FASTA
makeblastdb -in genome.fasta -dbtype nucl -out genome_db

# Pre-built databases available at NCBI
# https://ftp.ncbi.nlm.nih.gov/blast/db/
```

---

## Method 1: Integrated with Design

Run off-target check during primer design:

```bash
primerlab run pcr \
  --config my_config.yaml \
  --blast \
  --blast-db /path/to/genome_db
```

Output includes specificity grades:

```
Primer Pair 1:
  Forward: A (100% specific)
  Reverse: B (1 off-target, low identity)
  Overall: A
```

---

## Method 2: Standalone Check

Check existing primers:

```bash
primerlab blast \
  -f "ATGAGTAAAGGAGAAGAACT" \
  -r "GCCGTGATGTATACATTGTG" \
  -d /path/to/genome_db
```

Or from result file:

```bash
primerlab blast \
  -p output_pcr/result.json \
  -d /path/to/genome_db
```

---

## Understanding Results

### Grades

| Grade | Off-targets | Action |
|-------|-------------|--------|
| A | 0 | ✅ Safe to use |
| B | 1-2 low identity | ✅ Safe to use |
| C | 3-5 | ⚠️ Verify experimentally |
| D | 6-10 | ⚠️ Consider alternatives |
| F | >10 | ❌ Do not use |

### Score calculation

```
Score = 100 - (off_targets × penalty)

Penalty based on:
- Identity (higher = worse)
- 3' match (critical)
- Alignment length
```

---

## Output Files

```
blast_results/
├── blast_report.json     # Full BLAST results
├── specificity_report.md # Human-readable summary
└── off_targets.fasta     # Off-target sequences
```

---

## Configuration Options

In YAML config:

```yaml
offtarget:
  enabled: true
  database: "/path/to/genome_db"
  mode: auto  # auto, blast, biopython
  max_targets: 100
  evalue: 10
  threads: 4
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Database not found | Check path, run makeblastdb |
| BLAST not installed | Install ncbi-blast+ |
| Too many off-targets | Try different primer pair |
| Slow performance | Use --threads option |

---

## Next Steps

- [PCR Walkthrough](pcr-walkthrough.md)
- [qPCR Design](qpcr-design.md)
- [Troubleshooting](../troubleshooting.md)
