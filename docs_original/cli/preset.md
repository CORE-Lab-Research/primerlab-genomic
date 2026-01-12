# primerlab preset

Manage and view design presets.

## Synopsis

```bash
primerlab preset <subcommand> [options]
```

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `list` | List all available presets |
| `show` | Show details of a specific preset |

## Examples

### List Presets

```bash
primerlab preset list
```

**Output:**

```
📋 Available Presets:

  • long_range
  • high_gc

Use 'primerlab preset show <name>' for details.
```

### Show Preset Details

```bash
primerlab preset show long_range
```

## Using Presets in Config

```yaml
workflow: pcr

preset: long_range  # Apply preset parameters

input:
  sequence_path: "my_gene.fasta"

output:
  directory: "output_long_range"
```

Presets provide optimized parameters for specific use cases.
