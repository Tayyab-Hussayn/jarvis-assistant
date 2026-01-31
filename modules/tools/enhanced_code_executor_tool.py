#!/usr/bin/env python3
"""
Enhanced Code Execution Tool - Multi-language Docker execution
"""

import sys
sys.path.append('/home/krawin/exp.code/jarvis')

from modules.tools.base_tool import BaseTool, ToolResult, ToolStatus, tool_registry
from core.execution.docker_executor import DockerCodeExecutor, ExecutionConfig
import asyncio

class EnhancedCodeExecutorTool(BaseTool):
    """Enhanced tool for multi-language code execution"""
    
    def __init__(self):
        super().__init__(name="enhanced_code_executor")
        self.description = "Execute code in multiple languages with Docker isolation"
        self.executor = DockerCodeExecutor()
        self.initialized = False
    
    def validate_input(self, code: str, language: str = "python", **kwargs) -> bool:
        """Validate code execution parameters"""
        
        if not code or not isinstance(code, str):
            self.logger.error("Code parameter is required and must be a string")
            return False
        
        supported_languages = ["python", "javascript", "bash", "go", "rust"]
        if language not in supported_languages:
            self.logger.error(f"Language {language} not supported. Supported: {supported_languages}")
            return False
        
        # Basic security checks
        if language == "bash":
            dangerous_commands = ['rm -rf', 'sudo', 'format', 'mkfs', 'dd if=']
            if any(danger in code.lower() for danger in dangerous_commands):
                self.logger.error("Dangerous bash command detected")
                return False
        
        return True
    
    async def execute(self, code: str, language: str = "python", 
                     timeout: int = 30, memory_limit: str = "128m", 
                     **kwargs) -> ToolResult:
        """Execute code with enhanced security and isolation"""
        
        try:
            # Initialize executor if needed
            if not self.initialized:
                await self.executor.initialize()
                self.initialized = True
            
            # Create execution config
            config = ExecutionConfig(
                language=language,
                timeout=timeout,
                memory_limit=memory_limit,
                cpu_limit=kwargs.get("cpu_limit", "0.5"),
                network_disabled=kwargs.get("network_disabled", True),
                read_only=kwargs.get("read_only", True),
                max_output_size=kwargs.get("max_output_size", 10000)
            )
            
            # Execute code
            result = await self.executor.execute_code(code, config)
            
            # Format result
            output_data = {
                "language": result.language,
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "execution_time": round(result.execution_time, 3),
                "exit_code": result.exit_code,
                "docker_used": self.executor.docker_available
            }
            
            if result.success:
                return ToolResult(
                    success=True,
                    output=output_data,
                    status=ToolStatus.SUCCESS
                )
            else:
                return ToolResult(
                    success=False,
                    output=output_data,
                    error_message=result.error or f"Code execution failed with exit code {result.exit_code}",
                    status=ToolStatus.FAILURE
                )
        
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Code execution error: {str(e)}",
                status=ToolStatus.FAILURE
            )

# Register the enhanced tool
tool_registry.register_tool(EnhancedCodeExecutorTool())
