# **PrimerLab — AI Contributor Rules**

These rules define **what automated contributors (AI assistants, LLM agents, auto-coders) may and may not do** when contributing to the PrimerLab codebase.

These rules must be followed **strictly**.
Violations can break architecture, determinism, reproducibility, and workflows.

This document overrides all other guidelines if conflict arises.

---

# **1. General Principles**

Automated contributors must:

### **1.1 Follow project architecture exactly**

Architecture is defined in:

* `architecture.md`
* blueprint documents
* module-plan
* design-decisions

### **1.2 Never break determinism**

All workflows must produce identical output for identical input.

### **1.3 Never introduce security risks**

Follow:

* security-guidelines.md
* config safety rules
* logging safety rules

### **1.4 Always write testable, isolated modules**

All new code must integrate with test guidelines.

### **1.5 Minimize changes**

If unsure → do not modify.

### **1.6 Use Session Log (MANDATORY)**

At the **start** of every session:

* Read `.dev/AI Helper Files/SESSION_LOG.md`
* Understand context from previous sessions

At the **end** of every session (or before major changes):

* Update `SESSION_LOG.md` with:
  * Tasks attempted (success/fail)
  * Files changed
  * Issues encountered and resolutions
  * Notes for next session

This ensures continuity across chat sessions.

---

# **2. Allowed Contribution Scope**

Automated contributors **ARE allowed** to:

* write functions inside existing modules
* update internal utilities
* assist with workflow implementation
* refactor core code when safe
* create/modify unit tests
* create/modify integration tests
* add logging/progress statements
* update report generators
* update config schema (if explicitly instructed)
* fix bugs using existing architecture

They also may:

* create new internal modules (inside approved folders)
* add workflow utilities to workflow-specific directories

Provided they follow folder structures exactly.

---

# **3. Forbidden Contribution Scope**

Automated contributors **MUST NOT**:

### **3.1 Modify Public API Surface**

Forbidden:

* renaming public functions
* adding new public functions
* removing existing public functions
* changing argument names or order

### **3.2 Change Project Structure**

Forbidden:

* renaming folders
* adding new top-level folders
* reorganizing modules

### **3.3 Alter Workflow Folder Structure**

Example forbidden changes:

* moving workflow.py
* creating nested workflow folders
* mixing workflows

### **3.4 Create New Dependencies**

Forbidden:

* adding new PyPI packages
* requiring conda packages
* downloading binaries

### **3.5 Modify Error Codes**

Error codes are absolute and cannot be changed.

### **3.6 Introduce Randomness**

Forbidden:

* `random` usage
* timestamps in computations
* nondeterministic ordering
* hashed dictionaries without sorting

### **3.7 Directly Edit Table of Contents Files**

Never modify:

* README root
* long documentation indices

Unless explicitly instructed.

---

# **4. Import Rules (Strict)**

AI contributors must obey:

### **4.1 Public API imports**

Allowed only from:

```
from primerlab.api import ...
```

But public API must NOT be modified.

### **4.2 Workflow imports**

Workflows may import:

* local workflow modules
* core modules

Forbidden:

* importing other workflows
* importing public API
* importing CLI
* importing debug tools directly

### **4.3 Core imports**

Core modules may import ONLY:

* other core modules
* approved third-party packages

Forbidden:

* importing workflows
* importing public API
* importing CLI
* importing tests

### **4.4 No relative imports across layers**

Forbidden:

```
from ..core import something
```

Allowed:

```
from primerlab.core.module import something
```

---

# **5. Logging & Progress Rules**

AI contributors must:

* never write `print()`
* always use `log.info`, `log.warning`, `log.error`
* follow progress step templates exactly
* never log sensitive data (sequence content, API keys)
* never write multiline log entries

Progress messages must mirror workflow step boundaries.

---

# **6. Config Handling Rules**

### **6.1 Use central config loader only**

Forbidden:

```python
yaml.safe_load(open(file))
```

Allowed:

```python
from primerlab.core.config_loader import load_config
```

### **6.2 Never mutate config**

Forbidden:

```python
config["parameter"] = value
```

### **6.3 Validate keys using existing schema**

AI must not create new config fields unless instructed.

---

# **7. Error & Exception Rules**

Automated contributors must:

* use only allowed exceptions (`PrimerLabException` subclasses)
* not create new exception classes unless explicitly permitted
* reference error codes using constants defined in error-codes.md
* never print tracebacks
* write tracebacks only into debug folder

Forbidden:

```python
raise Exception("Something broke")
```

Allowed:

```python
raise ConfigError(ERR_CONFIG_002, "Missing parameter")
```

---

# **8. Output System Rules**

Automated contributors must:

* write outputs using output system utilities
* never write arbitrary files
* never write outside run folder
* never change output folder structure
* never include sensitive data in logs/reports

Forbidden:

```python
open("output.txt", "w")
```

Allowed:

```python
output_manager.write_json(...)
```

---

# **9. External Tools Rules**

AI contributors must ensure:

* all external tool calls use secure wrappers
* no shell=True
* no string-built commands
* all executions mocked in tests

Forbidden:

```python
os.system("primer3_core -args")
subprocess.run("primer3_core --args", shell=True)
```

Allowed:

```python
from primerlab.core.tools.primer3_wrapper import run_primer3
```

---

# **10. Testing Rules for AI-Generated Code**

### AI MUST

* write deterministic tests
* use mocks for external tools
* include golden tests for new workflows
* ensure tests run < 5 seconds
* follow test folder structure
* follow naming conventions

### AI MUST NOT

* call external binaries
* use large sample data
* write slow tests
* modify existing golden files unless explicitly instructed

---

# **11. Code Style Rules**

AI contributors must follow:

* coding-style.md
* naming-convention.md
* no unused imports
* no inline lambda complexity
* explicit return types
* consistent docstrings
* use pathlib
* avoid complex comprehensions
* use helper utilities where appropriate

---

# **12. Safety & Security Rules**

Automated contributors must obey:

* security-guidelines.md
* never embed keys
* never expose user paths
* never echo user-provided sequences
* never include private file content in logs
* never call unsafe deserializers

Forbidden:

```python
pickle.load(...)
yaml.load(...)
```

Allowed:

```python
yaml.safe_load(...)
```

---

# **13. Documentation Rules**

AI must:

* update docs when implementing new workflow features
* write in English
* use Markdown
* avoid copying API keys or sample sensitive data
* keep explanations short and clean

Forbidden:

* generating documentation in unsupported formats
* mixing languages
* generating PDFs

---

# **14. When AI Contributors Must Ask for Human Approval**

AI contributors must NOT proceed without explicit instruction if tasks require:

* new workflows
* new modules outside allowed scope
* new config fields
* changes to folder structure
* new public APIs
* changes that break determinism
* changes affecting error codes
* adding dependencies
* complex refactors

If unsure → STOP and ask.

---

# **15. Summary**

These rules ensure automated contributors:

* maintain architectural integrity
* preserve determinism
* follow strict security
* produce testable and safe code
* do not break the public API
* do not alter project structure
* remain consistent with design decisions
* collaborate safely with human maintainers

**AI Helper Rules = the law of the land.**
Every automated contribution must comply.
