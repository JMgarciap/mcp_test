import uvicorn
import os
import sys

# Ensure we can import from src/orchestrator
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

from orchestrator.mcp_server import app

def main():
    print("🚀 Starting Enterprise MCP Server on port 3333...")
    uvicorn.run(app, host="0.0.0.0", port=3333)

if __name__ == "__main__":
    main()
