---
name: Confluence Publisher Skill
description: Publishes generated reports to a Confluence Space.
---

# Confluence Publisher Skill

## Mission
Automate the "Last Mile" of delivery by pushing content to Confluence.

## Configuration
Requires environment variables:
- `ENABLE_CONFLUENCE_PUBLISH=true`
- `CONFLUENCE_SPACE_KEY`: Target space.
- `CONFLUENCE_PAGE_ID`: Parent page ID.
- `CONFLUENCE_USERNAME` / `CONFLUENCE_API_TOKEN` (if using real API).

## Actions
1. Reads `seller_page.md`.
2. Converts Markdown to Confluence Storage Format (if necessary) or uses an MCP Press adapter.
3. Updates the target page.
