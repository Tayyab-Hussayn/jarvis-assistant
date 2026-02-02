"""
Content Filter - Separates code from conversational text
"""

import re
import logging
from typing import Optional, Dict, Any

class ContentFilter:
    """Filters and extracts clean code from LLM responses"""
    
    def __init__(self):
        self.logger = logging.getLogger("content_filter")
    
    def extract_code(self, content: str, file_type: str = None) -> str:
        """Extract clean code from LLM response"""
        
        # Detect file type if not provided
        if not file_type:
            file_type = self._detect_file_type(content)
        
        # Apply appropriate extraction method
        if file_type == 'html':
            return self._extract_html_code(content)
        elif file_type == 'python':
            return self._extract_python_code(content)
        elif file_type == 'javascript':
            return self._extract_javascript_code(content)
        elif file_type == 'css':
            return self._extract_css_code(content)
        elif file_type == 'json':
            return self._extract_json_code(content)
        else:
            return self._extract_generic_code(content)
    
    def _detect_file_type(self, content: str) -> str:
        """Detect file type from content"""
        content_lower = content.lower()
        
        if '<!doctype html' in content_lower or '<html' in content_lower:
            return 'html'
        elif 'def ' in content or 'import ' in content or 'class ' in content:
            return 'python'
        elif 'function ' in content or 'const ' in content or 'let ' in content:
            return 'javascript'
        elif '{' in content and '}' in content and ('selector' in content_lower or 'color:' in content_lower):
            return 'css'
        elif content.strip().startswith('{') and content.strip().endswith('}'):
            return 'json'
        else:
            return 'generic'
    
    def _extract_html_code(self, content: str) -> str:
        """Extract HTML code from response"""
        
        # Look for code blocks first
        code_block_patterns = [
            r'```html\s*(.*?)\s*```',
            r'```\s*(<!DOCTYPE html.*?</html>)\s*```',
            r'```\s*(<html.*?</html>)\s*```'
        ]
        
        for pattern in code_block_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Look for HTML document structure
        html_patterns = [
            r'(<!DOCTYPE html.*?</html>)',
            r'(<html.*?</html>)',
            r'(<HTML.*?</HTML>)'
        ]
        
        for pattern in html_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no complete HTML found, return cleaned content
        cleaned = self._remove_conversational_text(content)
        
        # Remove any remaining markdown code block markers
        cleaned = re.sub(r'^```\w*\s*', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'\s*```\s*$', '', cleaned, flags=re.MULTILINE)
        
        return cleaned.strip()
    
    def _extract_python_code(self, content: str) -> str:
        """Extract Python code from response"""
        
        # Look for code blocks
        code_block_patterns = [
            r'```python\s*(.*?)\s*```',
            r'```py\s*(.*?)\s*```',
            r'```\s*((?:import|from|def|class|if|for|while|try).*?)\s*```'
        ]
        
        for pattern in code_block_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Extract Python code patterns
        python_patterns = [
            r'((?:import|from|def|class).*?)(?=\n\n[A-Z]|\n\n#[^#]|\Z)',
            r'(#!/usr/bin/env python.*?)(?=\n\n[A-Z]|\Z)'
        ]
        
        for pattern in python_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return self._remove_conversational_text(content)
    
    def _extract_javascript_code(self, content: str) -> str:
        """Extract JavaScript code from response"""
        
        code_block_patterns = [
            r'```javascript\s*(.*?)\s*```',
            r'```js\s*(.*?)\s*```',
            r'```\s*((?:function|const|let|var|class).*?)\s*```'
        ]
        
        for pattern in code_block_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return self._remove_conversational_text(content)
    
    def _extract_css_code(self, content: str) -> str:
        """Extract CSS code from response"""
        
        code_block_patterns = [
            r'```css\s*(.*?)\s*```',
            r'```\s*((?:/\*.*?\*/|[^{}]*\{[^{}]*\}).*?)\s*```'
        ]
        
        for pattern in code_block_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return self._remove_conversational_text(content)
    
    def _extract_json_code(self, content: str) -> str:
        """Extract JSON code from response"""
        
        code_block_patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(\{.*?\})\s*```'
        ]
        
        for pattern in code_block_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Look for JSON structure
        json_pattern = r'(\{.*?\})'
        match = re.search(json_pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return self._remove_conversational_text(content)
    
    def _extract_generic_code(self, content: str) -> str:
        """Extract code from generic content"""
        
        # Look for any code blocks
        code_block_pattern = r'```(?:\w+)?\s*(.*?)\s*```'
        match = re.search(code_block_pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return self._remove_conversational_text(content)
    
    def _remove_conversational_text(self, content: str) -> str:
        """Remove conversational text and keep only code-like content"""
        
        lines = content.split('\n')
        filtered_lines = []
        
        conversational_patterns = [
            r'^(I\'ll|I will|Let me|Here\'s|This is|I\'ve created)',
            r'^(Sure|Certainly|Of course|Absolutely)',
            r'^(The above|This code|This will|You can)',
            r'^(Note:|Important:|Remember:)',
            r'^\*\*.*?\*\*',  # Bold text
            r'^#{1,6}\s',     # Markdown headers
            r'^```\w*\s*$',   # Code block markers
            r'^\s*```\s*$',   # Code block end markers
        ]
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines at start
            if not line and not filtered_lines:
                continue
            
            # Skip conversational patterns
            is_conversational = any(re.match(pattern, line, re.IGNORECASE) for pattern in conversational_patterns)
            
            if not is_conversational:
                filtered_lines.append(line)
        
        # Join and clean up
        result = '\n'.join(filtered_lines).strip()
        
        # Remove any remaining markdown artifacts
        result = re.sub(r'^```\w*\s*', '', result, flags=re.MULTILINE)
        result = re.sub(r'\s*```\s*$', '', result, flags=re.MULTILINE)
        result = re.sub(r'^`+\w*\s*', '', result, flags=re.MULTILINE)
        
        # Remove leading conversational text before code starts
        code_start_patterns = [
            r'^.*?(?=<!DOCTYPE html)',
            r'^.*?(?=<html)',
            r'^.*?(?=#!/usr/bin)',
            r'^.*?(?=import\s)',
            r'^.*?(?=from\s)',
            r'^.*?(?=def\s)',
            r'^.*?(?=class\s)',
            r'^.*?(?=function\s)',
            r'^.*?(?=const\s)',
            r'^.*?(?=let\s)',
            r'^.*?(?=var\s)',
            r'^.*?(?=\{)'
        ]
        
        for pattern in code_start_patterns:
            match = re.search(pattern, result, re.DOTALL | re.IGNORECASE)
            if match:
                # Find where actual code starts
                code_start = match.end() - len(match.group().split()[-1]) if match.group().split() else match.end()
                result = result[code_start:].strip()
                break
        
        return result

# Global content filter
content_filter = ContentFilter()
