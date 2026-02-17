import json
from jinja2 import Template

def run_effort_estimator(governance_data, output_dir):
    """
    Generates Effort Estimation.
    """
    repo_count = len(governance_data.get("repos", []))
    finding_count = 0 
    # Mocking finding count from aggregate
    finding_count = repo_count * 12 
    
    total_sp = finding_count * 3 # 3 pts per finding avg
    
    resources = {
        "backend": max(1, repo_count // 2),
        "devops": 1,
        "security": 1,
        "qa": max(1, repo_count // 3),
        "architect": 1,
        "devops_util": 50,
        "security_util": 30
    }
    
    complexity = {
        "low": int(finding_count * 0.5),
        "medium": int(finding_count * 0.3),
        "high": int(finding_count * 0.2)
    }

    with open("templates/effort_estimation.md.tmpl", "r") as f:
        template = Template(f.read())
        
    result = template.render(
        date="2024-05-20",
        repo_count=repo_count,
        finding_count=finding_count,
        total_story_points=total_sp,
        estimated_duration_months=3,
        confidence_level="Medium",
        resources=resources,
        complexity=complexity,
        velocity=40
    )
    
    return result
