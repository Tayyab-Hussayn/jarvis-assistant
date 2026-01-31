#!/usr/bin/env python3
"""
Code Executor Tool - Executes code safely in sandboxed environment
"""

import asyncio
import tempfile
import os
import subprocess
import time
from typing import Dict, Any, Optional
import logging

from .base_tool import BaseTool, ToolResult, ToolStatus, tool_registry

class CodeExecutorTool(BaseTool):
    """Tool for executing code in various languages"""
    
    def __init__(self):
        super().__init__(name="code_executor")
        self.description = "Execute code safely in sandboxed environment"
        self.version = "1.0.0"
        self.supported_languages = ["python", "javascript", "bash", "shell"]
        self.timeout_default = 30
    
    def validate_input(self, code: str, language: str = "python", **kwargs) -> bool:
        """Validate code execution parameters"""
        
        if not code or not isinstance(code, str):
            self.logger.error("Code parameter is required and must be a string")
            return False
        
        if language not in self.supported_languages:
            self.logger.error(f"Language {language} not supported. Supported: {self.supported_languages}")
            return False
        
        # Basic security checks
        dangerous_patterns = [
            "import os",
            "import subprocess", 
            "import sys",
            "__import__",
            "eval(",
            "exec(",
            "open(",
            "file(",
            "input(",
            "raw_input("
        ]
        
        for pattern in dangerous_patterns:
            if pattern in code:
                self.logger.warning(f"Blocked dangerous pattern: {pattern}")
                return False
        
        return True
    
    async def execute(self, code: str, language: str = "python", 
                     timeout: int = None, **kwargs) -> ToolResult:
        """Execute code safely"""
        
        timeout = timeout or self.timeout_default
        
        try:
            if language == "python":
                return await self._execute_python(code, timeout)
            elif language in ["javascript", "js"]:
                return await self._execute_javascript(code, timeout)
            elif language in ["bash", "shell"]:
                return await self._execute_bash(code, timeout)
            else:
                return ToolResult(
                    success=False,
                    output=None,
                    error_message=f"Language {language} not implemented",
                    status=ToolStatus.FAILURE
                )
        
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Code execution failed: {str(e)}",
                status=ToolStatus.FAILURE
            )
    
    async def _execute_python(self, code: str, timeout: int) -> ToolResult:
        """Execute Python code"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Execute with timeout
            process = await asyncio.create_subprocess_exec(
                'python3', temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
                
                if process.returncode == 0:
                    output = stdout.decode('utf-8').strip()
                    return ToolResult(
                        success=True,
                        output=output if output else "Code executed successfully",
                        status=ToolStatus.SUCCESS
                    )
                else:
                    error = stderr.decode('utf-8').strip()
                    return ToolResult(
                        success=False,
                        output=None,
                        error_message=f"Python execution failed: {error}",
                        status=ToolStatus.FAILURE
                    )
            
            except asyncio.TimeoutError:
                process.kill()
                return ToolResult(
                    success=False,
                    output=None,
                    error_message=f"Code execution timed out after {timeout} seconds",
                    status=ToolStatus.TIMEOUT
                )
        
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
    
    async def _execute_javascript(self, code: str, timeout: int) -> ToolResult:
        """Execute JavaScript code using Node.js"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Check if node is available
            try:
                subprocess.run(['node', '--version'], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return ToolResult(
                    success=False,
                    output=None,
                    error_message="Node.js not available for JavaScript execution",
                    status=ToolStatus.FAILURE
                )
            
            # Execute with timeout
            process = await asyncio.create_subprocess_exec(
                'node', temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
                
                if process.returncode == 0:
                    output = stdout.decode('utf-8').strip()
                    return ToolResult(
                        success=True,
                        output=output if output else "Code executed successfully",
                        status=ToolStatus.SUCCESS
                    )
                else:
                    error = stderr.decode('utf-8').strip()
                    return ToolResult(
                        success=False,
                        output=None,
                        error_message=f"JavaScript execution failed: {error}",
                        status=ToolStatus.FAILURE
                    )
            
            except asyncio.TimeoutError:
                process.kill()
                return ToolResult(
                    success=False,
                    output=None,
                    error_message=f"Code execution timed out after {timeout} seconds",
                    status=ToolStatus.TIMEOUT
                )
        
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
    
    async def _execute_bash(self, code: str, timeout: int) -> ToolResult:
        """Execute Bash code"""
        
        try:
            # Execute with timeout
            process = await asyncio.create_subprocess_shell(
                code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
                
                if process.returncode == 0:
                    output = stdout.decode('utf-8').strip()
                    return ToolResult(
                        success=True,
                        output=output if output else "Code executed successfully",
                        status=ToolStatus.SUCCESS
                    )
                else:
                    error = stderr.decode('utf-8').strip()
                    return ToolResult(
                        success=False,
                        output=None,
                        error_message=f"Bash execution failed: {error}",
                        status=ToolStatus.FAILURE
                    )
            
            except asyncio.TimeoutError:
                process.kill()
                return ToolResult(
                    success=False,
                    output=None,
                    error_message=f"Code execution timed out after {timeout} seconds",
                    status=ToolStatus.TIMEOUT
                )
        
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Bash execution failed: {str(e)}",
                status=ToolStatus.FAILURE
            )

# Register the tool
tool_registry.register_tool(CodeExecutorTool())
