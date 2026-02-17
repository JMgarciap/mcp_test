import requests
import json
import time

URL = "http://localhost:3333/mcp/invoke"

def run_test():
    print("🚀 Testing MCP Audit Tools...")
    
    # 1. audit.run
    print("\n1️⃣  Running audit.run...")
    payload_run = {
        "name": "audit.run",
        "arguments": {
            "project_name": "mcp_test_project",
            "repos": ["https://github.com/pallets/flask"],
            "workflow_path": "examples/custom_workflow.md"
        }
    }
    
    try:
        res = requests.post(URL, json=payload_run)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
    except Exception as e:
        print(f"Failed: {e}")
        return

    # 2. audit.index
    print("\n2️⃣  Running audit.index...")
    payload_index = {
        "name": "audit.index",
        "arguments": {
            "project_name": "mcp_test_project"
        }
    }
    res = requests.post(URL, json=payload_index)
    print(f"Response: {res.json()}")

    # 3. audit.context_pack
    print("\n3️⃣  Running audit.context_pack...")
    payload_context = {
        "name": "audit.context_pack",
        "arguments": {
            "project_name": "mcp_test_project",
            "max_chars": 5000
        }
    }
    res = requests.post(URL, json=payload_context)
    print(f"Response: {res.json()}")

if __name__ == "__main__":
    time.sleep(2) # Wait for server
    run_test()
