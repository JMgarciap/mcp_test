# repo-intel-bundle-v2

An MCP server that performs static analysis on GitHub repositories (Enterprise or public) and produces local JSON/Markdown reports.

## Features

-   **Static Analysis:** Analyzes repository content without cloning or running builds.
-   **GitHub Enterprise Support:** Configurable API base URL.
-   **Deterministic Outputs:** Generates structured JSON and Markdown reports in a local `outputs/` directory.
-   **Scoring:** Calculates Quality, Cloud Readiness, and Risk scores.
-   **FastMCP:** Built using the `mcp.server.fastmcp` framework.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repo_url>
    cd repo-intel-bundle-v2
    ```

2.  **Configure environment:**
    ```bash
    cp .env.example .env
    # Edit .env and add your GITHUB_TOKEN
    ```

3.  **Install dependencies:**
    ```bash
    make setup
    ```

## Usage

### Run the MCP Server

```bash
make run
```

### Run Sample Analysis

```bash
make sample
```

## Output Structure

Reports are generated in the `outputs/` directory:

```
outputs/
  <project_name>/
    repos/
      <owner>_<repo>.json
      <owner>_<repo>.md
    summary.json
    summary.md
```
