# Operations Runbook

## Overview
The `repo-intel-bundle-v2` now includes an **Orchestrator MCP** that automates the end-to-end process of analyzing repositories, running intelligent agents, and producing governance reports.

## Running the Pipeline

### Method 1: Orchestrator Tool (Recommended)
Use an MCP client (like Claude Desktop or a custom script) to call `repo-intel-orchestrator`:

```json
{
  "name": "run_project_assessment",
  "arguments": {
    "project_name": "quarterly_audit_2026",
    "repo_urls": [
      "https://github.com/myorg/repo-a",
      "https://github.com/myorg/repo-b"
    ],
    "run_agents": true
  }
}
```

### Method 2: CLI Wrapper (via Makefile)
For operations or debugging, you can use the Makefile targets:

```bash
# 1. End-to-End Orchestrator Run (Sample)
make orchestrator
```

## Expected Outputs
All outputs are stored in `outputs/<project_name>/`:

-   **`repos/*.json`**: Raw analysis data from Mission 1.
-   **`agents/*.json`**: Intelligent agent findings (Security, QA).
-   **`governance_summary.md`**: The final portfolio report.

## Troubleshooting

### Authentication Errors
-   **Symptom**: `401 Unauthorized` or API limits.
-   **Fix**: Ensure `GITHUB_TOKEN` is set in `.env` and has `repo` scope.
-   **Enterprise**: Set `GITHUB_API_BASE_URL` in `.env` for GH Enterprise.

### Python Version Mismatch
-   **Symptom**: `ImportError` or `SyntaxError`.
-   **Fix**: Run `make setup` to ensure the virtual environment uses Python 3.10+.

### Adding New Skills
1.  Create skill definition in `skills/`.
2.  Implement agent script in `agents/`.
3.  Import function in `orchestrator/pipeline.py` and add to the execution loop.
