# primerlab stats

Analyze sequence statistics before primer design.

> **New in v0.1.6**

## Synopsis

```bash
primerlab stats <sequence> [options]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `sequence` | Yes | Path to FASTA file or raw sequence |

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--json` | `-j` | Output as JSON |

## Output

The stats command displays:

- **Length** — Sequence length in base pairs
- **GC Content** — GC percentage and count
- **AT Content** — AT percentage and count
- **N Count** — Number of masked (N) bases
- **IUPAC Codes** — Detected ambiguous codes
- **RNA Detection** — Whether sequence contains uracil (U)

## Examples

### Basic Usage

```bash
primerlab stats input.fasta
```

**Output:**

```
📊 Sequence Statistics: GAPDH
=============================================
  Length:      3,605 bp
  GC Content:  50.98% (1,838 bp)
  AT Content:  49.02% (1,767 bp)
=============================================
✅ Ready for primer design
```

### JSON Output

```bash
primerlab stats input.fasta --json
```

**Output:**

```json
{
  "name": "GAPDH",
  "length": 3605,
  "gc_percent": 50.98,
  "gc_count": 1838,
  "at_count": 1767,
  "n_count": 0,
  "iupac_codes": [],
  "iupac_count": 0,
  "has_uracil": false,
  "valid_for_design": true
}
```

### With Masked Regions

```bash
primerlab stats masked_sequence.fasta
```

**Output:**

```
📊 Sequence Statistics: TEST_MASKED
=============================================
  Length:      1,178 bp
  GC Content:  53.99% (636 bp)
  AT Content:  41.26% (486 bp)
  N (masked):  56 bp (4.75%)
=============================================
✅ Ready for primer design
```

### With IUPAC Codes

```bash
primerlab stats sequence_with_iupac.fasta
```

**Output:**

```
📊 Sequence Statistics: TEST_IUPAC
=============================================
  Length:      500 bp
  GC Content:  48.20% (241 bp)
  AT Content:  50.60% (253 bp)
  ⚠️  IUPAC codes: ['R', 'Y'] (6 bp)
      → Will be converted to N during design
=============================================
✅ Ready for primer design
```

## Use Cases

1. **Pre-flight check** — Verify sequence before design
2. **Pipeline scripting** — Use `--json` for automated workflows
3. **Troubleshooting** — Identify problematic sequences
