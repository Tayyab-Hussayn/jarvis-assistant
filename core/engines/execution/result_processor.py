"""
Result Processor - Parse and validate tool execution results
"""

import json
import re
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from modules.tools.base_tool import ToolResult, ToolStatus

class DataType(Enum):
    TEXT = "text"
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    HTML = "html"
    BINARY = "binary"
    NUMBER = "number"
    BOOLEAN = "boolean"

@dataclass
class ProcessedResult:
    original_result: ToolResult
    data_type: DataType
    structured_data: Any
    validation_passed: bool
    validation_errors: List[str]
    extracted_values: Dict[str, Any]
    confidence: float

class ResultProcessor:
    """Process and validate tool execution results"""
    
    def __init__(self):
        self.logger = logging.getLogger("result_processor")
        
        # Data type detection patterns
        self.type_patterns = {
            DataType.JSON: [r'^\s*[\{\[]', r'^\s*".*":\s*'],
            DataType.XML: [r'^\s*<\?xml', r'^\s*<[^>]+>'],
            DataType.HTML: [r'<!DOCTYPE html', r'<html', r'<body'],
            DataType.CSV: [r'^[^,\n]*,[^,\n]*', r'^\w+,\w+'],
            DataType.NUMBER: [r'^\s*-?\d+\.?\d*\s*$'],
            DataType.BOOLEAN: [r'^\s*(true|false|yes|no|1|0)\s*$']
        }
        
        # Common extraction patterns
        self.extraction_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "url": r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "ip_address": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            "file_path": r'(?:[a-zA-Z]:\\|/)(?:[^\\/:*?"<>|\r\n]+[\\\/])*[^\\/:*?"<>|\r\n]*',
            "number": r'-?\d+\.?\d*',
            "date": r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}'
        }
    
    def process_result(self, result: ToolResult, expected_type: Optional[DataType] = None,
                      validation_rules: Optional[Dict] = None) -> ProcessedResult:
        """Process and validate a tool result"""
        
        self.logger.info(f"Processing result from tool execution")
        
        # Detect data type
        detected_type = self._detect_data_type(result.output)
        data_type = expected_type or detected_type
        
        # Structure the data
        structured_data = self._structure_data(result.output, data_type)
        
        # Validate result
        validation_passed, validation_errors = self._validate_result(
            structured_data, validation_rules or {}
        )
        
        # Extract common values
        extracted_values = self._extract_values(result.output)
        
        # Calculate confidence
        confidence = self._calculate_confidence(result, validation_passed, data_type, detected_type)
        
        processed = ProcessedResult(
            original_result=result,
            data_type=data_type,
            structured_data=structured_data,
            validation_passed=validation_passed,
            validation_errors=validation_errors,
            extracted_values=extracted_values,
            confidence=confidence
        )
        
        self.logger.info(f"Result processed: type={data_type.value}, valid={validation_passed}, confidence={confidence:.2f}")
        return processed
    
    def _detect_data_type(self, data: Any) -> DataType:
        """Detect the data type of the output"""
        
        if data is None:
            return DataType.TEXT
        
        # Handle different input types
        if isinstance(data, bool):
            return DataType.BOOLEAN
        elif isinstance(data, (int, float)):
            return DataType.NUMBER
        elif isinstance(data, dict):
            return DataType.JSON
        elif isinstance(data, list):
            return DataType.JSON
        elif not isinstance(data, str):
            return DataType.TEXT
        
        # String data - detect format
        data_str = str(data).strip()
        
        if not data_str:
            return DataType.TEXT
        
        # Check patterns
        for data_type, patterns in self.type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, data_str, re.IGNORECASE | re.MULTILINE):
                    return data_type
        
        return DataType.TEXT
    
    def _structure_data(self, data: Any, data_type: DataType) -> Any:
        """Structure data according to detected type"""
        
        try:
            if data_type == DataType.JSON:
                if isinstance(data, (dict, list)):
                    return data
                elif isinstance(data, str):
                    return json.loads(data)
            
            elif data_type == DataType.CSV:
                if isinstance(data, str):
                    lines = data.strip().split('\n')
                    if len(lines) > 1:
                        headers = [h.strip() for h in lines[0].split(',')]
                        rows = []
                        for line in lines[1:]:
                            values = [v.strip() for v in line.split(',')]
                            if len(values) == len(headers):
                                rows.append(dict(zip(headers, values)))
                        return {"headers": headers, "rows": rows}
            
            elif data_type == DataType.NUMBER:
                if isinstance(data, str):
                    try:
                        if '.' in data:
                            return float(data)
                        else:
                            return int(data)
                    except ValueError:
                        pass
            
            elif data_type == DataType.BOOLEAN:
                if isinstance(data, str):
                    data_lower = data.lower().strip()
                    return data_lower in ['true', 'yes', '1']
            
            # For other types or if parsing fails, return as-is
            return data
            
        except Exception as e:
            self.logger.warning(f"Failed to structure data as {data_type.value}: {e}")
            return data
    
    def _validate_result(self, data: Any, validation_rules: Dict) -> Tuple[bool, List[str]]:
        """Validate structured data against rules"""
        
        errors = []
        
        # Required fields validation
        if "required_fields" in validation_rules and isinstance(data, dict):
            for field in validation_rules["required_fields"]:
                if field not in data:
                    errors.append(f"Missing required field: {field}")
        
        # Type validation
        if "expected_type" in validation_rules:
            expected_type = validation_rules["expected_type"]
            if not isinstance(data, expected_type):
                errors.append(f"Expected type {expected_type.__name__}, got {type(data).__name__}")
        
        # Range validation for numbers
        if "min_value" in validation_rules and isinstance(data, (int, float)):
            if data < validation_rules["min_value"]:
                errors.append(f"Value {data} below minimum {validation_rules['min_value']}")
        
        if "max_value" in validation_rules and isinstance(data, (int, float)):
            if data > validation_rules["max_value"]:
                errors.append(f"Value {data} above maximum {validation_rules['max_value']}")
        
        # Length validation for strings/lists
        if "min_length" in validation_rules and hasattr(data, '__len__'):
            if len(data) < validation_rules["min_length"]:
                errors.append(f"Length {len(data)} below minimum {validation_rules['min_length']}")
        
        if "max_length" in validation_rules and hasattr(data, '__len__'):
            if len(data) > validation_rules["max_length"]:
                errors.append(f"Length {len(data)} above maximum {validation_rules['max_length']}")
        
        # Pattern validation for strings
        if "pattern" in validation_rules and isinstance(data, str):
            pattern = validation_rules["pattern"]
            if not re.search(pattern, data):
                errors.append(f"Data does not match pattern: {pattern}")
        
        # Custom validation function
        if "validator" in validation_rules:
            validator = validation_rules["validator"]
            if callable(validator):
                try:
                    is_valid = validator(data)
                    if not is_valid:
                        errors.append("Custom validation failed")
                except Exception as e:
                    errors.append(f"Custom validation error: {e}")
        
        return len(errors) == 0, errors
    
    def _extract_values(self, data: Any) -> Dict[str, Any]:
        """Extract common values using patterns"""
        
        extracted = {}
        
        if not isinstance(data, str):
            data = str(data)
        
        # Extract using patterns
        for value_type, pattern in self.extraction_patterns.items():
            matches = re.findall(pattern, data, re.IGNORECASE)
            if matches:
                extracted[value_type] = matches if len(matches) > 1 else matches[0]
        
        # Extract key-value pairs from structured text
        kv_pattern = r'(\w+):\s*([^\n,;]+)'
        kv_matches = re.findall(kv_pattern, data)
        if kv_matches:
            extracted["key_value_pairs"] = dict(kv_matches)
        
        return extracted
    
    def _calculate_confidence(self, result: ToolResult, validation_passed: bool, 
                            expected_type: DataType, detected_type: DataType) -> float:
        """Calculate confidence score for the processed result"""
        
        confidence = 0.5  # Base confidence
        
        # Tool execution success
        if result.success:
            confidence += 0.3
        else:
            confidence -= 0.2
        
        # Validation passed
        if validation_passed:
            confidence += 0.2
        else:
            confidence -= 0.1
        
        # Type detection accuracy
        if expected_type == detected_type:
            confidence += 0.1
        
        # Tool confidence (if available)
        if hasattr(result, 'confidence') and result.confidence:
            confidence = (confidence + result.confidence) / 2
        
        # Execution time factor (faster = more confident for simple tasks)
        if result.execution_time < 1.0:
            confidence += 0.05
        elif result.execution_time > 10.0:
            confidence -= 0.05
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, confidence))
    
    def extract_specific_data(self, processed_result: ProcessedResult, 
                            extraction_config: Dict) -> Dict[str, Any]:
        """Extract specific data based on configuration"""
        
        extracted = {}
        data = processed_result.structured_data
        
        # Field extraction for structured data
        if "fields" in extraction_config and isinstance(data, dict):
            for field_name, field_config in extraction_config["fields"].items():
                if isinstance(field_config, str):
                    # Simple field name
                    if field_config in data:
                        extracted[field_name] = data[field_config]
                elif isinstance(field_config, dict):
                    # Complex field extraction
                    path = field_config.get("path", field_name)
                    default = field_config.get("default")
                    transform = field_config.get("transform")
                    
                    # Navigate path
                    value = self._navigate_path(data, path, default)
                    
                    # Apply transformation
                    if transform and callable(transform):
                        try:
                            value = transform(value)
                        except Exception as e:
                            self.logger.warning(f"Transform failed for {field_name}: {e}")
                    
                    extracted[field_name] = value
        
        # Pattern-based extraction
        if "patterns" in extraction_config:
            text_data = str(processed_result.original_result.output)
            for pattern_name, pattern in extraction_config["patterns"].items():
                matches = re.findall(pattern, text_data, re.IGNORECASE | re.MULTILINE)
                if matches:
                    extracted[pattern_name] = matches if len(matches) > 1 else matches[0]
        
        return extracted
    
    def _navigate_path(self, data: Any, path: str, default: Any = None) -> Any:
        """Navigate a dot-separated path in nested data"""
        
        try:
            current = data
            for part in path.split('.'):
                if isinstance(current, dict):
                    current = current.get(part, default)
                elif isinstance(current, list) and part.isdigit():
                    index = int(part)
                    current = current[index] if 0 <= index < len(current) else default
                else:
                    return default
            return current
        except Exception:
            return default
    
    def validate_success_criteria(self, processed_result: ProcessedResult, 
                                success_criteria: str) -> Tuple[bool, str]:
        """Validate if result meets success criteria"""
        
        # Simple success criteria evaluation
        criteria_lower = success_criteria.lower()
        
        # Check basic success
        if not processed_result.original_result.success:
            return False, "Tool execution failed"
        
        # Check validation
        if not processed_result.validation_passed:
            return False, f"Validation failed: {'; '.join(processed_result.validation_errors)}"
        
        # Check confidence threshold
        if "high confidence" in criteria_lower and processed_result.confidence < 0.8:
            return False, f"Confidence too low: {processed_result.confidence:.2f}"
        
        # Check for specific content
        if "contains" in criteria_lower:
            # Extract what should be contained
            contains_match = re.search(r'contains\s+["\']([^"\']+)["\']', criteria_lower)
            if contains_match:
                expected_content = contains_match.group(1)
                result_text = str(processed_result.original_result.output).lower()
                if expected_content not in result_text:
                    return False, f"Result does not contain expected content: {expected_content}"
        
        # Check for specific data type
        if "json" in criteria_lower and processed_result.data_type != DataType.JSON:
            return False, f"Expected JSON data, got {processed_result.data_type.value}"
        
        return True, "Success criteria met"

# Global result processor instance
result_processor = ResultProcessor()
