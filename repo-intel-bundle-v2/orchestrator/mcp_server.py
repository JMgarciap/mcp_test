import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import inspect
from orchestrator.tool_registry import registry

# Import tools module to force registration
import orchestrator.mcp_tools
import orchestrator.mcp_audit_tools

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCPServer")

app = FastAPI(title="Repo Intel CP Server", version="1.0.0")

class ToolExecutionRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]

class ToolExecutionResponse(BaseModel):
    content: List[Dict[str, Any]]
    isError: bool = False

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "repo-intel-bundle-v2"}

@app.get("/mcp/tools")
async def list_tools():
    """
    List all available tools in MCP format.
    """
    tools = registry.list_tools()
    return {
        "tools": [t.dict() for t in tools]
    }

@app.post("/mcp/invoke", response_model=ToolExecutionResponse)
async def invoke_tool(request: ToolExecutionRequest):
    """
    Execute a tool by name with provided arguments.
    """
    tool = registry.get_tool(request.name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{request.name}' not found.")
    
    func = tool["func"]
    try:
        logger.info(f"Executing tool: {request.name} with args: {request.arguments}")
        
        # Execute the function (support async if needed, currently sync for simplicity)
        if hasattr(func, '__code__') and inspect.iscoroutinefunction(func):
            result = await func(**request.arguments)
        else:
            result = func(**request.arguments)
            
        return ToolExecutionResponse(
            content=[{
                "type": "text",
                "text": str(result)
            }]
        )
    except Exception as e:
        logger.error(f"Error executing tool {request.name}: {e}")
        return ToolExecutionResponse(
            content=[{
                "type": "text",
                "text": f"Error: {str(e)}"
            }],
            isError=True
        )

# Protocol Handling (SSE for Copilot)
# Copilot often uses SSE for tool discovery and execution updates.
# For simplicity, we are using standard HTTP endpoints which are compatible with 
# many MCP clients, but strict MCP compliance might require /sse endpoint.
# We will stick to the basic invoke/list pattern for now as per requirements.

if __name__ == "__main__":
    import uvicorn
    # Inspect is already imported at the top if we fix it, but let's make sure
    uvicorn.run(app, host="0.0.0.0", port=3333)
