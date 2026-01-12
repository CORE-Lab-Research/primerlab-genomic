# primerlab compare

Compare two primer design results side-by-side.

## Synopsis

```bash
primerlab compare <result_a> <result_b> [options]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `result_a` | Yes | Path to first result.json |
| `result_b` | Yes | Path to second result.json |

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--labels` | `-l` | Custom labels (default: A,B) |

## Examples

### Basic Comparison

```bash
primerlab compare run1/result.json run2/result.json
```

### With Custom Labels

```bash
primerlab compare run1/result.json run2/result.json --labels "Original,Optimized"
```

## Output

The comparison shows:

- Quality scores
- Tm balance
- GC content
- Hairpin/dimer ΔG values
- Pros and cons for each design
- Winner determination
