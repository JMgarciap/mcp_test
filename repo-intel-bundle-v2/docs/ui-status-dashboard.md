# Streamlit Status UI (Mission 5)

This document describes the **Status Dashboard**, a read-only Streamlit application for monitoring the `repo-intel-bundle-v2` pipeline.

## Features
-   **N8N-style Flow**: Visualizes the pipeline stages (Analysis, Agents, Governance, Seller Mode).
-   **Real-time Monitoring**: Polling based; updates as `outputs/<project>/events.jsonl` is written.
-   **Local-Only**: No external calls; strictly file-based observation.
-   **Resilient**: Continues to function even if artifacts are missing.

## How it Works
1.  **Event Bus**: The Orchestrator emits events to `events.jsonl` and updates `status.json`.
2.  **Streamlit App**: Reads these files periodically (default 2s refresh).
3.  **Visualization**: Shows progress bars, timelines, and Graphviz flow diagrams.

## Usage

### 1. Install Dependencies
```bash
make ui-install
```

### 2. Run the UI
```bash
make ui
```
Opens `http://localhost:8501`.

### 3. Run the Orchestrator (in separate terminal)
```bash
make orchestrator
# OR via Inspector
```
You will see the UI update in real-time.

### 4. Tailing Events (CLI)
```bash
make tail PROJECT=<project_name>
```

## Troubleshooting
-   **Graphviz Error**: Ensure `dot` is installed on your system (`brew install graphviz`).
-   **No Projects**: Run `make sample` or `make orchestrator` first to generate output directories.
