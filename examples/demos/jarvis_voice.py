#!/usr/bin/env python3
"""
JARVIS Voice Integration - Connect voice to main system
"""

import sys
sys.path.append('/home/krawin/exp.code/jarvis')

from core.voice.voice_interface import voice_interface
from core.llm.llm_manager import llm_manager
import asyncio

async def jarvis_voice_chat():
    """JARVIS voice chat with Qwen integration"""
    
    print("🎤 JARVIS Voice Chat Starting...")
    
    # Set up Qwen
    import os
    os.environ['QWEN_API_KEY'] = "eo24BBq9pSxv6v8EXKwSBYm7tkdbrpVCY1fX1IxGLbfDIDlatSNESqM6MteL5Kjs9n_A6Ix4PJ83EwFcHcQHDA"
    
    # Switch to Qwen
    llm_manager.switch_provider('qwen')
    
    # Start voice conversation
    await voice_interface.voice_conversation(llm_manager)

async def jarvis_speak(text: str):
    """Make JARVIS speak"""
    print(f"🗣️  JARVIS: {text}")
    await voice_interface.speak(text, save_file=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "chat":
        asyncio.run(jarvis_voice_chat())
    elif len(sys.argv) > 1 and sys.argv[1] == "speak":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Hello, I am JARVIS!"
        asyncio.run(jarvis_speak(text))
    else:
        print("Usage:")
        print("  python jarvis_voice.py speak <text>")
        print("  python jarvis_voice.py chat")
