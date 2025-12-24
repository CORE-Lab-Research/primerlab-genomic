# **PrimerLab — AI Helper Overview**

This document introduces the AI Helper system — a set of guide files designed to help automated contributors (AI coding assistants, LLM-based agents, or autonomous tools) safely contribute to PrimerLab.

These helper files do **not** contain source code.
Instead, they define:

* rules
* architectural constraints
* task boundaries
* allowed operations
* allowed imports
* coding expectations
* safety checks
* interaction patterns

Their purpose is to ensure AI-generated code is **high quality, consistent, and never breaks the architecture**.

---

# **1. Purpose of the AI Helper System**

PrimerLab is intentionally designed for hybrid development:
human contributors + automated contributors.

AI helpers exist to:

* assist in writing code
* generate workflow templates
* update modules
* create new tests
* follow blueprint and architecture rules
* enforce deterministic patterns
* avoid architectural violations
* maintain reproducibility
* prevent unsafe code

They act as “rules of engagement” for any automation.

---

# **2. Why AI Helpers Are Needed**

Without guidance, AI-generated code tends to:

* break import rules
* create circular dependencies
* bypass architecture layers
* log sensitive data
* introduce random nondeterministic behavior
* write unsafe subprocess code
* modify public API unintentionally
* change folder structure
* remove determinism from output
* violate config schema
* include unused dependencies

AI helpers reduce these risks by being explicit and strict.

---

# **3. Structure of the AI Helper System**

AI Helpers live under:

```
.dev/AI Helper Files/
```

Files include:

| File                      | Purpose                                     |
| ------------------------- | ------------------------------------------- |
| **ai-helper-overview.md** | You are here. High-level explanation        |
| **ai-helper-rules.md**    | Hard requirements AI must follow            |
| **ai-prompts.md**         | Prompt templates for safe, consistent tasks |
| **task-templates.md**     | Templates for structured development tasks  |

These files allow AIs to work modularly and role-specifically.

---

# **4. Expected Automated Contributor Behavior**

Automated contributors **must**:

### **4.1 Follow architecture strictly**

* Do not import from wrong layer
* Do not violate public/workflow/core boundaries

### **4.2 Preserve determinism**

* no randomness
* no time-dependent output
* no uncontrolled external calls

### **4.3 Follow exact file structure**

* never add new folders without instruction
* never rename folders
* never relocate modules

### **4.4 Use logging + progress systems correctly**

* no print statements
* always log progress steps

### **4.5 Guarantee safe, testable code**

* must run under unit/integration tests
* must produce deterministic JSON
* must not introduce flakiness

### **4.6 Avoid adding dependencies**

* only use dependencies in requirements.txt
* no new libraries unless explicitly approved

---

# **5. Allowed Contribution Types**

AI helpers may assist with:

* implementing workflow functions
* writing workflow utilities
* updating QC logic
* creating unit tests
* adding integration tests
* generating Markdown reports
* updating documentation
* maintaining internal modules
* writing tool wrappers (mocked)
* refactoring internal code (core-only)

AI helpers may NOT:

* modify public APIs
* change config schema
* change output folder structure
* redefine WorkflowResult
* alter error codes
* restructure repositories
* add new workflows without approval
* modify version numbers

---

# **6. Safety Boundaries for Automated Code**

Automated contributors must not:

* call real external binaries
* produce shell=True subprocess code
* embed API keys in code
* write unvalidated, dynamic paths
* log raw biological sequences
* use unsafe loaders (yaml.load)
* alter deterministic functions

If a task requires these changes, a human contributor must review first.

---

# **7. Interaction Workflow for Automated Tools**

AI-based contributors follow this pattern:

```
1. Read ai-helper-rules.md
2. Read architecture.md
3. Read module-plan.md
4. Read blueprint documents relevant to the task
5. Perform task in isolation
6. Validate code format and style
7. Produce final patch
```

Each step ensures stable and safe contributions.

---

# **8. Versioning & Evolution of AI Helper Files**

AI helper files evolve with project milestones:

* v0.1.x → minimal PCR-only support
* v0.2.x → qPCR, CRISPR workflows added
* v0.3.x → multiplex workflows added
* v0.4–1.0 → structure modeling & advanced tools added
* v1.1+ → plugin system support

Automated contributors must always check these helpers before generating code.

---

# **9. Example Use Cases for AI Helpers**

### **9.1 Use Case: Generate QC engine update**

AI reads:

* blueprint-data-model
* blueprint-config
* blueprint-error-handling

Then produces QC code consistent with architecture.

### **9.2 Use Case: Add new workflow step**

AI reads:

* module-plan
* architecture
* logging-progress rules

And outputs deterministic workflow updates.

### **9.3 Use Case: Create integration tests**

AI reads:

* integration-tests.md
* test-guidelines.md

And generates proper golden test structure.

---

# **10. Limitations of AI Helpers**

AI helpers **do not**:

* replace human code review
* decide new features
* change architecture
* modify design decisions
* create external dependencies

They enforce boundaries — not creativity.

---

# **11. Summary**

The AI Helper System is a structured set of documents guiding automated contributors to produce:

* safe
* deterministic
* architecture-compliant
* readable
* testable
* maintainable

code within the PrimerLab project.

It prevents accidental architecture violations and ensures long-term project consistency, even when automated agents contribute to core development.
