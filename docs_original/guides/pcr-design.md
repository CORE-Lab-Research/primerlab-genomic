# PCR Primer Design Guide

A complete walkthrough of the PCR primer design workflow.

## Overview

This guide covers:

1. Configuration setup
2. Running the design
3. Understanding output
4. Validating primers
5. Exporting for ordering

---

## 1. Prepare Your Sequence

PrimerLab accepts sequences in two ways:

**Option A: Inline sequence**

```yaml
input:
  sequence: "ATGCGATCGATCG..."
```

**Option B: FASTA file**

```yaml
input:
  sequence_path: /path/to/gene.fasta
```

---

## 2. Configure Parameters

Create `pcr_config.yaml`:

```yaml
input:
  sequence_path: ./my_gene.fasta

parameters:
  # Melting temperature
  tm:
    min: 57.0
    opt: 60.0
    max: 63.0
  
  # Primer length
  primer_size:
    min: 18
    opt: 20
    max: 25
  
  # Amplicon size
  product_size:
    min: 200
    max: 500
  
  # GC content
  gc:
    min: 40.0
    max: 60.0

output:
  format: json
  directory: ./output
```

### Parameter Recommendations

| Application | Product Size | Tm | Notes |
|-------------|:------------:|:--:|-------|
| Cloning | 200-2000 bp | 58-62°C | Standard |
| Colony PCR | 300-1000 bp | 55-60°C | Fast cycling |
| Long-range | 2000-10000 bp | 62-68°C | Long primers |
| Diagnostic | 100-500 bp | 58-62°C | Specific |

---

## 3. Run the Design

```bash
primerlab run pcr --config pcr_config.yaml
```

### Available Options

```bash
primerlab run pcr \
  --config pcr_config.yaml \
  --out results/ \
  --export idt,benchling \
  --report \
  --report-format html
```

| Flag | Purpose |
|------|---------|
| `--out` | Custom output directory |
| `--export` | Generate ordering files |
| `--report` | Generate enhanced report |
| `--mask auto` | Exclude repeat regions |
| `--validate` | Run in-silico PCR |
| `--blast` | Check off-targets |

---

## 4. Understand the Output

### Output Files

| File | Description |
|------|-------------|
| `primers.json` | Full results with all metrics |
| `report.md` | Human-readable summary |
| `primers_idt.csv` | IDT ordering format |
| `audit.json` | Design parameters used |

### Primer Quality Scores

Each primer pair receives a score (0-100) based on:

| Factor | Weight | Criteria |
|--------|:------:|----------|
| Tm match | 25% | Closeness to optimal |
| GC content | 20% | Within 40-60% |
| Self-dimer | 20% | ΔG > -5 kcal/mol |
| Hairpin | 15% | ΔG > -2 kcal/mol |
| 3' stability | 20% | No runs of G/C |

---

## 5. Validate Primers

### In-silico PCR

Verify primers amplify the correct region:

```bash
primerlab insilico \
  -p output/primers.json \
  -t my_gene.fasta
```

### Off-target Check

Check specificity against a genome:

```bash
primerlab blast \
  -p output/primers.json \
  -d /path/to/genome.fasta
```

### Compatibility Check

Verify no primer dimers:

```bash
primerlab check-compat -p output/primers.json
```

---

## 6. Export for Ordering

Generate files for synthesis vendors:

```bash
# IDT format
primerlab run pcr -c config.yaml --export idt

# Multiple formats
primerlab run pcr -c config.yaml --export idt,sigma,thermo
```

### Supported Vendors

| Vendor | Format | Notes |
|--------|--------|-------|
| IDT | CSV | Includes scale/purification |
| Sigma | CSV | Ready for upload |
| Thermo | XLSX | Excel format |
| Benchling | CSV | API-compatible |

---

## Complete Example

```bash
# 1. Create config
cat > gene_amplification.yaml << 'EOF'
input:
  sequence_path: ./BRCA1_exon1.fasta

parameters:
  tm:
    opt: 60.0
  product_size:
    min: 200
    max: 400
  gc:
    min: 45.0
    max: 55.0

output:
  include_rationale: true
EOF

# 2. Design primers
primerlab run pcr \
  --config gene_amplification.yaml \
  --validate \
  --report \
  --export idt

# 3. Review results
cat primerlab_output/report.md
```

---

## Troubleshooting

**No primers found**

- Relax constraints (wider Tm range, larger product size)
- Check sequence for repeat regions (`primerlab stats gene.fasta`)

**Poor quality scores**

- Sequence may have challenging regions (high GC, repeats)
- Try `--mask auto` to avoid problematic areas

**Primers form dimers**

- Run `primerlab check-compat` on results
- Choose pairs with higher compatibility scores

---

## Next Steps

- [qPCR Design](qpcr-design) — Add TaqMan probes
- [Batch Processing](batch-design) — Design for multiple genes
- [Nested PCR](nested-pcr) — Increased specificity
- [Multiplex PCR](multiplex) — Multiple targets
- [Species Specificity](species-specificity) — Pathogen detection
