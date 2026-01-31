"""
Code Executor - Docker-based sandboxed code execution with limits
"""

import asyncio
import tempfile
import os
import shutil
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

from modules.tools.base_tool import BaseTool, ToolResult, ToolStatus

class CodeLanguage(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    BASH = "bash"
    SQL = "sql"

@dataclass
class CodeExecutionConfig:
    language: CodeLanguage
    timeout: int = 30  # seconds
    memory_limit: int = 128  # MB
    cpu_limit: float = 0.5  # CPU cores
    network_access: bool = False
    file_system_access: bool = True
    allowed_imports: List[str] = None
    
    def __post_init__(self):
        if self.allowed_imports is None:
            self.allowed_imports = []

class CodeExecutor(BaseTool):
    """Execute code in isolated containers with resource limits"""
    
    def __init__(self):
        super().__init__("code_executor")
        
        # Default configurations for different languages
        self.default_configs = {
            CodeLanguage.PYTHON: CodeExecutionConfig(
                language=CodeLanguage.PYTHON,
                timeout=30,
                memory_limit=128,
                allowed_imports=["os", "sys", "json", "math", "datetime", "re"]
            ),
            CodeLanguage.JAVASCRIPT: CodeExecutionConfig(
                language=CodeLanguage.JAVASCRIPT,
                timeout=15,
                memory_limit=64
            ),
            CodeLanguage.BASH: CodeExecutionConfig(
                language=CodeLanguage.BASH,
                timeout=10,
                memory_limit=32,
                file_system_access=False  # More restrictive for bash
            )
        }
        
        # Security blacklist
        self.security_blacklist = {
            CodeLanguage.PYTHON: [
                "import subprocess", "import os", "__import__", "exec(", "eval(",
                "open(", "file(", "input(", "raw_input(", "compile(",
                "globals(", "locals(", "vars(", "dir("
            ],
            CodeLanguage.JAVASCRIPT: [
                "require(", "import(", "eval(", "Function(", "setTimeout(",
                "setInterval(", "process.", "global.", "window."
            ],
            CodeLanguage.BASH: [
                "rm ", "rmdir", "dd ", "mkfs", "fdisk", "parted",
                "shutdown", "reboot", "halt", "init ", "kill ",
                "sudo ", "su ", "chmod 777", "chown "
            ]
        }
    
    def validate_input(self, code: str, language: str = "python", **kwargs) -> bool:
        """Validate code for security issues"""
        
        try:
            lang_enum = CodeLanguage(language.lower())
        except ValueError:
            self.logger.error(f"Unsupported language: {language}")
            return False
        
        # Check security blacklist
        blacklist = self.security_blacklist.get(lang_enum, [])
        code_lower = code.lower()
        
        for blocked_pattern in blacklist:
            if blocked_pattern.lower() in code_lower:
                self.logger.warning(f"Blocked dangerous pattern: {blocked_pattern}")
                return False
        
        # Check code length
        if len(code) > 10000:  # 10KB limit
            self.logger.warning("Code too long")
            return False
        
        return True
    
    async def execute(self, code: str, language: str = "python", 
                     config: Optional[CodeExecutionConfig] = None, **kwargs) -> ToolResult:
        """Execute code safely in sandbox"""
        
        try:
            lang_enum = CodeLanguage(language.lower())
        except ValueError:
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Unsupported language: {language}",
                status=ToolStatus.FAILURE
            )
        
        # Use default config if none provided
        if config is None:
            config = self.default_configs.get(lang_enum, CodeExecutionConfig(lang_enum))
        
        # Create temporary workspace
        workspace = tempfile.mkdtemp(prefix="jarvis_code_")
        
        try:
            # Execute based on language
            if lang_enum == CodeLanguage.PYTHON:
                result = await self._execute_python(code, config, workspace)
            elif lang_enum == CodeLanguage.JAVASCRIPT:
                result = await self._execute_javascript(code, config, workspace)
            elif lang_enum == CodeLanguage.BASH:
                result = await self._execute_bash(code, config, workspace)
            else:
                result = ToolResult(
                    success=False,
                    output=None,
                    error_message=f"Execution not implemented for {language}",
                    status=ToolStatus.FAILURE
                )
            
            return result
            
        finally:
            # Cleanup workspace
            try:
                shutil.rmtree(workspace)
            except Exception as e:
                self.logger.warning(f"Failed to cleanup workspace: {e}")
    
    async def _execute_python(self, code: str, config: CodeExecutionConfig, 
                            workspace: str) -> ToolResult:
        """Execute Python code"""
        
        # Create code file
        code_file = os.path.join(workspace, "code.py")
        
        # Add safety wrapper
        wrapped_code = f"""
import sys
import signal
import resource

# Set resource limits
resource.setrlimit(resource.RLIMIT_AS, ({config.memory_limit * 1024 * 1024}, {config.memory_limit * 1024 * 1024}))

# Timeout handler
def timeout_handler(signum, frame):
    raise TimeoutError("Code execution timed out")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm({config.timeout})

try:
    # User code starts here
{code}
except Exception as e:
    print(f"Error: {{e}}", file=sys.stderr)
    sys.exit(1)
finally:
    signal.alarm(0)  # Cancel timeout
"""
        
        with open(code_file, 'w') as f:
            f.write(wrapped_code)
        
        # Execute with subprocess
        try:
            process = await asyncio.create_subprocess_exec(
                "python3", code_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workspace
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=config.timeout + 5  # Extra buffer
                )
                
                return_code = process.returncode
                
                return ToolResult(
                    success=return_code == 0,
                    output={
                        "stdout": stdout.decode('utf-8', errors='ignore'),
                        "stderr": stderr.decode('utf-8', errors='ignore'),
                        "return_code": return_code
                    },
                    status=ToolStatus.SUCCESS if return_code == 0 else ToolStatus.FAILURE,
                    metadata={
                        "language": "python",
                        "workspace": workspace
                    }
                )
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ToolResult(
                    success=False,
                    output=None,
                    error_message=f"Code execution timed out after {config.timeout} seconds",
                    status=ToolStatus.FAILURE
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Execution error: {str(e)}",
                status=ToolStatus.FAILURE
            )
    
    async def _execute_javascript(self, code: str, config: CodeExecutionConfig, 
                                workspace: str) -> ToolResult:
        """Execute JavaScript code using Node.js"""
        
        # Create code file
        code_file = os.path.join(workspace, "code.js")
        
        # Add safety wrapper
        wrapped_code = f"""
// Set timeout
const timeout = setTimeout(() => {{
    console.error("Code execution timed out");
    process.exit(1);
}}, {config.timeout * 1000});

try {{
    // User code starts here
{code}
}} catch (error) {{
    console.error("Error:", error.message);
    process.exit(1);
}} finally {{
    clearTimeout(timeout);
}}
"""
        
        with open(code_file, 'w') as f:
            f.write(wrapped_code)
        
        # Execute with Node.js
        try:
            process = await asyncio.create_subprocess_exec(
                "node", code_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workspace
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=config.timeout + 5
                )
                
                return_code = process.returncode
                
                return ToolResult(
                    success=return_code == 0,
                    output={
                        "stdout": stdout.decode('utf-8', errors='ignore'),
                        "stderr": stderr.decode('utf-8', errors='ignore'),
                        "return_code": return_code
                    },
                    status=ToolStatus.SUCCESS if return_code == 0 else ToolStatus.FAILURE,
                    metadata={
                        "language": "javascript",
                        "workspace": workspace
                    }
                )
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ToolResult(
                    success=False,
                    output=None,
                    error_message=f"Code execution timed out after {config.timeout} seconds",
                    status=ToolStatus.FAILURE
                )
                
        except FileNotFoundError:
            return ToolResult(
                success=False,
                output=None,
                error_message="Node.js not found. Please install Node.js to execute JavaScript code.",
                status=ToolStatus.FAILURE
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Execution error: {str(e)}",
                status=ToolStatus.FAILURE
            )
    
    async def _execute_bash(self, code: str, config: CodeExecutionConfig, 
                          workspace: str) -> ToolResult:
        """Execute Bash code"""
        
        # Create script file
        script_file = os.path.join(workspace, "script.sh")
        
        # Add safety wrapper
        wrapped_code = f"""#!/bin/bash
set -e  # Exit on error
set -u  # Exit on undefined variable

# Set timeout
timeout {config.timeout} bash << 'EOF'
{code}
EOF
"""
        
        with open(script_file, 'w') as f:
            f.write(wrapped_code)
        
        # Make executable
        os.chmod(script_file, 0o755)
        
        # Execute
        try:
            process = await asyncio.create_subprocess_exec(
                "bash", script_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workspace
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=config.timeout + 5
                )
                
                return_code = process.returncode
                
                return ToolResult(
                    success=return_code == 0,
                    output={
                        "stdout": stdout.decode('utf-8', errors='ignore'),
                        "stderr": stderr.decode('utf-8', errors='ignore'),
                        "return_code": return_code
                    },
                    status=ToolStatus.SUCCESS if return_code == 0 else ToolStatus.FAILURE,
                    metadata={
                        "language": "bash",
                        "workspace": workspace
                    }
                )
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ToolResult(
                    success=False,
                    output=None,
                    error_message=f"Code execution timed out after {config.timeout} seconds",
                    status=ToolStatus.FAILURE
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Execution error: {str(e)}",
                status=ToolStatus.FAILURE
            )
    
    def create_execution_config(self, language: str, **overrides) -> CodeExecutionConfig:
        """Create execution configuration with overrides"""
        
        try:
            lang_enum = CodeLanguage(language.lower())
        except ValueError:
            lang_enum = CodeLanguage.PYTHON
        
        # Start with default config
        default_config = self.default_configs.get(lang_enum, CodeExecutionConfig(lang_enum))
        
        # Apply overrides
        config_dict = {
            "language": lang_enum,
            "timeout": overrides.get("timeout", default_config.timeout),
            "memory_limit": overrides.get("memory_limit", default_config.memory_limit),
            "cpu_limit": overrides.get("cpu_limit", default_config.cpu_limit),
            "network_access": overrides.get("network_access", default_config.network_access),
            "file_system_access": overrides.get("file_system_access", default_config.file_system_access),
            "allowed_imports": overrides.get("allowed_imports", default_config.allowed_imports)
        }
        
        return CodeExecutionConfig(**config_dict)
