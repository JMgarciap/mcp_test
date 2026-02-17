import json
import os
import glob
import argparse
from datetime import datetime

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def save_markdown(path, content):
    with open(path, 'w') as f:
        f.write(content)

def aggregate_data(project_dir):
    repos_dir = os.path.join(project_dir, "repos")
    agents_dir = os.path.join(project_dir, "agents")
    
    # Load all repo JSONs
    repo_files = glob.glob(os.path.join(repos_dir, "*.json"))
    
    portfolio = []
    
    for f in repo_files:
        print(f"Loading {f}...")  # Helpful for debugging
        try:
            repo_data = load_json(f)
            # Infer slug based on filename or data
            basename = os.path.basename(f).replace(".json", "")
            
            # Load corresponding agent outputs if they exist
            vuln_path = os.path.join(agents_dir, f"{basename}.vuln_detective.json")
            test_path = os.path.join(agents_dir, f"{basename}.test_coverage.json")
            
            vuln_data = load_json(vuln_path) if os.path.exists(vuln_path) else {}
            test_data = load_json(test_path) if os.path.exists(test_path) else {}
            
            item = {
                "name": f"{repo_data['metadata'].get('owner', 'unknown')}/{repo_data['metadata'].get('repo', 'unknown')}",
                "scores": repo_data.get("scores", {}),
                "security_score": vuln_data.get("security_score", "N/A"),
                "risk_level": vuln_data.get("risk_level", "N/A"),
                "testing_maturity": test_data.get("testing_maturity", "N/A")
            }
            portfolio.append(item)
        except Exception as e:
            print(f"Skipping {f}: {e}")

    return {"repos": portfolio}

def generate_governance_report(portfolio, project_name):
    timestamp = datetime.now().isoformat()
    
    # Calculate Averages
    repos = portfolio.get("repos", [])
    
    # Calculate Averages
    total_quality = sum(i['scores'].get('quality', 0) for i in repos)
    avg_quality = total_quality / len(repos) if repos else 0
    
    md = []
    md.append(f"# Governance Report: {project_name}")
    md.append(f"**Date:** {timestamp}")
    md.append(f"**Repos Analyzed:** {len(repos)}")
    md.append(f"**Portfolio Health (Avg Quality):** {avg_quality:.1f}/100")
    md.append("")
    
    md.append("## Portfolio Dashboard")
    md.append("| Repository | Quality | Cloud | Risk | Security Score | Test Maturity |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    
    for i in repos:
        md.append(f"| {i['name']} | {i['scores'].get('quality')} | {i['scores'].get('cloud_readiness')} | {i['scores'].get('risk')} | {i.get('security_score')} | {i.get('testing_maturity')} |")
    md.append("")

    md.append("## Strategic Roadmap")
    
    # Phase 1: High Risk
    md.append("### Phase 1: Risk Remediation")
    high_risk = [i['name'] for i in repos if i.get('risk_level') in ['Critical', 'High'] or i['scores'].get('risk', 0) > 50]
    if high_risk:
        for r in high_risk: md.append(f"- [ ] Fix critical security issues in **{r}**")
    else:
        md.append("- No critical risks detected.")
        
    # Phase 2: Standardization
    md.append("### Phase 2: Standardization")
    low_tests = [i['name'] for i in repos if i.get('testing_maturity') == 'Low']
    if low_tests:
        for r in low_tests: md.append(f"- [ ] Implement CI and basic tests for **{r}**")
    else:
        md.append("- All repos have basic testing infrastructure.")
    
    md.append("")
    md.append("## Visualizations")
    
    # Mermaid Code
    md.append("```mermaid")
    md.append("pie title Risk Distribution")
    
    risk_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "N/A": 0}
    for i in repos:
        risk_counts[i.get('risk_level', 'N/A')] += 1
        
    for k, v in risk_counts.items():
        if v > 0: md.append(f'    "{k}" : {v}')
    md.append("```")

    return "\n".join(md)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", help="Path to project output directory (containing repos/)")
    args = parser.parse_args()
    
    portfolio = aggregate_data(args.project_dir)
    project_name = os.path.basename(args.project_dir)
    
    report = generate_governance_report(portfolio, project_name)
    
    # Save
    out_path = os.path.join(args.project_dir, "governance_summary.md")
    json_path = os.path.join(args.project_dir, "governance_summary.json")
    
    save_markdown(out_path, report)
    save_json(json_path, portfolio)
    
    print(f"Generated governance report at {out_path}")

if __name__ == "__main__":
    main()
