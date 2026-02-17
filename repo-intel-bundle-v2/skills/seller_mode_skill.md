---
name: Seller Mode Skill
description: Transforms technical governance data into executive-level Confluence pages.
---

# Seller Mode Skill

## Mission
Convert raw technical data into "Scannable", "Premium" executive content.

## Inputs
- `governance_summary.json`: The aggregated portfolio data.

## Actions
1. Calculate "Portfolio Health" metrics.
2. Extract "Quick Wins" (Low effort, high impact findings).
3. Generate "Scorecards" comparing repository maturity.
4. Render content using Jinja2 templates optimized for Confluence.

## Output
- `outputs/<project>/confluence/seller_page.md`: A localized Markdown file ready for Confluence import or publishing.
