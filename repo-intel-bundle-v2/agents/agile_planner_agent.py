import json
import os
from jinja2 import Template

def run_agile_planner(governance_data, output_dir):
    """
    Generates a Backlog from governance data.
    """
    # Heuristics to generate stories from findings
    epics = []
    
    # Epic 1: Security Remediation
    security_features = []
    for repo in governance_data.get("repos", []):
        score = repo.get("scores", {}).get("security", 100)
        if score < 80:
            security_features.append({
                "name": f"Harden {repo['name']}",
                "stories": [
                    {"id": "SEC-001", "role": "Security Eng", "goal": "patch critical vulnerabilities", "benefit": "reduce exploit risk", "priority": "P0"},
                    {"id": "SEC-002", "role": "DevOps", "goal": "rotate secrets", "benefit": "prevent unauthorized access", "priority": "P0"}
                ]
            })
    
    if security_features:
        epics.append({
            "name": "Security Hardening",
            "description": "Remediate critical security vulnerabilities across the portfolio.",
            "features": security_features
        })
        
    # Epic 2: Quality Assurance
    qa_features = []
    for repo in governance_data.get("repos", []):
        if repo.get("scores", {}).get("test_coverage", 0) < 50:
            qa_features.append({
                "name": f"Improve Testing for {repo['name']}",
                "stories": [
                    {"id": "QA-001", "role": "SDET", "goal": "setup CI test runner", "benefit": "catch regressions", "priority": "P1"},
                    {"id": "QA-002", "role": "Dev", "goal": "increase unit coverage to 50%", "benefit": "improve stability", "priority": "P2"}
                ]
            })
            
    if qa_features:
        epics.append({
            "name": "Quality Assurance Uplift",
            "description": "Establish baseline testing standards.",
            "features": qa_features
        })

    # Render Template
    with open("templates/backlog.md.tmpl", "r") as f:
        template = Template(f.read())
        
    result = template.render(
        project_name="Portfolio Remediation",
        date="2024-05-20", # Dynamic in real usage
        technical_problems=[{"category": "Security", "description": "Multiple repos with secret leaks"}], # Placeholder
        risk_areas=[{"severity": "High", "description": "Lack of CI/CD hardening"}],
        epics=epics,
        backlog=["Update documentation", "Review licensing"]
    )
    
    return result
