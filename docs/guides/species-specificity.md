# Species Specificity

Ensure your primers amplify *only* your target organism and ignore background DNA.

## Use Cases

- **Pathogen Detection**: Detect *Salmonella* in a *Human* sample.
- **Environmental DNA (eDNA)**: Identify specific species in water/soil samples.
- **GMO Testing**: Distinguish transgenic sequences from host crops.

## How It Works

PrimerLab uses BLAST+ to check primer candidates against two databases:

1. **Target Database**: The genome(s) of the organism you WANT to amplify.
2. **Background Database**: The genome(s) of organisms you do NOT want to amplify (e.g., Human, Mouse, Soil metagenome).

It calculates a **Specificity Score**:

- **+ Points**: Perfect matches in Target Database.
- **- Points**: Significant matches in Background Database, especially at the 3' end.

---

## Configuration

Add a `specificity` block to your config:

```yaml
# specificity_config.yaml
specificity:
  # Positive control: Primers MUST bind here
  target_database: ./data/salmonella_genome.fasta
  
  # Negative control: Primers MUST NOT bind here
  background_database: ./data/human_genome.fasta
  
  # Thresholds
  min_specificity_score: 90
  check_3_end: true  # Critical for specificity
```

## Running the Check

### Integrated Workflow

Run this during primer design to filter out non-specific primers automatically:

```bash
primerlab run pcr --config specificity_config.yaml --species-check
```

### Standalone Tool

Check existing primers:

```bash
primerlab species-check \
  --primers my_primers.json \
  --target-db salmonella.fasta \
  --background-db human.fasta
```

---

## Interpreting Results

The tool outputs a summary table:

| Primer Pair | Target Hits | Background Hits | Specificity Score | Status |
|-------------|:-----------:|:---------------:|:-----------------:|:------:|
| Pair 1      | 1           | 0               | 100               | ✅ PASS |
| Pair 2      | 1           | 5               | 45                | ❌ FAIL |
| Pair 3      | 1           | 1 (weak)        | 85                | ⚠️ WARN |

- **FAIL**: Significant background amplification likely.
- **WARN**: Weak background binding; may work if annealing temperature is optimized.
