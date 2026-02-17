# Confluence Seller Mode

**Seller Mode** is a premium reporting feature that transforms technical analysis into executive-ready dashboards.

## Features
-   **Executive Summary**: High-level impact assessment.
-   **Quick Wins**: Automatically identified low-hanging fruit.
-   **Scorecards**: Clear, comparative tables.
-   **Roadmap**: Strategic timeline for remediation.

## How to Enable
Seller Mode runs automatically as part of the `Orchestrator` pipeline when `run_agents=True`.

## Output Location
Artifacts are generated in:
`outputs/<project_name>/confluence/seller_page.md`

## Publishing to Confluence
To enable automatic publishing, set the following in `.env`:

```bash
ENABLE_CONFLUENCE_PUBLISH=true
CONFLUENCE_SPACE_KEY=ENG
CONFLUENCE_PAGE_ID=12345678
```

*Note: Currently, the publisher runs in "Mock Mode" and logs the intent to publish without making API calls.*
