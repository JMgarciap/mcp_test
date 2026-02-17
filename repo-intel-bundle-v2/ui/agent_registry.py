AGENTS = [
    {
        "id": "mcp_analyze",
        "display_name": "Repo Intelligence (MCP)",
        "icon": "ui/assets/repo.png",
        "category": "Core",
        "short_desc": "Static repo scan: CI, Docker, deps, IaC, tests, secrets smells.",
        "purpose": "Analyze repositories to extract metadata and risk signals.",
        "inputs": ["Repo URL", "Git Ref"],
        "outputs": ["Analysis JSON", "Analysis Markdown"],
        "stages": ["MCP_ANALYZE"]
    },
    {
        "id": "security",
        "display_name": "Security Review Agent",
        "icon": "ui/assets/security.png",
        "category": "Reasoning",
        "short_desc": "Interprets risk signals, correlates findings, maps compliance gaps.",
        "purpose": "Assess security posture and identify vulnerabilities.",
        "inputs": ["Analysis JSON"],
        "outputs": ["Security Assessment", "Remediation Plan"],
        "stages": ["AGENT_SECURITY"]
    },
    {
        "id": "tests",
        "display_name": "Test Coverage Agent",
        "icon": "ui/assets/tests.png",
        "category": "Reasoning",
        "short_desc": "Evaluates test maturity, identifies missing test cases, proposes CI gates.",
        "purpose": "Evaluate quality assurance maturity and test gaps.",
        "inputs": ["Analysis JSON"],
        "outputs": ["Coverage Report", "Test Strategy"],
        "stages": ["AGENT_TESTS"]
    },
    {
        "id": "integrator",
        "display_name": "Governance Integrator",
        "icon": "ui/assets/integrator.png",
        "category": "Portfolio",
        "short_desc": "Consolidates multi-repo results, normalizes scores, produces roadmap.",
        "purpose": "Aggregate findings across the portfolio for executive reporting.",
        "inputs": ["Repo Artifacts"],
        "outputs": ["Governance Summary", "Portfolio Roadmap"],
        "stages": ["INTEGRATOR"]
    },
    {
        "id": "planner",
        "display_name": "Agile Delivery Planner",
        "icon": "ui/assets/planner.png",
        "category": "Planning",
        "short_desc": "Generates Epics, User Stories, and a prioritized Backlog.",
        "purpose": "Translate technical findings into an actionable Agile backlog.",
        "inputs": ["Governance Summary"],
        "outputs": ["Backlog.md"],
        "stages": ["AGILE_PLANNER"]
    },
    {
        "id": "roadmap",
        "display_name": "Execution Roadmap",
        "icon": "ui/assets/roadmap.png",
        "category": "Planning",
        "short_desc": "Phases work into Quick Wins, Stabilization, and Modernization.",
        "purpose": "Create a strategic timeline for remediation and improvement.",
        "inputs": ["Governance Summary"],
        "outputs": ["Roadmap.md"],
        "stages": ["EXEC_ROADMAP"]
    },
    {
        "id": "estimator",
        "display_name": "Effort Estimator",
        "icon": "ui/assets/estimator.png",
        "category": "Planning",
        "short_desc": "Estimates Story Points, Resource Needs, and Team Topology.",
        "purpose": "Provide scope and resource sizing for the defined backlog.",
        "inputs": ["Backlog", "Governance Summary"],
        "outputs": ["Effort_Estimation.md"],
        "stages": ["EFFORT_ESTIMATOR"]
    },
    {
        "id": "seller",
        "display_name": "Seller Mode Formatter",
        "icon": "ui/assets/seller.png",
        "category": "Presentation",
        "short_desc": "Transforms outputs into board-ready Confluence page.",
        "purpose": "Format technical data into business-ready executive slides/pages.",
        "inputs": ["Governance Summary"],
        "outputs": ["Seller Page Markdown"],
        "stages": ["SELLER_MODE"]
    },
    {
        "id": "publisher",
        "display_name": "Confluence Publisher",
        "icon": "ui/assets/publisher.png",
        "category": "Delivery",
        "short_desc": "Publishes seller page/sections via MCP Press.",
        "purpose": "Deliver final reports to knowledge management systems.",
        "inputs": ["Seller Page Markdown"],
        "outputs": ["Confluence Page URL"],
        "stages": ["PUBLISH"]
    }
]

def get_agent_by_id(agent_id):
    for agent in AGENTS:
        if agent["id"] == agent_id:
            return agent
    return None

def get_agent_for_stage(stage_name):
    for agent in AGENTS:
        if stage_name in agent["stages"]:
            return agent
    return None
