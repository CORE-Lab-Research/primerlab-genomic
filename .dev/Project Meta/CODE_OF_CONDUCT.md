# **PrimerLab Code of Conduct**

The PrimerLab community aims to provide a welcoming, safe, and productive environment for all contributors — human and automated — working together to build a high-quality computational biology framework.

This Code of Conduct outlines expectations for behavior, collaboration, and scientific responsibility.
Participation in this project implies agreement to this code.

---

# **1. Core Principles**

All contributors must:

* treat others respectfully
* collaborate constructively
* maintain scientific integrity
* follow architectural and security guidelines
* protect sensitive data
* communicate clearly and professionally

PrimerLab is a technical and scientific project.
Professionalism is required at all times.

---

# **2. Respectful Collaboration**

Contributors must:

* be considerate of different levels of experience
* provide helpful and actionable feedback
* accept constructive criticism
* avoid personal attacks
* keep discussions technical and relevant

Harassment or discriminatory behavior will not be tolerated.

---

# **3. Scientific & Technical Integrity**

All contributors must uphold high standards:

* no falsification of data
* no fabricated benchmarks
* no misleading documentation
* no unsafe biological claims
* no misuse of computational tools

Scientific accuracy is essential.

---

# **4. Data Safety & Ethical Standards**

PrimerLab deals with DNA/RNA sequences and molecular design tools.
To ensure ethical and responsible use:

### **4.1 Prohibited Data**

Contributors must NOT submit:

* patient genetic sequences
* clinical laboratory sequences
* proprietary biotech sequences
* identifiable biological samples
* restricted or confidential genomic data

Only synthetic, mock, or publicly licensed sequences are allowed.

### **4.2 Privacy & Confidentiality**

* Do not share private data or keys.
* Do not commit sensitive files to the repository.
* Do not include real-world metadata that could identify individuals or institutions.

---

# **5. Security, Safety & Responsible Use**

Contributors must follow:

* `security-guidelines.md`
* safe subprocess execution rules
* config and logging safety constraints
* deterministic workflow principles

Prohibited behaviors:

* unsafe subprocess calls (`shell=True`)
* leaking API keys
* logging raw biological sequences
* executing unvalidated external commands
* adding unsafe dependencies

PrimerLab must remain secure and safe for scientific use.

---

# **6. Automated Contributor Behavior**

Automated tools (AI assistants, agents, code generators) are welcome but must obey:

* `.dev/AI Helper Files/ai-helper-rules.md`
* `task-templates.md`
* deterministic behavior
* architectural boundaries
* security guidelines

Automated contributions that violate rules will be rejected.

Human contributors using AI are responsible for verifying output.

---

# **7. Contribution Standards**

All contributions must:

* follow architecture & module design
* pass all tests
* maintain determinism
* not break backward compatibility
* follow the naming and coding style
* include tests for new features or fixes
* update documentation when needed

Refactoring or feature changes that break these standards will not be accepted.

---

# **8. Communication Standards**

In issues, pull requests, and discussions:

* be concise
* stay technical
* provide reproducible examples
* avoid emotionally charged language
* prefer evidence over opinion

If there is a disagreement, refer to:

* blueprint documents
* module-plan
* design-decisions.md
* ADR history
* security guidelines

Objective reasoning always prevails.

---

# **9. Unacceptable Behavior**

The following actions are not tolerated:

* personal insults or hostility
* disclosing sensitive biological data
* ignoring architecture rules intentionally
* introducing unsafe or malicious code
* undermining determinism
* bypassing tests
* spam, trolling, or content unrelated to development
* misuse of AI tools to generate low-quality, large patches

Violations may result in:

* discussion lock
* PR rejection
* temporary or permanent ban

---

# **10. Reporting Issues**

If you encounter:

* unsafe code
* guideline violations
* security concerns
* harmful biological content
* harassment

Please open a **Private Issue** or contact maintainers directly.
Maintain confidentiality when reporting sensitive issues.

---

# **11. Enforcement**

Project maintainers will:

* review reports fairly
* ensure proportional responses
* maintain confidentiality
* align enforcement with project values

Decisions by maintainers are final.

---

# **12. Acknowledgment**

By participating in the PrimerLab project, contributors agree to:

* follow this Code of Conduct
* uphold scientific integrity
* prioritize safety and reproducibility
* collaborate respectfully
* comply with all architectural and security rules

Thank you for helping build a safe, open, and scientifically rigorous community.

---
