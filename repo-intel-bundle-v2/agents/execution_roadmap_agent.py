import json
from jinja2 import Template

def run_roadmap_generator(governance_data, output_dir):
    """
    Generates a 3-Phase Roadmap.
    """
    # Logic to slot tasks into phases
    phase_1 = []
    phase_2 = []
    phase_3 = []
    
    for repo in governance_data.get("repos", []):
        # Quick Wins: Config changes
        phase_1.append({"category": "Config", "task": f"Enable Dependabot for {repo['name']}", "effort": 1})
        
        # Stabilization: Testing
        phase_2.append({"category": "Quality", "task": f"Add Unit Tests for {repo['name']}", "effort": 5})
        
        # Modernization: Refactoring
        phase_3.append({"category": "Refactor", "task": f"Migrate {repo['name']} to PyProject", "effort": 8})

    with open("templates/roadmap.md.tmpl", "r") as f:
        template = Template(f.read())
        
    result = template.render(
        project_name="Remediation Execution",
        target_date="Q3 2024",
        phase_1=phase_1,
        phase_2=phase_2,
        phase_3=phase_3,
        milestones=[
            {"date": "Week 4", "name": "Security Baseline Met"},
            {"date": "Week 12", "name": "Quality Gates Enforced"}
        ]
    )
    
    return result
