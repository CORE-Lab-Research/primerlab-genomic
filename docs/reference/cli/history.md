---
title: "primerlab history"
description: "CLI reference for the primerlab history command"
---
View and manage primer design history.

## Synopsis

```bash
primerlab history <subcommand> [options]
```

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `list` | List recent designs |
| `show` | Show details of a design |
| `export` | Export history to CSV |
| `stats` | Show database statistics |
| `delete` | Delete a design |

## Examples

### List Recent Designs

```bash
# Show last 10 designs
primerlab history list

# Show last 20 designs
primerlab history list --limit 20

# Filter by gene
primerlab history list --gene GAPDH

# Filter by workflow
primerlab history list --workflow qpcr
```

### Show Design Details

```bash
primerlab history show 42
```

### Export to CSV

```bash
primerlab history export --output primer_history.csv
```

### View Statistics

```bash
primerlab history stats
```

### Delete a Design

```bash
primerlab history delete 42
```

## Database Location

History is stored in SQLite at:

- Linux/macOS: `~/.primerlab/history.db`
- Windows: `%USERPROFILE%\.primerlab\history.db`
