#!/usr/bin/env python3
"""
Voice Tool - JARVIS tool for voice interaction
"""

import sys
sys.path.append('/home/krawin/exp.code/jarvis')

from modules.tools.base_tool import BaseTool, ToolResult, ToolStatus, tool_registry
from core.voice.voice_interface import VoiceInterface, VoiceConfig
import asyncio

class VoiceTool(BaseTool):
    """Tool for voice interaction - TTS and STT"""
    
    def __init__(self):
        super().__init__(name="voice")
        self.description = "Text-to-speech and speech-to-text capabilities"
        self.voice_interface = VoiceInterface()
    
    def validate_input(self, action: str, **kwargs) -> bool:
        """Validate voice action parameters"""
        
        valid_actions = ["speak", "listen", "transcribe", "conversation"]
        
        if action not in valid_actions:
            self.logger.error(f"Invalid action: {action}. Valid: {valid_actions}")
            return False
        
        if action == "speak" and not kwargs.get("text"):
            self.logger.error("Speak action requires 'text' parameter")
            return False
        
        if action == "transcribe" and not kwargs.get("audio_file"):
            self.logger.error("Transcribe action requires 'audio_file' parameter")
            return False
        
        return True
    
    async def execute(self, action: str, **kwargs) -> ToolResult:
        """Execute voice action"""
        
        try:
            if action == "speak":
                text = kwargs["text"]
                save_file = kwargs.get("save_file", False)
                
                result = await self.voice_interface.speak(text, save_file)
                
                return ToolResult(
                    success=True,
                    output={
                        "message": f"Spoke: {text[:50]}...",
                        "audio_file": result if save_file else None
                    },
                    status=ToolStatus.SUCCESS
                )
            
            elif action == "listen":
                duration = kwargs.get("duration", 5)
                
                text = await self.voice_interface.listen(duration)
                
                return ToolResult(
                    success=bool(text.strip()),
                    output={
                        "transcribed_text": text,
                        "duration": duration
                    },
                    error_message="No speech detected" if not text.strip() else None,
                    status=ToolStatus.SUCCESS if text.strip() else ToolStatus.FAILURE
                )
            
            elif action == "transcribe":
                audio_file = kwargs["audio_file"]
                
                text = await self.voice_interface.transcribe_file(audio_file)
                
                return ToolResult(
                    success=bool(text.strip()),
                    output={
                        "transcribed_text": text,
                        "audio_file": audio_file
                    },
                    error_message="Transcription failed" if not text.strip() else None,
                    status=ToolStatus.SUCCESS if text.strip() else ToolStatus.FAILURE
                )
            
            elif action == "conversation":
                # This would need LLM manager integration
                return ToolResult(
                    success=True,
                    output={
                        "message": "Voice conversation mode available",
                        "note": "Use voice_interface.voice_conversation(llm_manager) for full conversation"
                    },
                    status=ToolStatus.SUCCESS
                )
            
            else:
                return ToolResult(
                    success=False,
                    output=None,
                    error_message=f"Unknown action: {action}",
                    status=ToolStatus.FAILURE
                )
        
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Voice error: {str(e)}",
                status=ToolStatus.FAILURE
            )

# Register the tool
tool_registry.register_tool(VoiceTool())
