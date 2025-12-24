# **PrimerLab — Standard AI Prompt Library**

This document defines **approved prompt templates** for interacting with automated contributors safely.

These prompts ensure that AI-generated code:

* respects architectural boundaries
* follows coding standards
* uses deterministic functions
* stays within allowed modules
* triggers correct testing patterns

All prompts are written in a “role + constraints + task + output” format to eliminate ambiguity.

---

# **1. Purpose of This Document**

This file provides:

* reusable, safe prompts
* templates for code tasks
* templates for refactoring
* templates for workflow updates
* templates for tests
* templates for docs and configs

Every contributor (human or automated) must use these templates for consistent output.

---

# **2. Fundamental Prompt Format**

Every prompt must follow this structure:

```
You are an automated contributor for PrimerLab.
Follow all rules in .dev/AI Helper Files/ai-helper-rules.md.
Follow the architecture defined in .dev/High-Level Documentation/architecture.md.
Never modify public API, output schema, config schema, or folder layout.

<task description>

Respond ONLY with:
1) Implementation plan
2) Final patch/code block (no explanation)

Do NOT add imports beyond those allowed.
Do NOT introduce new dependencies.
Do NOT break determinism.
```

All templates below are specializations of this structure.

---

# **3. Prompt Template — Implement Module**

```
You are an automated contributor for PrimerLab.
Follow ai-helper-rules.md strictly.

Task: Implement <module>/<function>.
Read:
- architecture.md
- module-plan.md
- relevant blueprint
- coding-style.md
- naming-convention.md

Constraints:
- deterministic output only
- no public API changes
- use logger only if workflow-level
- do not mutate config
- use pathlib for paths

Respond with:
1. Implementation Plan
2. Final code block only
```

---

# **4. Prompt Template — Modify Workflow**

```
You are an automated contributor for PrimerLab.
Follow ai-helper-rules.md and blueprint for this workflow.

Task: Modify workflow: <workflow name>

Read:
- blueprint-output-system.md
- blueprint-logging-system.md
- blueprint-config-system.md
- workflow standards

Constraints:
- keep workflow entrypoint same
- use log.info for steps
- do not print
- update WorkflowResult if explicitly instructed
- deterministic behavior required

Respond with:
1. Step-by-step plan
2. Final patch (code only)
```

---

# **5. Prompt Template — Create Unit Tests**

```
You are an automated contributor for PrimerLab.
Follow ai-helper-rules.md and test-guidelines.md.

Task: Create unit tests for <module/function>.

Constraints:
- deterministic tests
- use pytest
- use mocks where external tools are involved
- run under 200ms
- no real filesystem except tmp_path
- no random numbers

Respond with:
1. Test plan
2. Final test file (code only)
```

---

# **6. Prompt Template — Create Integration Test**

```
You are an automated contributor for PrimerLab.
Follow ai-helper-rules.md and integration-tests.md.

Task: Create integration test for workflow <name>.

Constraints:
- mock Primer3/BLAST
- validate output folder structure
- validate logs
- validate debug folder
- golden output required (if applicable)
- must run <700ms

Respond with:
1. Test plan
2. Final test code only
```

---

# **7. Prompt Template — Fix Bug**

```
You are an automated contributor for PrimerLab.
Follow ai-helper-rules.md.

Task: Fix bug: <bug description>.

Provide:
1. Reproduction summary
2. Root cause analysis
3. Patch plan
4. Final code patch

Constraints:
- do not alter public API
- do not change folder structure
- do not change error codes
```

---

# **8. Prompt Template — Refactor Code**

```
You are an automated contributor for PrimerLab.
Follow ai-helper-rules.md.

Task: Refactor module <module> for clarity/performance.

Constraints:
- must not change behavior
- must not break tests
- must not change JSON output ordering
- no new dependencies
- minimal changes only

Respond with:
1. Refactor plan
2. Final code patch
```

---

# **9. Prompt Template — Add Config Parameter**

```
You are an automated contributor for PrimerLab.
Follow ai-helper-rules.md and config-design.md.

Task: Add new config parameter <name>.

Respond with:
1. Required updates list:
   - config schema
   - config loader
   - workflow validation
   - documentation
   - sample configs
   - tests

2. Final patches for all affected files

Constraints:
- backward compatible
- do not break existing configs
```

---

# **10. Prompt Template — Update Report Generator**

```
You are an automated contributor for PrimerLab.
Follow ai-helper-rules.md and blueprint-output-system.md.

Task: Modify report generator to <goal>.

Constraints:
- deterministic formatting
- do not change output folder structure
- do not include sensitive sequence data
- follow Markdown style rules

Respond with:
1. Change plan
2. Final patch
```

---

# **11. Prompt Template — Update External Tool Wrapper**

```
You are an automated contributor for PrimerLab.
Follow ai-helper-rules.md and security-guidelines.md.

Task: Update external tool wrapper <tool>.

Constraints:
- no shell=True
- safe subprocess only
- deterministic mocks required
- update corresponding tests

Respond with:
1. Implementation plan
2. Final code patch
```

---

# **12. Prompt Template — Documentation Update**

```
You are an automated contributor for PrimerLab.

Task: Update documentation in <file>.

Constraints:
- English only
- markdown only
- must follow design decisions
- must not alter architecture
- must not modify index or directory structure

Respond with:
1. Update summary
2. Final Markdown patch
```

---

# **13. Prompt Template — Safe Multi-File Change**

For big tasks.

```
You are an automated contributor for PrimerLab.
Follow ALL project rules.

Task: Multi-file update for <goal>.

Constraints:
- list every file edited
- apply changes minimalistically
- no new folders unless explicitly allowed
- no public API changes
- reproducibility must be preserved

Respond with:
1. Change summary
2. File-by-file plan
3. Final patches
```

---

# **14. Prompt Template — Execute Code Analysis**

```
You are an automated contributor for PrimerLab.

Task: Analyze module <module> for:
- architecture violations
- security violations
- determinism issues
- missing tests
- style violations

Respond with:
1. Summary of issues found
2. Fix plan
(no code unless asked)
```

---

# **15. Summary**

This document provides a **complete library of safe, reusable AI prompts** that produce:

* deterministic results
* architecture-compliant code
* minimal and safe changes
* high-quality implementations
* reproducible workflows
* predictable behavior

All automated work inside PrimerLab must use these templates.
