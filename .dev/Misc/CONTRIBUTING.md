# **Contributing to PrimerLab**

Thank you for your interest in contributing to **PrimerLab**!
This project follows a carefully designed architecture to ensure:

* deterministic behavior
* reproducible scientific results
* security and safety
* clarity and modularity
* long-term maintainability

This document explains how both **human contributors** and **automated contributors** (AI-based agents, coding assistants) must participate in the project.

---

# **1. Before You Start**

Before contributing, please read these core documents:

### **Required Reading**

* `.dev/High-Level Documentation/architecture.md`
* `.dev/High-Level Documentation/module-plan.md`
* All Blueprint documents in `.dev/Blueprint Files/`
* `.dev/AI Helper Files/ai-helper-rules.md`
* `.dev/AI Helper Files/ai-prompts.md`
* `.dev/Misc/design-decisions.md`
* `.dev/Misc/security-guidelines.md`
* `.dev/Misc/test-guidelines.md`

These define **all rules, constraints, and architectural boundaries**.

---

# **2. How to Contribute**

Contributions fall into several categories:

### ✔ Allowed

* fixing bugs
* improving internal modules
* extending QC logic
* adding internal utilities
* writing unit tests
* writing integration tests
* improving documentation
* enhancing workflow internals
* adding optional tool wrappers
* improving error messages
* performance optimizations (non-breaking)

### ✖ Forbidden

* modifying public API
* altering folder structure
* rewriting workflow entrypoints
* changing error codes
* breaking determinism
* embedding API keys
* adding external dependencies
* modifying output schema
* introducing randomness

If unsure → ask before proceeding.

---

# **3. Repository Structure**

PrimerLab uses a strict folder architecture:

```
primerlab/
    api/
    core/
    workflows/
        pcr/
        qpcr/         (future)
        crispr/       (future)
        multiplex/    (future)
docs/
tests/
```

Contributors must NOT:

* create new top-level folders
* move workflow directories
* store configs or secrets inside code

---

# **4. Setting Up Development Environment**

### Requirements

* Python 3.11
* Virtual environment (.venv)
* Linux or WSL2 recommended
* No global installation of dependencies

### Setup

```
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r primerlab/requirements.txt
pip install -r primerlab/requirements-dev.txt
```

### Run tests

```
pytest
```

---

# **5. Coding Standards**

All code must follow:

* `.dev/Development Rules/coding-style.md`
* `.dev/High-Level Documentation/naming-convention.md`

Key principles:

* deterministic
* modular
* explicit
* safe
* small functions
* descriptive names
* pathlib only (no os.path)

Never log sensitive data (raw sequences, keys).

---

# **6. Testing Requirements**

Every contribution **must** include tests.

### **Required:**

* unit tests for new modules
* updated tests when modifying existing modules
* integration tests when workflows change
* golden tests when output schema touched

### **Not Allowed:**

* slow tests (> 700ms integration, > 200ms unit)
* external tool calls
* random inputs

Tests must pass:

```
pytest --disable-warnings
```

Minimal coverage target: **80%**.

---

# **7. Using Automated Contributors (AI Assistants)**

PrimerLab is designed to work with automated coding tools.

Automated contributors must:

* follow all rules in `ai-helper-rules.md`
* use approved templates in `task-templates.md`
* respect architecture and determinism
* avoid modifying public API
* avoid creating new dependencies
* never break output structure
* never introduce randomness
* use mocks for all external tools

If a human uses an AI assistant to generate code, they must confirm it follows project rules.

---

# **8. Workflow Contribution Rules**

When modifying workflows:

* do not change workflow entrypoints
* do not mutate config
* use logger for all step boundaries
* integrate with progress system
* create/update WorkflowResult
* update report templates if needed
* write integration tests

Follow all workflow-related blueprints.

---

# **9. Submitting Pull Requests**

### Steps

1. Fork repository
2. Create a new branch
3. Make your changes
4. Ensure all tests pass
5. Ensure no architecture violations
6. Ensure deterministic behavior
7. Update docs if required
8. Submit a pull request

### PR Must Include

* summary of changes
* files modified
* justification based on blueprint/rules
* notes on backward compatibility

### PR Will Be Rejected If

* changes public API
* breaks tests
* adds new dependencies
* violates architecture
* removes determinism
* contains unsafe code

---

# **10. Code Review Checklist**

Reviewers (human or automated) must verify:

* naming conventions
* deterministic behavior
* logs + progress integration
* exceptions use error codes
* no external tool calls in tests
* no print() statements
* no shell=True subprocess calls
* minimal patch size
* no sensitive sequence logging
* config validation rules applied correctly

---

# **11. Communication Rules**

All contributors must:

* be clear
* be respectful
* avoid assumptions
* provide reproducible cases
* reference blueprint or ADRs when proposing changes

If a major modification is needed → open an Issue first.

---

# **12. Contributor Safety**

NEVER submit:

* personal biological sequences
* laboratory confidential data
* real patient sequences
* proprietary PCR targets

Use synthetic and mock data only.

---

# **13. Licensing**

PrimerLab is released under the MIT license.
Contributors must accept their contributions being incorporated under this license.

---

# **14. Summary**

By following this guide, contributors (human and automated) ensure that PrimerLab remains:

* safe
* deterministic
* maintainable
* scientific-grade
* collaborative
* extensible

PrimerLab is a long-term project — stability and clarity are essential.

We welcome your contributions!
Please follow the rules and enjoy building the future of computational molecular design.
