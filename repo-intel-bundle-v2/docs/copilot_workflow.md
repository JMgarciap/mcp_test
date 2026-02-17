# Copilot Chat Workflow

Use these prompt patterns to control the audit directly from VS Code Chat.

## 🚀 Phase 1: Execution

**User:**
> @repo-intel /run audit.run project_name="audit-v1" repos="https://github.com/pallets/flask" workflow_path="examples/custom_workflow.md"

**Copilot:**
> *Running audit...*
> *(Returns JSON with status: success)*

## 📂 Phase 2: Indexing

**User:**
> @repo-intel /run audit.index project_name="audit-v1"

**Copilot:**
> *Generated INDEX.md and COPILOT_BRIEF.md*

## 📝 Phase 3: Reporting

**User:**
> @repo-intel /run audit.context_pack project_name="audit-v1"

**Copilot:**
> *(Receives massive context string)*

**User:**
> "Based on the context pack, write a detailed executive summary of the security risks."
