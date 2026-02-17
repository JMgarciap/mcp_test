# Architecture

## Pipeline Flowchart

```mermaid
flowchart TD
    A[Client (Copilot/User)] -->|analyze_repo(url)| B(MCP Server)
    B --> C{GitHub Client}
    C -->|Fetch Meta & Tree| D[GitHub API]
    B --> E[Signal Detector]
    E -->|Read Files| C
    E -->|Signals| F[Scoring Engine]
    F -->|Scores| G[Analyzer]
    G -->|Result JSON| H[Report Generator]
    H -->|Markdown| I[Final Output]
    I --> A
```

## Component Interaction

1.  **Server (`server.py`)**: Receives request.
2.  **Analyzer (`analyzer.py`)**: Orchestrates the process.
3.  **GitHub Client (`github_client.py`)**: Fetches tree and content.
4.  **Signal Detector (`signals.py`)**: Scans for patterns.
5.  **Scoring (`scoring.py`)**: Computes scores.
6.  **Report Generator (`report.py`)**: Formats output.
