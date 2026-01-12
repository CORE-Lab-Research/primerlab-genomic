# primerlab validate

Validate a configuration file.

## Synopsis

```bash
primerlab validate <config> [options]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `config` | Yes | Path to config YAML file |

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--workflow` | `-w` | Workflow type (default: pcr) |

## Examples

### Validate PCR Config

```bash
primerlab validate my_config.yaml
```

### Validate qPCR Config

```bash
primerlab validate my_qpcr.yaml --workflow qpcr
```

## Output

**Success:**

```
✅ Configuration is valid!
   Workflow: PCR
   Output: output_pcr
   Tm Range: 58 - 62 °C
   Product Size: 200 - 600 bp
```

**Error:**

```
❌ Configuration Error: Missing required field 'input.sequence'
   Error Code: ERR_CONFIG_MISSING_FIELD
```
