#!/usr/bin/env python3
"""
Enhanced Code Execution Environment - Docker-based multi-language execution
"""

import asyncio
import logging
import tempfile
import os
import json
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
import subprocess

@dataclass
class ExecutionConfig:
    """Code execution configuration"""
    language: str
    timeout: int = 30
    memory_limit: str = "128m"
    cpu_limit: str = "0.5"
    network_disabled: bool = True
    read_only: bool = True
    max_output_size: int = 10000

@dataclass
class ExecutionResult:
    """Code execution result"""
    success: bool
    output: str
    error: str
    execution_time: float
    exit_code: int
    language: str
    resource_usage: Dict[str, Any] = None

class DockerCodeExecutor:
    """Docker-based code executor for multiple languages"""
    
    def __init__(self):
        self.logger = logging.getLogger("docker_executor")
        self.docker_available = False
        self.supported_languages = {
            "python": {
                "image": "python:3.11-alpine",
                "command": ["python", "-c"],
                "file_extension": ".py"
            },
            "javascript": {
                "image": "node:18-alpine",
                "command": ["node", "-e"],
                "file_extension": ".js"
            },
            "bash": {
                "image": "alpine:latest",
                "command": ["sh", "-c"],
                "file_extension": ".sh"
            },
            "go": {
                "image": "golang:1.21-alpine",
                "command": ["go", "run"],
                "file_extension": ".go"
            },
            "rust": {
                "image": "rust:1.75-alpine",
                "command": ["rustc", "--edition", "2021", "-o", "/tmp/main", "-", "&&", "/tmp/main"],
                "file_extension": ".rs"
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize Docker executor"""
        try:
            # Check if Docker is available
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                self.docker_available = True
                self.logger.info("✅ Docker available for code execution")
                return True
            else:
                self.logger.warning("❌ Docker not available")
                return False
                
        except Exception as e:
            self.logger.warning(f"❌ Docker check failed: {e}")
            return False
    
    async def execute_code(self, code: str, config: ExecutionConfig) -> ExecutionResult:
        """Execute code in Docker container"""
        
        if not self.docker_available:
            return await self._fallback_execution(code, config)
        
        if config.language not in self.supported_languages:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Unsupported language: {config.language}",
                execution_time=0,
                exit_code=1,
                language=config.language
            )
        
        lang_config = self.supported_languages[config.language]
        start_time = time.time()
        
        try:
            # Create temporary file for code
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix=lang_config["file_extension"],
                delete=False
            ) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            # Build Docker command
            docker_cmd = [
                "docker", "run",
                "--rm",
                f"--memory={config.memory_limit}",
                f"--cpus={config.cpu_limit}",
                "-v", f"{temp_file_path}:/code{lang_config['file_extension']}:ro",
                lang_config["image"]
            ]
            
            # Add network isolation if requested
            if config.network_disabled:
                docker_cmd.insert(-1, "--network=none")
            
            # Add read-only if requested  
            if config.read_only:
                docker_cmd.insert(-1, "--read-only")
            
            # Add language-specific execution command
            if config.language == "python":
                docker_cmd.extend(["python", "/code.py"])
            elif config.language == "javascript":
                docker_cmd.extend(["node", "/code.js"])
            elif config.language == "bash":
                docker_cmd.extend(["sh", "/code.sh"])
            elif config.language == "go":
                docker_cmd.extend(["sh", "-c", "cd /tmp && cp /code.go . && go run code.go"])
            elif config.language == "rust":
                docker_cmd.extend(["sh", "-c", "rustc /code.rs -o /tmp/main && /tmp/main"])
            
            # Remove empty strings from command
            docker_cmd = [cmd for cmd in docker_cmd if cmd and cmd.strip()]
            
            # Execute in Docker
            process = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=config.timeout
                )
                
                execution_time = time.time() - start_time
                
                # Decode output
                output = stdout.decode('utf-8', errors='replace')[:config.max_output_size]
                error = stderr.decode('utf-8', errors='replace')[:config.max_output_size]
                
                # Clean up temp file
                os.unlink(temp_file_path)
                
                return ExecutionResult(
                    success=process.returncode == 0,
                    output=output,
                    error=error,
                    execution_time=execution_time,
                    exit_code=process.returncode,
                    language=config.language
                )
                
            except asyncio.TimeoutError:
                process.kill()
                os.unlink(temp_file_path)
                
                return ExecutionResult(
                    success=False,
                    output="",
                    error=f"Execution timed out after {config.timeout} seconds",
                    execution_time=config.timeout,
                    exit_code=124,
                    language=config.language
                )
        
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Docker execution failed: {str(e)}",
                execution_time=time.time() - start_time,
                exit_code=1,
                language=config.language
            )
    
    async def _fallback_execution(self, code: str, config: ExecutionConfig) -> ExecutionResult:
        """Fallback execution without Docker"""
        
        if config.language == "python":
            return await self._execute_python_fallback(code, config)
        elif config.language == "javascript":
            return await self._execute_js_fallback(code, config)
        elif config.language == "bash":
            return await self._execute_bash_fallback(code, config)
        else:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Fallback execution not available for {config.language}",
                execution_time=0,
                exit_code=1,
                language=config.language
            )
    
    async def _execute_python_fallback(self, code: str, config: ExecutionConfig) -> ExecutionResult:
        """Fallback Python execution"""
        start_time = time.time()
        
        try:
            # Security check
            dangerous_imports = ['os', 'subprocess', 'sys', '__import__', 'eval', 'exec']
            if any(danger in code for danger in dangerous_imports):
                return ExecutionResult(
                    success=False,
                    output="",
                    error="Dangerous code detected - execution blocked",
                    execution_time=0,
                    exit_code=1,
                    language=config.language
                )
            
            # Execute with subprocess
            process = await asyncio.create_subprocess_exec(
                "python", "-c", code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=config.timeout
            )
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=process.returncode == 0,
                output=stdout.decode('utf-8', errors='replace')[:config.max_output_size],
                error=stderr.decode('utf-8', errors='replace')[:config.max_output_size],
                execution_time=execution_time,
                exit_code=process.returncode,
                language=config.language
            )
            
        except asyncio.TimeoutError:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Execution timed out after {config.timeout} seconds",
                execution_time=config.timeout,
                exit_code=124,
                language=config.language
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Execution failed: {str(e)}",
                execution_time=time.time() - start_time,
                exit_code=1,
                language=config.language
            )
    
    async def _execute_js_fallback(self, code: str, config: ExecutionConfig) -> ExecutionResult:
        """Fallback JavaScript execution"""
        start_time = time.time()
        
        try:
            # Check if Node.js is available
            process = await asyncio.create_subprocess_exec(
                "node", "-e", code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=config.timeout
            )
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=process.returncode == 0,
                output=stdout.decode('utf-8', errors='replace')[:config.max_output_size],
                error=stderr.decode('utf-8', errors='replace')[:config.max_output_size],
                execution_time=execution_time,
                exit_code=process.returncode,
                language=config.language
            )
            
        except FileNotFoundError:
            return ExecutionResult(
                success=False,
                output="",
                error="Node.js not available for JavaScript execution",
                execution_time=0,
                exit_code=1,
                language=config.language
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=f"JavaScript execution failed: {str(e)}",
                execution_time=time.time() - start_time,
                exit_code=1,
                language=config.language
            )
    
    async def _execute_bash_fallback(self, code: str, config: ExecutionConfig) -> ExecutionResult:
        """Fallback Bash execution"""
        start_time = time.time()
        
        try:
            # Basic security check
            dangerous_commands = ['rm -rf', 'sudo', 'chmod', 'chown', '>', '>>', 'curl', 'wget']
            if any(danger in code for danger in dangerous_commands):
                return ExecutionResult(
                    success=False,
                    output="",
                    error="Dangerous command detected - execution blocked",
                    execution_time=0,
                    exit_code=1,
                    language=config.language
                )
            
            process = await asyncio.create_subprocess_shell(
                code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=config.timeout
            )
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=process.returncode == 0,
                output=stdout.decode('utf-8', errors='replace')[:config.max_output_size],
                error=stderr.decode('utf-8', errors='replace')[:config.max_output_size],
                execution_time=execution_time,
                exit_code=process.returncode,
                language=config.language
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Bash execution failed: {str(e)}",
                execution_time=time.time() - start_time,
                exit_code=1,
                language=config.language
            )

# Global code executor instance
docker_executor = DockerCodeExecutor()
