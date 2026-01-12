# Quick Start Tutorial

Design your first PCR primers in 5 minutes.

## Step 1: Prepare Your Sequence

Save your target sequence as `my_gene.fasta`:

```
>My_Target_Gene
ATGAGTAAAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGAATTAGATGGT
GATGTTAATGGGCACAAATTTTCTGTCAGTGGAGAGGGTGAAGGTGATGCAACATACGGA
AAACTTACCCTTAAATTTATTTGCACTACTGGAAAACTACCTGTTCCATGGCCAACACTT
GTCACTACTTTCTCTTATGGTGTTCAATGCTTTTCCCGTTATCCGGATCATATGAAACGG
CATGACTTTTTCAAGAGTGCCATGCCCGAAGGTTATGTACAGGAACGCACTATATCTTTC
AAAGATGACGGGAACTACAAGACGCGTGCTGAAGTCAAGTTTGAAGGTGATACCCTTGTT
AATCGTATCGAGTTAAAAGGTATTGATTTTAAAGAAGATGGAAACATTCTCGGACACAAA
CTCGAGTACAACTATAACTCACACAATGTATACATCACGGCAGACAAACAAAAGAATGGA
ATCAAAGCTAACTTCAAAATTCGCCACAACATTGAAGATGGATCCGTTCAACTAGCAGAC
CATTATCAACAAAATACTCCAATTGGCGATGGCCCTGTCCTTTTACCAGACAACCATTAC
```

---

## Step 2: Create Configuration

Create `pcr_config.yaml`:

```yaml
workflow: pcr

input:
  sequence_path: "my_gene.fasta"

parameters:
  primer_size: {min: 18, opt: 20, max: 24}
  tm: {min: 58.0, opt: 60.0, max: 62.0}
  product_size_range: [[200, 400]]

output:
  directory: "output_pcr"
```

---

## Step 3: Run Primer Design

```bash
primerlab run pcr --config pcr_config.yaml
```

Expected output:

```
🧬 PrimerLab v0.3.5
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1/5] Loading sequence...
[2/5] Designing primers...
[3/5] Running QC...
[4/5] Scoring primers...
[5/5] Generating report...

✅ Design complete!
   Primers: 5 pairs
   Best score: 95.2
   Output: output_pcr/
```

---

## Step 4: View Results

### Check the report

```bash
cat output_pcr/report.md
```

### View primer details

```bash
cat output_pcr/result.json | jq '.primers[0]'
```

Example output:

```json
{
  "forward": {
    "sequence": "ATGAGTAAAGGAGAAGAACT",
    "tm": 58.5,
    "gc": 40.0,
    "length": 20
  },
  "reverse": {
    "sequence": "GCCGTGATGTATACATTGTG",
    "tm": 59.2,
    "gc": 45.0,
    "length": 20
  },
  "amplicon_size": 320,
  "score": 95.2
}
```

---

## Step 5: Validate (Optional)

Run in-silico PCR to validate:

```bash
primerlab insilico \
  -f "ATGAGTAAAGGAGAAGAACT" \
  -r "GCCGTGATGTATACATTGTG" \
  -t my_gene.fasta
```

---

## Next Steps

- [PCR Walkthrough](pcr-walkthrough.md) - Detailed configuration
- [qPCR Design](qpcr-design.md) - TaqMan assay design
- [Off-target Analysis](offtarget-tutorial.md) - BLAST check

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No primers found | Relax Tm or product size range |
| File not found | Check file path |
| Invalid sequence | Ensure FASTA format |

See [Troubleshooting](../troubleshooting.md) for more.
