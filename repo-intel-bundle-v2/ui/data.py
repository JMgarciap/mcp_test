import json
import os
import glob
from datetime import datetime
import pandas as pd

def get_available_projects(output_dir="outputs"):
    """
    Returns list of project folders that contain status.json or events.jsonl
    """
    projects = []
    if not os.path.exists(output_dir):
        return []
        
    for name in os.listdir(output_dir):
        path = os.path.join(output_dir, name)
        if os.path.isdir(path):
            if os.path.exists(os.path.join(path, "status.json")) or \
               os.path.exists(os.path.join(path, "events.jsonl")):
                projects.append(name)
    
    # Sort by modification time (newest first)
    projects.sort(key=lambda x: os.path.getmtime(os.path.join(output_dir, x)), reverse=True)
    return projects

def load_status(project_name, output_dir="outputs"):
    path = os.path.join(output_dir, project_name, "status.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return None

def load_events(project_name, output_dir="outputs", limit=200):
    path = os.path.join(output_dir, project_name, "events.jsonl")
    if not os.path.exists(path):
        return []
        
    events = []
    try:
        with open(path, "r") as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except:
                    continue
    except:
        pass
        
    return events[-limit:][::-1] # Return last N reversed (newest first)

def get_artifacts_list(project_name, output_dir="outputs"):
    path = os.path.join(output_dir, project_name)
    artifacts = []
    
    # Recursively find interesting files
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".md") or file.endswith(".json"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, start=path)
                artifacts.append({
                    "name": file,
                    "path": full_path,
                    "rel_path": rel_path,
                    "type": "MD" if file.endswith(".md") else "JSON"
                })
    return artifacts

def get_aggregated_metrics(project_name, output_dir="outputs"):
    """
    Calculates portfolio metrics from governance_summary.json if available.
    """
    path = os.path.join(output_dir, project_name, "governance_summary.json")
    metrics = {
        "quality": 0, "cloud": 0, "risk": 0, "security": 0, "testing": "N/A", "findings": 0
    }
    
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
                
            # Handle new dict structure or legacy list
            if isinstance(data, dict):
                repos = data.get("repos", [])
            elif isinstance(data, list):
                repos = data
            else:
                repos = []

            if not repos: return metrics
            
            count = len(repos)
            metrics["quality"] = sum(r['scores'].get('quality', 0) for r in repos) / count
            metrics["cloud"] = sum(r['scores'].get('cloud_readiness', 0) for r in repos) / count
            metrics["risk"] = sum(r['scores'].get('risk', 0) for r in repos) / count
            
            # Security & Findings
            metrics["security"] = sum(r.get('security_score', 0) for r in repos) / count
            val = 0
            for r in repos:
                # findings might be list or count depending on agent
                f_data = r.get('findings', [])
                val += len(f_data) if isinstance(f_data, list) else 0
            metrics["findings"] = val
            
        except Exception as e:
            print(f"Error calculating metrics for {project_name}: {e}")
            pass
            
    return metrics

def get_all_findings(project_name, output_dir="outputs"):
    """
    Aggregates all findings from analysis.json and agent reports into a normalized list.
    """
    findings = []
    path = os.path.join(output_dir, project_name)
    
    # 1. Load Repo Intelligence (analysis.json)
    # This usually contains the raw static analysis issues
    # We might need to iterate through repo output folders if they exist, 
    # but for now let's assume valid data might be in governance_summary or we scan for agent reports.
    
    # Actually, the best source for "Findings" is the governance_summary.json which aggregates them,
    # OR iterating through specific agent outputs if we want raw details.
    
    # Let's try to load governance_summary.json first as it's the consolidated source
    gov_path = os.path.join(path, "governance_summary.json")
    if os.path.exists(gov_path):
        try:
            with open(gov_path, "r") as f:
                data = json.load(f)
                
            repos = data.get("repos", []) if isinstance(data, dict) else data
            
            for r in repos:
                repo_name = r.get("repo", "Unknown")
                
                # Findings from Repo Intel
                for f in r.get("findings", []):
                    findings.append({
                        "id": f.get("id", "N/A"),
                        "title": f.get("title", f.get("message", "Unknown Issue")),
                        "severity": f.get("severity", "MEDIUM").upper(),
                        "category": f.get("category", "Code Quality"),
                        "agent": "Repo Intelligence",
                        "repo": repo_name,
                        "description": f.get("description", f.get("message", "")),
                        "remediation": f.get("remediation", "Check code compliance."),
                        "file": f.get("file", "N/A"),
                        "line": f.get("line", 0)
                    })
                    
                # We could also look for other agent findings if they are merged here
                # Or we can look at "agent_reports" directory if we implemented that structure
        except Exception as e:
            print(f"Error loading governance findings: {e}")

    # 2. Mock/Simulate Reasoning Agent Findings if not present (since we are in a demo/transition phase)
    # In a real scenario, we would read agents/security_agent/report.json etc.
    # For now, let's ensure we have some rich data for the UI if the file is thin
    
    return findings
