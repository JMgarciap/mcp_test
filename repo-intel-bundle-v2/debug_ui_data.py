import sys
import os
import json

# Add current dir to path so we can import ui modules
sys.path.append(os.getcwd())

from ui.data import load_status, get_aggregated_metrics
from ui.agent_registry import AGENTS

project = "jmgp_audit"
print(f"--- Debugging Project: {project} ---")

# 1. Test load_status
print("\n[1] Testing load_status...")
status = load_status(project)
if status:
    print("✅ Status loaded successfully")
    print(f"Keys: {list(status.keys())}")
    print(f"Stages: {list(status.get('stages', {}).keys())}")
    
    # Check if all agents have their stages in status
    print("\nChecking Agent Stages vs Status:")
    for agent in AGENTS:
        missing = []
        for stage in agent['stages']:
            if stage not in status['stages']:
                missing.append(stage)
        if missing:
            print(f"❌ Agent {agent['id']} missing stages in status: {missing}")
        else:
            print(f"✅ Agent {agent['id']} stages found.")
else:
    print("❌ Failed to load status")

# 2. Test get_aggregated_metrics
print("\n[2] Testing get_aggregated_metrics...")
metrics = get_aggregated_metrics(project)
print(f"Metrics: {metrics}")

# 3. Check governance_summary.json directly
gov_path = f"outputs/{project}/governance_summary.json"
if os.path.exists(gov_path):
    print(f"\n[3] Found {gov_path}")
    with open(gov_path, 'r') as f:
        data = json.load(f)
        print(f"Type: {type(data)}")
        if isinstance(data, dict):
            print(f"Keys: {list(data.keys())}")
            if "repos" in data:
                print(f"Repos count: {len(data['repos'])}")
else:
    print(f"\n❌ {gov_path} NOT FOUND")
