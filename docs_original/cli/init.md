# primerlab init

Generate a template configuration file.

## Synopsis

```bash
primerlab init [options]
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--workflow` | `-w` | Workflow type: pcr, qpcr (default: pcr) |
| `--output` | `-o` | Output filename (default: config.yaml) |

## Examples

### Generate PCR Config

```bash
primerlab init
# Creates config.yaml
```

### Generate qPCR Config

```bash
primerlab init --workflow qpcr --output my_qpcr.yaml
```

## Generated Config

The generated config includes all available options with comments:

```yaml
workflow: pcr

input:
  sequence: "YOUR_SEQUENCE_HERE"
  # Or use: sequence_path: "input.fasta"

parameters:
  primer_size: {min: 18, opt: 20, max: 24}
  tm: {min: 58.0, opt: 60.0, max: 62.0}
  product_size_range: [[200, 600]]
  gc: {min: 40, max: 60}

output:
  directory: "output_pcr"
```
