---
title: "Batch Processing"
description: "Feature documentation: Batch Processing"
---
Process multiple primer files efficiently with parallel execution and caching.

## Overview

PrimerLab supports batch processing for species-check operations:

- **Directory Loading**: Load all primer JSON files from a directory
- **Parallel Processing**: Multi-threaded execution with `ThreadPoolExecutor`
- **SQLite Caching**: Cache alignment results to avoid redundant calculations
- **Consolidated Reports**: Summary CSV with all results

## CLI Usage

### Batch Species-Check

```bash
primerlab species-check \
  --primers-dir primers/ \
  --target human.fasta \
  --offtargets mouse.fasta \
  --parallel 4 \
  --output results/
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--primers-dir` | Directory with primer JSON files | - |
| `--parallel` | Number of threads | 4 |
| `--no-cache` | Disable SQLite caching | False |

## Python API

### batch_species_check_api

```python
from primerlab.api import batch_species_check_api

result = batch_species_check_api(
    primer_dir="primers/",
    target_name="Human",
    target_template=human_sequence,
    offtarget_templates={"Mouse": mouse_seq},
    max_workers=4
)

print(f"Pass rate: {result['pass_rate']}%")
print(f"Avg score: {result['summary']['avg_score']}")
```

### Using File List

```python
result = batch_species_check_api(
    primer_files=["gene1.json", "gene2.json", "gene3.json"],
    target_name="Human",
    target_template=sequence
)
```

## Batch Loader Module

### load_primers_from_directory

```python
from primerlab.core.species.batch import load_primers_from_directory

batch_input = load_primers_from_directory("primers/")

print(f"Files: {batch_input.total_files}")
print(f"Primers: {batch_input.total_primers}")
```

### load_multi_fasta_templates

```python
from primerlab.core.species.batch import load_multi_fasta_templates

templates = load_multi_fasta_templates("templates/")
for name, template in templates.items():
    print(f"{name}: {len(template.sequence)} bp")
```

## Caching

### SQLite Cache

Alignment results are cached in SQLite for performance:

```python
from primerlab.core.species.batch import AlignmentCache, get_cache

cache = get_cache()
print(f"Cache size: {cache.size()}")
print(f"Hit rate: {cache.hit_rate():.1%}")
```

### Cache Configuration

- **Location**: `~/.primerlab/cache.db`
- **TTL**: 7 days (default)
- **Disable**: Use `--no-cache` flag

## Output

### CSV Report

```csv
Filename,Score,Grade,Is_Specific,Primers_Checked,Warnings
gene1_primers.json,95.0,A,True,2,"None"
gene2_primers.json,78.5,C,True,3,"Low binding on target"

Total,86.8,-,-,-,-
```

### BatchSpeciesResult

```python
@dataclass
class BatchSpeciesResult:
    total_files: int
    total_primers: int
    processed: int
    passed: int
    failed: int
    results: Dict[str, SpeciesCheckResult]
    summary: Dict[str, Any]
```

## Performance Tips

1. **Use caching** for repeated analyses
2. **Match threads** to CPU cores
3. **Organize primers** by project/experiment
4. **Pre-filter** primers before batch processing

## See Also

- [Species Specificity](species-specificity)
- [Batch Tutorial](../tutorials/batch-species-check)
- [CLI Reference](../cli/species-check)
