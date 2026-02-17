import subprocess
import json
import sys
import os

def test_stdio_server():
    print("🚀 Starting STDIO Server Test...")
    
    # Start the server process
    process = subprocess.Popen(
        [sys.executable, "-m", "orchestrator.server_stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
        text=True,
        bufsize=0 # Unbuffered
    )

    try:
        # 1. Initialize
        print("\n1️⃣  Sending 'initialize'...")
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0"}
            }
        }
        process.stdin.write(json.dumps(init_req) + "\n")
        process.stdin.flush()
        
        response = json.loads(process.stdout.readline())
        print(f"✅ Init Response: {response}")
        assert response["result"]["serverInfo"]["name"] == "repo-intel-stdio"

        # 2. List Tools
        print("\n2️⃣  Sending 'tools/list'...")
        list_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        process.stdin.write(json.dumps(list_req) + "\n")
        process.stdin.flush()
        
        response = json.loads(process.stdout.readline())
        tools = response["result"]["tools"]
        print(f"✅ Found {len(tools)} tools.")
        tool_names = [t["name"] for t in tools]
        print(f"   Tools: {tool_names}")
        assert "audit.run" in tool_names
        
        # 3. Ping
        print("\n3️⃣  Sending 'ping'...")
        ping_req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "ping"
        }
        process.stdin.write(json.dumps(ping_req) + "\n")
        process.stdin.flush()
        response = json.loads(process.stdout.readline())
        print(f"✅ Ping Response: {response}")

        print("\n🎉 STDIO Server Verification Passed!")

    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
    finally:
        process.terminate()

if __name__ == "__main__":
    test_stdio_server()
