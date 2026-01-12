# primerlab species-check

Check primer specificity across multiple species templates.

## Synopsis

```bash
primerlab species-check --primers FILE --target FILE [OPTIONS]
```

## Description

The `species-check` command analyzes primer binding across target and off-target species to ensure specificity. It calculates binding scores, identifies cross-reactivity risks, and generates detailed reports.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--primers, -p` | Yes | Path to primers JSON file |
| `--target, -t` | Yes | Path to target species FASTA |
| `--offtargets` | No | Comma-separated off-target FASTA files |
| `--output, -o` | No | Output directory (default: species_check_output) |
| `--format` | No | Report format: markdown, json, excel, html (default: markdown) |
| `--primers-dir` | No | Directory with multiple primer JSON files (batch mode) |
| `--parallel` | No | Number of threads for batch processing (default: 4) |
| `--no-cache` | No | Disable SQLite caching |

## Examples

### Basic Usage

```bash
primerlab species-check \
  --primers primers.json \
  --target human_template.fasta
```

### With Off-targets

```bash
primerlab species-check \
  --primers primers.json \
  --target human.fasta \
  --offtargets mouse.fasta,rat.fasta \
  --output results/
```

### Batch Mode

```bash
primerlab species-check \
  --primers-dir primers_directory/ \
  --target human.fasta \
  --parallel 4 \
  --output batch_results/
```

### HTML Report

```bash
primerlab species-check \
  --primers primers.json \
  --target human.fasta \
  --format html
```

## Input Format

### primers.json

```json
[
  {"name": "Gene1", "forward": "ATGCGATCGATCGATCGATCG", "reverse": "CGATCGATCGATCGATCGCAT"},
  {"name": "Gene2", "forward": "GCTAGCTAGCTAGCTAGCTAG", "reverse": "TAGCTAGCTAGCTAGCTAGCT"}
]
```

### FASTA Files

```
>SpeciesName
ATGCGATCGATCGATCGATCG...
```

## Output

### Console Output

```
🧬 Species Specificity Check (v0.4.3)
==================================================
📂 Loading primers: primers.json
🎯 Target: Human (350 bp)
🔬 Off-targets: Mouse, Rat

⏳ Analyzing 2 primer pairs...

==================================================
📊 Specificity Results:
   Gene1: Score 95.0 (Grade A) ✅ SPECIFIC
   Gene2: Score 87.5 (Grade B) ✅ SPECIFIC

🎯 Overall: 91.3 (Grade A)
   Specific: 2/2 (100%)

📁 Report saved to: species_check_output/species_analysis.md
```

### Report Files

- `species_analysis.json` - Full JSON data
- `species_analysis.md` - Markdown report
- `species_analysis.html` - HTML report
- `species_analysis.xlsx` - Excel workbook

## Scoring

| Score | Grade | Meaning |
|-------|-------|---------|
| ≥90 | A | Excellent specificity |
| 80-89 | B | Good specificity |
| 70-79 | C | Acceptable |
| 60-69 | D | Poor - review recommended |
| <60 | F | Fail - redesign required |

## See Also

- [Species Specificity Feature](../features/species-specificity.md)
- [Species Check Tutorial](../tutorials/species-check.md)
- [Batch Processing](../features/batch-processing.md)
