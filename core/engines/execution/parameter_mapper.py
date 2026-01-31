#!/usr/bin/env python3
"""
Tool Parameter Mapper - Maps generic parameters to tool-specific parameters
"""

from typing import Dict, Any, Optional, List
import logging

class ToolParameterMapper:
    """Maps generic parameters to tool-specific parameter names"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Tool parameter mappings
        self.parameter_mappings = {
            "file_manager": {
                "required": ["operation", "path"],
                "mappings": {
                    "action": "operation",
                    "file_path": "path",
                    "filepath": "path",
                    "filename": "path",
                    "directory": "path",
                    "dir": "path",
                    "text": "content",
                    "data": "content",
                    "file_content": "content",
                    "dest": "destination",
                    "target": "destination"
                },
                "defaults": {
                    "operation": "read",
                    "encoding": "utf-8",
                    "append": False
                }
            },
            
            "terminal_executor": {
                "required": ["command"],
                "mappings": {
                    "cmd": "command",
                    "shell_command": "command",
                    "bash_command": "command",
                    "script": "command",
                    "working_dir": "cwd",
                    "directory": "cwd",
                    "timeout_seconds": "timeout"
                },
                "defaults": {
                    "timeout": 30,
                    "capture_output": True
                }
            },
            
            "code_executor": {
                "required": ["code"],
                "mappings": {
                    "source_code": "code",
                    "script": "code",
                    "program": "code",
                    "lang": "language",
                    "programming_language": "language"
                },
                "defaults": {
                    "language": "python",
                    "timeout": 30
                }
            },
            
            "calculator": {
                "required": ["expression"],
                "mappings": {
                    "formula": "expression",
                    "calculation": "expression",
                    "math": "expression",
                    "equation": "expression"
                },
                "defaults": {}
            },
            
            "web_search": {
                "required": ["query"],
                "mappings": {
                    "search_term": "query",
                    "search_query": "query",
                    "keywords": "query",
                    "q": "query",
                    "max_results": "limit",
                    "num_results": "limit"
                },
                "defaults": {
                    "limit": 10
                }
            },
            
            "human_input": {
                "required": ["prompt"],
                "mappings": {
                    "message": "prompt",
                    "question": "prompt",
                    "request": "prompt"
                },
                "defaults": {
                    "timeout": 300
                }
            }
        }
    
    def map_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Map generic parameters to tool-specific parameters"""
        
        if tool_name not in self.parameter_mappings:
            self.logger.warning(f"No parameter mapping found for tool: {tool_name}")
            return parameters
        
        mapping_config = self.parameter_mappings[tool_name]
        mapped_params = {}
        
        # Start with defaults
        mapped_params.update(mapping_config.get("defaults", {}))
        
        # Apply parameter mappings
        mappings = mapping_config.get("mappings", {})
        for param_name, param_value in parameters.items():
            if param_name in mappings:
                # Use mapped name
                mapped_name = mappings[param_name]
                mapped_params[mapped_name] = param_value
            else:
                # Use original name
                mapped_params[param_name] = param_value
        
        # Check required parameters
        required_params = mapping_config.get("required", [])
        missing_params = []
        
        for required_param in required_params:
            if required_param not in mapped_params:
                missing_params.append(required_param)
        
        if missing_params:
            self.logger.error(f"Missing required parameters for {tool_name}: {missing_params}")
            # Try to infer missing parameters
            mapped_params.update(self._infer_missing_parameters(tool_name, mapped_params, missing_params))
        
        self.logger.debug(f"Mapped parameters for {tool_name}: {mapped_params}")
        return mapped_params
    
    def _infer_missing_parameters(self, tool_name: str, current_params: Dict[str, Any], 
                                missing_params: List[str]) -> Dict[str, Any]:
        """Try to infer missing parameters from context"""
        
        inferred = {}
        
        # Common inference patterns
        if "command" in missing_params and tool_name == "terminal_executor":
            # Try to build command from other parameters
            if "script" in current_params:
                inferred["command"] = current_params["script"]
            elif "action" in current_params:
                inferred["command"] = str(current_params["action"])
        
        if "code" in missing_params and tool_name == "code_executor":
            # Try to build code from other parameters
            if "script" in current_params:
                inferred["code"] = current_params["script"]
            elif "program" in current_params:
                inferred["code"] = current_params["program"]
        
        if "expression" in missing_params and tool_name == "calculator":
            # Try to build expression from other parameters
            if "math" in current_params:
                inferred["expression"] = current_params["math"]
            elif "calculation" in current_params:
                inferred["expression"] = current_params["calculation"]
        
        if "query" in missing_params and tool_name == "web_search":
            # Try to build query from other parameters
            if "search" in current_params:
                inferred["query"] = current_params["search"]
            elif "keywords" in current_params:
                inferred["query"] = current_params["keywords"]
        
        if "operation" in missing_params and tool_name == "file_manager":
            # Infer operation from context
            if "content" in current_params:
                inferred["operation"] = "write"
            elif "path" in current_params:
                inferred["operation"] = "read"
        
        if "path" in missing_params and tool_name == "file_manager":
            # Try to infer path from other parameters
            if "file" in current_params:
                inferred["path"] = current_params["file"]
            elif "filename" in current_params:
                inferred["path"] = current_params["filename"]
        
        if inferred:
            self.logger.info(f"Inferred missing parameters for {tool_name}: {inferred}")
        
        return inferred
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get parameter schema for a tool"""
        return self.parameter_mappings.get(tool_name)
    
    def validate_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate parameters for a tool"""
        
        if tool_name not in self.parameter_mappings:
            return True, []  # No validation rules
        
        mapping_config = self.parameter_mappings[tool_name]
        required_params = mapping_config.get("required", [])
        
        missing_params = []
        for required_param in required_params:
            if required_param not in parameters:
                missing_params.append(required_param)
        
        return len(missing_params) == 0, missing_params

# Global parameter mapper instance
parameter_mapper = ToolParameterMapper()
