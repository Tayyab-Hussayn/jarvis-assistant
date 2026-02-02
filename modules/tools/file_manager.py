"""
File Manager Tool - Safe file operations
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Union
from modules.tools.base_tool import BaseTool, ToolResult, ToolStatus

class FileManager(BaseTool):
    """Handle file system operations safely"""
    
    WHITELIST_DIRS = [
        "/home/krawin/exp.code/jarvis",
        "/home/krawin/exp.code/jarvis/workspace",  # Default workspace for generated files
        "/tmp/jarvis_workspace",
        "/var/tmp/jarvis"
    ]
    
    DEFAULT_WORKSPACE = "/home/krawin/exp.code/jarvis/workspace"
    
    def __init__(self):
        super().__init__("file_manager")
        # Ensure workspace exists
        import os
        os.makedirs(self.DEFAULT_WORKSPACE, exist_ok=True)
        
    def _is_path_safe(self, path: str) -> bool:
        """Check if path is in whitelist"""
        abs_path = os.path.abspath(path)
        return any(abs_path.startswith(allowed) for allowed in self.WHITELIST_DIRS)
    
    def validate_input(self, operation: str, path: str, **kwargs) -> bool:
        """Validate file operation"""
        if not self._is_path_safe(path):
            self.logger.warning(f"Path not in whitelist: {path}")
            return False
        return True
    
    async def execute(self, operation: str, path: str, **kwargs) -> ToolResult:
        """Execute file operation"""
        
        try:
            if operation == "read":
                return await self._read_file(path, **kwargs)
            elif operation == "write":
                content = kwargs.get("content", "")
                encoding = kwargs.get("encoding", "utf-8")
                append = kwargs.get("append", False)
                return await self._write_file(path, content, encoding, append)
            elif operation == "create_dir":
                return await self._create_directory(path)
            elif operation == "list":
                return await self._list_directory(path)
            elif operation == "delete":
                return await self._delete_path(path)
            elif operation == "copy":
                return await self._copy_path(path, kwargs.get("destination"), **kwargs)
            elif operation == "move":
                return await self._move_path(path, kwargs.get("destination"), **kwargs)
            else:
                return ToolResult(
                    success=False,
                    output=None,
                    error_message=f"Unknown operation: {operation}",
                    status=ToolStatus.FAILURE
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error_message=f"File operation failed: {str(e)}",
                status=ToolStatus.FAILURE
            )
    
    async def _read_file(self, path: str, encoding: str = "utf-8") -> ToolResult:
        """Read file content"""
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return ToolResult(
                success=True,
                output=content,
                metadata={"path": path, "size": len(content)}
            )
        except FileNotFoundError:
            return ToolResult(
                success=False,
                output=None,
                error_message=f"File not found: {path}",
                status=ToolStatus.FAILURE
            )
    
    async def _write_file(self, path: str, content: str, encoding: str = "utf-8", append: bool = False) -> ToolResult:
        """Write content to file with intelligent path handling"""
        
        # Smart path resolution
        resolved_path = self._resolve_path(path)
        
        mode = 'a' if append else 'w'
        
        # Create directory structure if it doesn't exist
        dir_path = os.path.dirname(resolved_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
            self.logger.info(f"📁 Created directory structure: {dir_path}")
        
        with open(resolved_path, mode, encoding=encoding) as f:
            f.write(content)
        
        return ToolResult(
            success=True,
            output=f"Written {len(content)} characters to {resolved_path}",
            metadata={"path": resolved_path, "size": len(content), "append": append}
        )
    
    def _resolve_path(self, path: str) -> str:
        """Intelligently resolve file paths"""
        import os
        
        # Handle different path formats
        if path.startswith('/'):
            # Absolute path - check if it's in whitelist
            if self._is_path_safe(path):
                return path
            else:
                # Redirect to workspace if not safe
                filename = os.path.basename(path)
                return os.path.join(self.DEFAULT_WORKSPACE, filename)
        
        elif '/' in path:
            # Relative path with directories
            if path.startswith('workspace/'):
                # Remove workspace/ prefix and use workspace
                relative_path = path[10:]  # Remove 'workspace/'
                return os.path.join(self.DEFAULT_WORKSPACE, relative_path)
            else:
                # Treat as relative to workspace
                return os.path.join(self.DEFAULT_WORKSPACE, path)
        
        else:
            # Just a filename - use workspace
            return os.path.join(self.DEFAULT_WORKSPACE, path)
    
    async def _create_directory(self, path: str) -> ToolResult:
        """Create directory"""
        os.makedirs(path, exist_ok=True)
        return ToolResult(
            success=True,
            output=f"Directory created: {path}",
            metadata={"path": path}
        )
    
    async def _list_directory(self, path: str) -> ToolResult:
        """List directory contents"""
        if not os.path.exists(path):
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Directory not found: {path}",
                status=ToolStatus.FAILURE
            )
        
        items = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            items.append({
                "name": item,
                "path": item_path,
                "is_dir": os.path.isdir(item_path),
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0
            })
        
        return ToolResult(
            success=True,
            output=items,
            metadata={"path": path, "count": len(items)}
        )
    
    async def _delete_path(self, path: str) -> ToolResult:
        """Delete file or directory"""
        if not os.path.exists(path):
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Path not found: {path}",
                status=ToolStatus.FAILURE
            )
        
        if os.path.isdir(path):
            shutil.rmtree(path)
            action = "Directory deleted"
        else:
            os.remove(path)
            action = "File deleted"
        
        return ToolResult(
            success=True,
            output=f"{action}: {path}",
            metadata={"path": path, "action": action}
        )
    
    async def _copy_path(self, source: str, destination: str) -> ToolResult:
        """Copy file or directory"""
        if not self._is_path_safe(destination):
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Destination not in whitelist: {destination}",
                status=ToolStatus.FAILURE
            )
        
        if os.path.isdir(source):
            shutil.copytree(source, destination)
            action = "Directory copied"
        else:
            shutil.copy2(source, destination)
            action = "File copied"
        
        return ToolResult(
            success=True,
            output=f"{action}: {source} -> {destination}",
            metadata={"source": source, "destination": destination}
        )
    
    async def _move_path(self, source: str, destination: str) -> ToolResult:
        """Move file or directory"""
        if not self._is_path_safe(destination):
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Destination not in whitelist: {destination}",
                status=ToolStatus.FAILURE
            )
        
        shutil.move(source, destination)
        
        return ToolResult(
            success=True,
            output=f"Moved: {source} -> {destination}",
            metadata={"source": source, "destination": destination}
        )
