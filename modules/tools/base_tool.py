"""
JARVIS Tool Framework - Base classes and registry for all tools
"""

import json
import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class ToolStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"

@dataclass
class ToolResult:
    success: bool
    output: Any
    error_message: str = ""
    execution_time: float = 0.0
    confidence: float = 1.0
    status: ToolStatus = ToolStatus.SUCCESS
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class BaseTool(ABC):
    """Abstract base class for all tools"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"tool.{name}")
        self.execution_count = 0
        self.success_count = 0
        
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters"""
        pass
    
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters - override in subclasses"""
        return True
    
    async def safe_execute(self, **kwargs) -> ToolResult:
        """Execute with error handling and logging"""
        start_time = time.time()
        self.execution_count += 1
        
        try:
            # Validate inputs
            if not self.validate_input(**kwargs):
                return ToolResult(
                    success=False,
                    output=None,
                    error_message="Input validation failed",
                    execution_time=time.time() - start_time,
                    status=ToolStatus.FAILURE
                )
            
            # Execute tool
            result = await self.execute(**kwargs)
            result.execution_time = time.time() - start_time
            
            if result.success:
                self.success_count += 1
                
            self.logger.info(f"Tool {self.name} executed: success={result.success}, time={result.execution_time:.2f}s")
            return result
            
        except Exception as e:
            error_result = ToolResult(
                success=False,
                output=None,
                error_message=str(e),
                execution_time=time.time() - start_time,
                status=ToolStatus.FAILURE
            )
            self.logger.error(f"Tool {self.name} failed: {e}")
            return error_result
    
    def get_stats(self) -> Dict:
        """Get tool execution statistics"""
        success_rate = (self.success_count / self.execution_count) if self.execution_count > 0 else 0.0
        return {
            "name": self.name,
            "executions": self.execution_count,
            "successes": self.success_count,
            "success_rate": success_rate
        }

class ToolRegistry:
    """Registry for managing all available tools"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.logger = logging.getLogger("tool_registry")
    
    def register_tool(self, tool: BaseTool):
        """Register a tool"""
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all available tools"""
        return list(self.tools.keys())
    
    async def execute_tool(self, name: str, **kwargs) -> ToolResult:
        """Execute a tool by name"""
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Tool '{name}' not found",
                status=ToolStatus.FAILURE
            )
        
        return await tool.safe_execute(**kwargs)
    
    def get_all_stats(self) -> Dict:
        """Get statistics for all tools"""
        return {name: tool.get_stats() for name, tool in self.tools.items()}

# Global tool registry
tool_registry = ToolRegistry()
