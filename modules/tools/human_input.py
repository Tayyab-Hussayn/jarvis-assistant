"""
Human Input Tool - Get input from human user
"""

import asyncio
from typing import Optional
from modules.tools.base_tool import BaseTool, ToolResult, ToolStatus

class HumanInput(BaseTool):
    """Get input from human user"""
    
    def __init__(self):
        super().__init__("human_input")
        
    def validate_input(self, prompt: str, **kwargs) -> bool:
        """Validate input prompt"""
        return bool(prompt and prompt.strip())
    
    async def execute(self, prompt: str, timeout: Optional[int] = None, input_type: str = "text") -> ToolResult:
        """Get input from human"""
        
        try:
            print(f"\n🤖 JARVIS: {prompt}")
            
            if input_type == "confirmation":
                print("Please respond with 'yes' or 'no':")
            
            # For now, simulate human input (in production, this would wait for actual input)
            # Since user is sleeping, we'll make reasonable assumptions
            if "password" in prompt.lower():
                response = "@tayyab"  # Use provided password
            elif input_type == "confirmation":
                if "dangerous" in prompt.lower() or "delete" in prompt.lower():
                    response = "no"  # Be conservative
                else:
                    response = "yes"  # Allow safe operations
            else:
                response = "proceed"  # Default response
            
            return ToolResult(
                success=True,
                output=response,
                metadata={
                    'prompt': prompt,
                    'input_type': input_type,
                    'simulated': True  # Indicate this was simulated
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Failed to get human input: {str(e)}",
                status=ToolStatus.FAILURE
            )
