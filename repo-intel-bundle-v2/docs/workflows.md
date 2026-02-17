# Dynamic Workflows

Repo Intel Bundle v2 supports **Dynamic Workflows**, allowing you to define exactly which agents to run using a Markdown checklist.

## Usage

```bash
python scripts/run_orchestrator.py \
  --project my_audit \
  --repos https://github.com/my/repo \
  --workflow examples/custom_workflow.md
```

## Workflow File Format

The workflow file is a standard Markdown file. The orchestrator looks for checklist items (`- [ ]`).

- **Checked (`- [x]`)**: Phase will run.
- **Unchecked (`- [ ]`)**: Phase will be skipped.

### Syntax
```markdown
- [x] phase:<phase_name> [param1=val1] [param2=val2]
```

### Available Phases

| Phase | Description | Key Agent |
| :--- | :--- | :--- |
| `analysis` | Basic git analysis and stats | RepoAnalyzer |
| `security` | Vulnerability & secret scanning | VulnerabilityDetective |
| `tests` | Test coverage analysis | TestCoverageAgent |
| `governance` | Compliance aggregation | GovernanceIntegrator |
| `planning` | Backlog & Roadmap generation | AgilePlanner |
| `reporting` | Executive summary & Confluence | SellerFormatter |

## Example

Save this as `my_flow.md`:

```markdown
# My Security Audit
- [x] phase:analysis ref=main
- [x] phase:security
- [ ] phase:tests (Skip tests for this run)
- [x] phase:reporting
```
