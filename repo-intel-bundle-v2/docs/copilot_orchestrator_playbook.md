# Copilot Orchestrator Playbook — One-Command Enterprise Audit

## Inputs
- repo_url: https://github.com/jgraph/drawio-mcp
- workflow_file: 01.md
- project_name: drawio_mcp_audit

## Tool Chain (must follow)

### Step 1 — audit.run
Call MCP tool: audit.run
Inputs:
- project_name: drawio_mcp_audit
- repos: ["https://github.com/jgraph/drawio-mcp"]
- workflow_path: "01.md"

Stop if status != success/partial.

### Step 2 — audit.index
Call MCP tool: audit.index
Inputs:
- project_name: drawio_mcp_audit

### Step 3 — audit.context_pack
Call MCP tool: audit.context_pack
Inputs:
- project_name: drawio_mcp_audit
- workflow_path: "01.md"

### Step 4 — Write final report
Using ONLY context_pack_text and referenced artifacts, create:
outputs/drawio_mcp_audit/copilot_final_report.md

Rules:
- No reruns after Step 1
- No scripts
- No code fixes
- Evidence citations: file path + section heading

Report sections:
1) Executive Summary
2) Risk Radar (Security / Tests / Governance / Delivery)
3) Top Findings (max 10, evidence-cited)
4) Explainability View
5) Evidence Graph (Mermaid)
6) Backlog (Epics → Stories → Tasks)
7) Effort & Roadmap summary
8) Confluence-ready Seller Summary