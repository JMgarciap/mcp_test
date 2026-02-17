import json
import os
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

def analyze_coverage(repo_data):
    signals = repo_data.get("signals", {})
    
    has_tests = signals.get("has_tests", False)
    has_ci = signals.get("has_ci", False)
    
    # Determine Maturity
    if has_tests and has_ci:
        maturity = "High"
    elif has_tests or has_ci:
        maturity = "Medium"
    else:
        maturity = "Low"
        
    # Gaps & Recommendations
    gaps = []
    backlog = []
    
    if not has_tests:
        gaps.append("No automated tests detected.")
        backlog.append("Initialize unit testing framework (e.g., pytest, jest).")
        backlog.append("Write smoke tests for critical paths.")
    
    if not has_ci:
        gaps.append("No CI pipeline found.")
        backlog.append("Create GitHub Actions workflow for linting and testing.")
    
    if has_tests and not has_ci:
        gaps.append("Tests exist but execution is not automated in CI.")
        backlog.append("Automate existing tests in CI pipeline.")

    return {
        "agent": "Test Coverage Agent",
        "repo_slug": f"{repo_data['metadata']['owner']}_{repo_data['metadata']['repo']}",
        "timestamp": datetime.now().isoformat(),
        "testing_maturity": maturity,
        "gaps": gaps,
        "backlog": backlog
    }

def generate_report(data):
    md = []
    md.append(f"# Test Coverage Report: {data['repo_slug']}")
    md.append(f"**Date:** {data['timestamp']}")
    md.append(f"**Testing Maturity:** {data['testing_maturity']}")
    md.append("")
    
    md.append("## Maturity Assessment")
    if data['testing_maturity'] == "High":
        md.append("🟢 **High Maturity**: Project has both tests and CI integration.")
    elif data['testing_maturity'] == "Medium":
        md.append("🟡 **Medium Maturity**: Partial implementation found (Tests or CI missing).")
    else:
        md.append("🔴 **Low Maturity**: No testing infrastructure detected.")
    md.append("")

    if data['gaps']:
        md.append("## Critical Gaps")
        for gap in data['gaps']:
            md.append(f"- ⚠️ {gap}")
        md.append("")

    md.append("## Recommended Backlog")
    for item in data['backlog']:
        md.append(f"- [ ] {item}")
        
    return "\n".join(md)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Path to repo analysis JSON")
    parser.add_argument("output_dir", help="Directory to save agent outputs")
    args = parser.parse_args()

    repo_data = load_json(args.input_file)
    result = analyze_coverage(repo_data)
    
    # Paths
    slug = result['repo_slug']
    os.makedirs(args.output_dir, exist_ok=True)
    json_path = os.path.join(args.output_dir, f"{slug}.test_coverage.json")
    md_path = os.path.join(args.output_dir, f"{slug}.test_coverage.md")
    
    # Save
    save_json(json_path, result)
    save_markdown(md_path, generate_report(result))
    
    print(f"Processed {slug} -> {json_path}")

if __name__ == "__main__":
    main()
