import sys
import json
import logging
import os
import traceback
from typing import Dict, Any, Optional

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Ensure we can import from src/orchestrator if run directly
sys.path.append(os.getcwd())

# Import Tool Registry and Tools to force registration
from orchestrator.tool_registry import registry
import orchestrator.mcp_tools
import orchestrator.mcp_audit_tools

# Configure logging to stderr to avoid corrupting stdout JSON-RPC
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp-stdio")

def send_json_rpc(message: Dict[str, Any]):
    """Send a JSON-RPC message to stdout."""
    json.dump(message, sys.stdout)
    sys.stdout.write("\n")
    sys.stdout.flush()

def handle_initialize(request: Dict[str, Any]):
    """Handle the initialize request."""
    # MCP Protocol: Return server capabilities
    response = {
        "jsonrpc": "2.0",
        "id": request["id"],
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": True
                }
            },
            "serverInfo": {
                "name": "repo-intel-stdio",
                "version": "1.0.0"
            }
        }
    }
    send_json_rpc(response)

def handle_list_tools(request: Dict[str, Any]):
    """Handle tools/list request."""
    tools = []
    # registry.list_tools() returns List[ToolMetadata]
    for tool_meta in registry.list_tools():
        tools.append({
            "name": tool_meta.name,
            "description": tool_meta.description,
            "inputSchema": tool_meta.parameters
        })
    
    response = {
        "jsonrpc": "2.0",
        "id": request["id"],
        "result": {
            "tools": tools
        }
    }
    send_json_rpc(response)

def handle_call_tool(request: Dict[str, Any]):
    """Handle tools/call request."""
    params = request.get("params", {})
    name = params.get("name")
    args = params.get("arguments", {})
    
    logger.info(f"🔧 Invoking tool: {name} with args: {args}")
    
    try:
        tool_entry = registry.get_tool(name)
        if not tool_entry:
            raise ValueError(f"Tool not found: {name}")
            
        # Execute the tool
        # registry.get_tool returns {"func": ..., "metadata": ...}
        func = tool_entry["func"]
        result = func(**args)
        
        # Format for MCP
        content = []
        if isinstance(result, str):
            content.append({"type": "text", "text": result})
        else:
            content.append({"type": "text", "text": json.dumps(result, default=str)})
            
        response = {
            "jsonrpc": "2.0",
            "id": request["id"],
            "result": {
                "content": content,
                "isError": False
            }
        }
    except Exception as e:
        logger.error(f"❌ Tool execution failed: {e}")
        logger.error(traceback.format_exc())
        response = {
            "jsonrpc": "2.0",
            "id": request["id"],
            "result": {
                "content": [{"type": "text", "text": str(e)}],
                "isError": True
            }
        }
    
    send_json_rpc(response)

def handle_ping(request: Dict[str, Any]):
    """Handle ping request."""
    response = {
        "jsonrpc": "2.0",
        "id": request["id"],
        "result": {}
    }
    send_json_rpc(response)

def main():
    logger.info("🚀 STDIO MCP Server Started")
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            line = line.strip()
            if not line:
                continue
                
            request = json.loads(line)
            method = request.get("method")
            
            if method == "initialize":
                handle_initialize(request)
            elif method == "notifications/initialized":
                # client acknowledging initialization
                pass 
            elif method == "ping":
                handle_ping(request)
            elif method == "tools/list":
                handle_list_tools(request)
            elif method == "tools/call":
                handle_call_tool(request)
            else:
                logger.warning(f"Unknown method: {method}")
                
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON")
        except Exception as e:
            logger.error(f"Server error: {e}")
            logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
