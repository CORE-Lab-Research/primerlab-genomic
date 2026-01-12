# Case Study: SARS-CoV-2

A real-world example of designing primers for pathogen detection, specifically identifying the COVID-19 (SARS-CoV-2) spike protein gene.

## Objective

Design a **qPCR assay** (TaqMan) to detect the *Spike (S) gene* of SARS-CoV-2.

**Requirements**:

- **Specificity**: Must not cross-react with Human DNA or other Coronaviruses.
- **Sensitivity**: High efficiency (>90%) for low viral load detection.
- **Amplicon**: Small (<150 bp) for rapid cycling.

---

## Step 1: Input Sequence

We start with a conserved region of the Spike gene.

```fasta
>SARS-CoV-2_S_Gene_Partial
ATGTTTGTTTTTCTTGTTTTATTGCCACTAGTCTCTAGTCAGTGTGTTAATCTTACAACCAGAACTCAATTACCCCCTGCATACACTAATTCTTTCACACGTGGTGTTTATTACCCTGACAAAGTTTTCAGATCCTCAGTTTTACATTCAACTCAGGACTTGTTCTTACCTTTCTTTTCCAATGTTACTTGGTTCCATGCTATACATGTCTCTGGGACCAATGGTACTAAGAGGTTTGATAACCCTGTCCTACCATTTAATGATGGTGTTTATTTTGCTTCCACTGAGAAGTCTAACATAATAAGAGGCTGGATTTTTGGTACTACTTTAGATTCGAAGACCCAGTCCCTACTTATTGTTAATAACGCTACTAATGTTGTTATTAAAGTCTGTGAATTTCAATTTTGTAATGATCCATTTTTGGGTGTTTATTACCACAAAAACAACAAAAGTTGGATGGAAAGTGAG
```

Save this as `sars_cov2_spike.fasta`.

---

## Step 2: Configuration

Create `covid_design.yaml`. Note the specific parameters for pathogen detection.

```yaml
workflow: qpcr
mode: taqman

input:
  sequence_path: ./sars_cov2_spike.fasta

parameters:
  # Standard qPCR Tm settings
  tm:
    min: 58.0
    opt: 60.0 # Standard annealing
    max: 62.0
  
  # Small amplicon for speed
  product_size:
    min: 70
    max: 150
  
  # Probe settings (MUST be higher Tm than primers)
  probe:
    tm:
      min: 68.0
      opt: 70.0
      max: 72.0
    size:
      min: 20
      max: 30

# Critical: Specificity Check
specificity:
  target_database: ./viral_genomes.fasta  # Contains SARS-CoV-2
  background_database: ./human_genome.fasta # Prevent false positives
  check_3_end: true
```

---

## Step 3: Execution

Run the design command with the species check enabled.

```bash
primerlab run qpcr --config covid_design.yaml --species-check
```

## Step 4: Result Analysis

PrimerLab generates `primers.json`. Let's look at the top hit:

```json
{
  "rank": 1,
  "score": 98.5,
  "forward": {
    "sequence": "AGATTCGAAGACCCAGTCC",
    "tm": 59.8
  },
  "reverse": {
    "sequence": "TGAGCAGTGTTTTTGTTC",
    "tm": 60.1
  },
  "probe": {
    "sequence": "ACCAGTCCCTACTTATTGTTAATAACG",
    "tm": 70.2,
    "modification": "FAM-BHQ1"
  },
  "product_size": 112,
  "specificity": "PASS"
}
```

### Why this is a good result

1. **Tm Match**: Primers are 59.8°C / 60.1°C (Perfect match).
2. **Probe Tm**: 70.2°C (10°C higher than primers, ensuring probe binds first).
3. **Size**: 112 bp is ideal for qPCR.
4. **Specificity**: Passed the Human genome screen.

---

## Step 5: Validation (In-Silico)

Before ordering, we run an in-silico PCR to ensure no off-targets were missed.

```bash
primerlab insilico -p parameters.json -t human_genome.fasta
```

**Output**: `0 amplifications found`. (Success!)

---

## Conclusion

We successfully designed a highly specific, standardized qPCR assay for SARS-CoV-2 in under 5 minutes.
