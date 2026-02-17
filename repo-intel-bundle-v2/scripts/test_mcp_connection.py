import requests
import json
import sys

BASE_URL = "http://localhost:3333"

def test_health():
    print("🏥 Testing Health Endpoint...")
    try:
        resp = requests.get(f"{BASE_URL}/health")
        resp.raise_for_status()
        print(f"✅ Health OK: {resp.json()}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        sys.exit(1)

def test_list_tools():
    print("\n🛠️  Testing List Tools Endpoint...")
    try:
        resp = requests.get(f"{BASE_URL}/mcp/tools")
        resp.raise_for_status()
        tools = resp.json().get("tools", [])
        print(f"✅ Found {len(tools)} tools:")
        for t in tools:
            print(f"  - {t['name']}: {t['description']}")
            
        if not tools:
             print("⚠️  No tools found! Registration might be broken.")
             sys.exit(1)
             
    except Exception as e:
        print(f"❌ List Tools Failed: {e}")
        sys.exit(1)

def main():
    test_health()
    test_list_tools()
    print("\n🎉 MCP Server Connection Verified!")

if __name__ == "__main__":
    main()
