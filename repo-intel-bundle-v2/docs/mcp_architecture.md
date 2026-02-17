# Enterprise MCP Server Architecture

## Overview
The **Repo Intel Bundle v2** exposes its capabilities through a **Model Context Protocol (MCP)** server built with **FastAPI**.

This architecture allows AI assistants (like GitHub Copilot) to discover and execute platform tools directly, enabling "Chat with your Repo" workflows.

## Layers

### 1. Interface Layer (MCP Tools)
- **Location**: `orchestrator/mcp_tools.py`
- **Role**: Thin wrappers around business logic independently callable by AI.
- **Registry**: `orchestrator/tool_registry.py` handles auto-discovery and schema generation.

### 2. Logic Layer (Agents)
- **Location**: `agents/*.py`
- **Role**: The core intelligence (Security, Testing, Governance).
- **Execution**: Tools invoke the `AssessmentPipeline` which orchestrates these agents.

### 3. Transport Layer (FastAPI)
- **Location**: `orchestrator/mcp_server.py`
- **Role**: Handles HTTP requests (`POST /mcp/invoke`) and exposes the JSON-RPC interface.
- **Port**: 3333

## Available Tools

| Tool Name | Description | Agent Backing |
| :--- | :--- | :--- |
| `analyze_repository` | Basic stats and language detection | Base Analyzer |
| `security_review` | Finds vulns and secrets | Vulnerability Detective |
| `test_coverage_analysis` | Checks testing maturity | Test Coverage Agent |
| `governance_evaluation` | Corporate compliance check | Governance Integrator |
| `generate_agile_backlog` | AI-generated user stories | Agile Planner |
| `estimate_delivery_effort` | Story points estimation | Effort Estimator |
| `generate_execution_roadmap` | Implementation timeline | Roadmap Agent |
| `generate_seller_summary` | Executive one-pager | Seller Formatter |

## Integration Flow

1. **User** types prompt in Copilot: "Check security for repo X".
2. **Copilot** queries `/mcp/tools` to find `security_review`.
3. **Copilot** sends `POST /mcp/invoke` with repo URL.
4. **Server** runs the pipeline and returns the findings.
5. **Copilot** summarizes the findings to the User.
