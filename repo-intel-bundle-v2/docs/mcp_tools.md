# MCP Audit Tools

New high-level tools designed for "One-Command Audits" via Copilot.

## 1. `audit.run`
Runs the orchestration pipeline for a project.

**Inputs:**
- `project_name` (str): Name of the session/project.
- `repos` (str or list): URL(s) of the repositories.
- `workflow_path` (str): Path to the Markdown workflow definition.

**Example Prompt:**
> "Run an audit for project 'fintech-beta' on https://github.com/fastapi/fastapi using workflow examples/custom_workflow.md"

---

## 2. `audit.index`
Generates a map of all created artifacts.

**Inputs:**
- `project_name` (str)

**Example Prompt:**
> "Generate the index for fintech-beta"

---

## 3. `audit.context_pack`
Retrieves a token-optimized summary of the entire run for the LLM.

**Inputs:**
- `project_name` (str)
- `max_chars` (int, default 20000)

**Example Prompt:**
> "Get the context pack for fintech-beta and write a summarized report"
