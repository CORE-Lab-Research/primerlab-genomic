# Troubleshooting

Comprehensive solutions for common issues when using PrimerLab.

## Installation & Setup

### `command not found: primerlab`

**Cause**: The package is not installed or not in your PATH.
**Solution**:

1. Ensure you installed with pip: `pip install primerlab-genomic`
2. Check if your Python `bin` directory is in your PATH.
3. Try running via python: `python -m primerlab.cli.main --version`

### `ModuleNotFoundError: No module named 'ViennaRNA'`

**Cause**: ViennaRNA is not installed or not linked correctly.
**Solution**:

- **Conda**: `conda install -c bioconda viennarna`
- **Pip**: `pip install viennarna` (may require compilation)
- **Windows**: Recommend using WSL or Docker, as ViennaRNA native Windows support is tricky.

### `BLAST+ not found`

**Cause**: NCBI BLAST+ toolkit is missing.
**Solution**:

- **Debian/Ubuntu**: `sudo apt-get install ncbi-blast+`
- **macOS**: `brew install blast`
- **Internal Fix**: If installed but not found, set path in config:

    ```yaml
    tools:
      blast_path: /usr/local/bin/blastn
    ```

---

## Design Failures

### `No primers found`

**Cause**: Constraints are too strict.
**Checklist**:

1. [ ] **Tm Range**: Is the range too narrow? Widen it (e.g., `min: 55, max: 65`).
2. [ ] **Product Size**: Is the product size range feasible?
3. [ ] **GC Clamp**: Are you enforcing strict GC clamps? Try disabling.
4. [ ] **Repeats**: Input sequence might be low complexity. Run `primerlab stats input.fasta`.

### `High Self-Complementarity`

**Cause**: Primer sequence folds on itself.
**Solution**:

- Increase `tm_opt`. Higher temperatures melt secondary structures.
- Use `check-compat` to visualize the problem.

---

## Output Issues

### `Report generation failed`

**Cause**: Missing dependencies or IO error.
**Solution**:

- Run with `--debug` to see the full stack trace.
- Ensure you have write permissions to the output directory.

---

## Common Error Messages

| Error Code | Meaning | Solution |
|:---:|---|---|
| `ERR-001` | Invalid DNA Sequence | Check input file for non-IUPAC characters. |
| `ERR-002` | Config Validation Failed | Run `primerlab validate config.yaml`. |
| `ERR-005` | Timeout | Sequence is too long or complex. Increase timeout or mask regions. |
