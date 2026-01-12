---
title: "API Reference"
description: "Python API reference for API Reference"
---
## Overview

PrimerLab provides a public Python API for programmatic access to primer design functionality.

## Installation

```bash
pip install primerlab-genomic
```

## Quick Start

```python
from primerlab.api import design_pcr_primers, design_qpcr_primers

# Design PCR primers
result = design_pcr_primers(
    sequence="ATCGATCG..." * 100,
    product_size_min=200,
    product_size_max=400
)

print(result.primers)
print(result.success)
```

## API Modules

| Module | Description |
|--------|-------------|
| [`primerlab.api.public`](public-api) | Main public API functions |
| `primerlab.core` | Core design engine (internal) |
| `primerlab.workflows` | Workflow orchestration |

## Key Functions

### `design_pcr_primers()`

Design primers for standard PCR.

```python
from primerlab.api import design_pcr_primers

result = design_pcr_primers(
    sequence="ATCGATCG...",
    product_size_min=200,
    product_size_max=400,
    tm_min=57.0,
    tm_max=63.0
)
```

### `design_qpcr_primers()`

Design primers for quantitative PCR with probe.

```python
from primerlab.api import design_qpcr_primers

result = design_qpcr_primers(
    sequence="ATCGATCG...",
    product_size_max=150,  # qPCR prefers shorter amplicons
    include_probe=True
)
```

### `run_audit()`

Generate a reproducibility audit.

```python
from primerlab.api import run_audit

audit = run_audit(result)
audit.save("audit.json")
```

## Result Objects

### `WorkflowResult`

```python
@dataclass
class WorkflowResult:
    success: bool
    workflow_type: str
    primers: Dict[str, Primer]
    amplicons: List[Amplicon]
    qc_results: Dict[str, QCResult]
    metadata: RunMetadata
    raw_results: Dict[str, Any]
```

### `Primer`

```python
@dataclass
class Primer:
    sequence: str
    tm: float
    gc_content: float
    position: int
    length: int
```

## See Also

- [CLI Reference](../cli/README) - Command-line interface
- [Configuration](../configuration/README) - Config file options
- [Examples](../../examples/README) - Example use cases
