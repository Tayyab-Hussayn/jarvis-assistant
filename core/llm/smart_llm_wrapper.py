"""
Smart LLM Wrapper - Automatically applies content filtering for file generation
"""

import re
import logging
from typing import Optional, Dict, Any
from core.llm.llm_manager import llm_manager
from core.llm.content_filter import content_filter

class SmartLLMWrapper:
    """Intelligent wrapper that applies content filtering when appropriate"""
    
    def __init__(self):
        self.logger = logging.getLogger("smart_llm_wrapper")
    
    async def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> Any:
        """Generate response with automatic content filtering for file generation"""
        
        # Get response from LLM
        response = await llm_manager.generate(prompt, system_prompt, **kwargs)
        
        # Check if this is a file generation request
        if self._is_file_generation_request(prompt):
            self.logger.info("🔍 Detected file generation request - applying content filter")
            
            # Detect file type from prompt
            file_type = self._detect_file_type_from_prompt(prompt)
            
            # Apply content filter
            original_content = response.content
            filtered_content = content_filter.extract_code(original_content, file_type)
            
            # Update response with filtered content
            response.content = filtered_content
            
            # Add metadata about filtering
            if not hasattr(response, 'metadata') or response.metadata is None:
                response.metadata = {}
            
            response.metadata.update({
                'content_filtered': True,
                'original_length': len(original_content),
                'filtered_length': len(filtered_content),
                'reduction_percent': ((len(original_content) - len(filtered_content)) / len(original_content) * 100) if original_content else 0,
                'detected_file_type': file_type
            })
            
            self.logger.info(f"✨ Content filtered: {response.metadata['reduction_percent']:.1f}% reduction")
        
        return response
    
    def _is_file_generation_request(self, prompt: str) -> bool:
        """Detect if the prompt is requesting file generation"""
        
        file_generation_indicators = [
            # Direct file creation requests
            r'create.*?(?:file|website|page|script|app)',
            r'generate.*?(?:file|website|page|script|app|code)',
            r'build.*?(?:website|page|app|application)',
            r'write.*?(?:file|script|code|program)',
            r'make.*?(?:website|page|app|file)',
            
            # File type mentions
            r'(?:html|css|javascript|python|json|xml|yaml).*?(?:file|code|script)',
            r'(?:\.html|\.css|\.js|\.py|\.json|\.xml|\.yaml)',
            
            # Web development
            r'(?:landing page|website|web app|portfolio|dashboard)',
            r'(?:frontend|backend|full.?stack)',
            
            # Programming requests
            r'(?:function|class|module|component|api)',
            r'(?:algorithm|script|program|application)',
            
            # Save/output requests
            r'save.*?(?:as|to|in).*?\.(?:html|css|js|py|json)',
            r'output.*?(?:file|code)',
        ]
        
        prompt_lower = prompt.lower()
        
        return any(re.search(pattern, prompt_lower) for pattern in file_generation_indicators)
    
    def _detect_file_type_from_prompt(self, prompt: str) -> str:
        """Detect the intended file type from the prompt"""
        
        prompt_lower = prompt.lower()
        
        # File extension patterns (highest priority)
        if re.search(r'\.html|\.htm', prompt_lower):
            return 'html'
        elif re.search(r'\.py', prompt_lower):
            return 'python'
        elif re.search(r'\.js', prompt_lower):
            return 'javascript'
        elif re.search(r'\.css', prompt_lower):
            return 'css'
        elif re.search(r'\.json', prompt_lower):
            return 'json'
        elif re.search(r'\.xml', prompt_lower):
            return 'xml'
        elif re.search(r'\.yaml|\.yml', prompt_lower):
            return 'yaml'
        
        # Specific language/technology mentions (high priority)
        if re.search(r'\bjavascript\b|\bjs\b(?!\w)', prompt_lower):
            return 'javascript'
        elif re.search(r'\bjson\b', prompt_lower):
            return 'json'
        elif re.search(r'\bpython\b|\bpy\b(?!\w)', prompt_lower):
            return 'python'
        elif re.search(r'\bcss\b', prompt_lower):
            return 'css'
        elif re.search(r'\bhtml\b', prompt_lower):
            return 'html'
        
        # Content-based detection (medium priority)
        if re.search(r'website|web|page|landing', prompt_lower):
            return 'html'
        elif re.search(r'function.*javascript|javascript.*function', prompt_lower):
            return 'javascript'
        elif re.search(r'script.*python|python.*script', prompt_lower):
            return 'python'
        elif re.search(r'config.*json|json.*config', prompt_lower):
            return 'json'
        elif re.search(r'style|styling|styles', prompt_lower):
            return 'css'
        
        # General patterns (low priority)
        if re.search(r'function|const|let|var', prompt_lower):
            return 'javascript'
        elif re.search(r'def|class|import', prompt_lower):
            return 'python'
        elif re.search(r'api|data|config', prompt_lower):
            return 'json'
        
        return 'generic'
    
    async def cleanup(self):
        """Cleanup resources"""
        await llm_manager.cleanup()

# Global smart wrapper instance
smart_llm = SmartLLMWrapper()
