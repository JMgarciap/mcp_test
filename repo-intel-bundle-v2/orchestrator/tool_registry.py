import inspect
from typing import Callable, Dict, Any, List, Optional
from pydantic import BaseModel

class ToolMetadata(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class ToolRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
            cls._instance.tools = {}
        return cls._instance

    def register(self, name: str, description: str):
        """
        Decorator to register a function as an MCP tool.
        """
        def decorator(func: Callable):
            # Extract parameters from function signature
            sig = inspect.signature(func)
            params = {
                "type": "object",
                "properties": {},
                "required": []
            }
            
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue
                    
                param_type = "string" # Default to string
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == dict:    
                    param_type = "object"
                elif param.annotation == list:
                    param_type = "array"
                    
                params["properties"][param_name] = {
                    "type": param_type,
                    "description": f"Parameter {param_name}"
                }
                
                if param.default == inspect.Parameter.empty:
                    params["required"].append(param_name)

            tool_metadata = ToolMetadata(
                name=name,
                description=description,
                parameters=params
            )
            
            self.tools[name] = {
                "func": func,
                "metadata": tool_metadata
            }
            return func
        return decorator

    def get_tool(self, name: str) -> Optional[Dict]:
        return self.tools.get(name)

    def list_tools(self) -> List[ToolMetadata]:
        return [t["metadata"] for t in self.tools.values()]
        
# Global Registry Instance
registry = ToolRegistry()
