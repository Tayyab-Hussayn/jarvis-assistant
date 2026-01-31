"""
Terminal Executor Tool - Safe command execution with guards
"""

import os
import subprocess
import asyncio
from typing import List, Dict
from modules.tools.base_tool import BaseTool, ToolResult, ToolStatus

class TerminalExecutor(BaseTool):
    """Execute terminal commands with safety guards"""
    
    # Command blacklist for safety
    BLACKLIST = [
        "rm -rf /",
        ":(){ :|:& };:",  # Fork bomb
        "dd if=/dev/random of=/dev/sda",
        "chmod -R 777 /",
        "mkfs",
        "fdisk",
        "parted",
        "format",
        "del /f /s /q C:\\",
        "shutdown",
        "reboot",
        "halt"
    ]
    
    # Allowed directories
    WHITELIST_DIRS = [
        "/home/krawin/exp.code/jarvis",
        "/tmp/jarvis_workspace",
        "/var/tmp/jarvis"
    ]
    
    def __init__(self):
        super().__init__("terminal_executor")
        self.max_execution_time = 300  # 5 minutes
        
    def validate_input(self, command: str, **kwargs) -> bool:
        """Validate command safety"""
        # Check blacklist
        for blocked_cmd in self.BLACKLIST:
            if blocked_cmd in command.lower():
                self.logger.warning(f"Blocked dangerous command: {command}")
                return False
        
        # Check for suspicious patterns
        suspicious_patterns = ["sudo rm", "rm -rf", "> /dev/", "dd if=", "mkfs"]
        for pattern in suspicious_patterns:
            if pattern in command.lower():
                self.logger.warning(f"Blocked suspicious command: {command}")
                return False
        
        return True
    
    async def execute(self, command: str, working_dir: str = None, timeout: int = None) -> ToolResult:
        """Execute terminal command safely"""
        
        # Set working directory
        if working_dir is None:
            working_dir = "/home/krawin/exp.code/jarvis"
        
        # Validate working directory
        if not any(working_dir.startswith(allowed) for allowed in self.WHITELIST_DIRS):
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Working directory not in whitelist: {working_dir}",
                status=ToolStatus.FAILURE
            )
        
        # Set timeout
        if timeout is None:
            timeout = self.max_execution_time
        
        try:
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
                
                return_code = process.returncode
                
                result = ToolResult(
                    success=return_code == 0,
                    output={
                        "stdout": stdout.decode('utf-8', errors='ignore'),
                        "stderr": stderr.decode('utf-8', errors='ignore'),
                        "return_code": return_code
                    },
                    status=ToolStatus.SUCCESS if return_code == 0 else ToolStatus.FAILURE,
                    metadata={
                        "command": command,
                        "working_dir": working_dir,
                        "timeout": timeout
                    }
                )
                
                if return_code != 0:
                    result.error_message = f"Command failed with return code {return_code}"
                
                return result
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ToolResult(
                    success=False,
                    output=None,
                    error_message=f"Command timed out after {timeout} seconds",
                    status=ToolStatus.FAILURE
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Execution error: {str(e)}",
                status=ToolStatus.FAILURE
            )
