#!/usr/bin/env python3
"""
Test JARVIS TTS Integration
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.voice.voice_interface import voice_interface
from core.llm.llm_manager import llm_manager

async def test_jarvis_voice():
    """Test JARVIS with voice output"""
    
    print("🤖 Testing JARVIS Voice Integration")
    print("=" * 40)
    
    # Test TTS
    print("1. Testing Text-to-Speech...")
    await voice_interface.speak("Hello! I am JARVIS. My text to speech system is now working perfectly!")
    
    # Test LLM + TTS integration
    print("\n2. Testing LLM + TTS integration...")
    try:
        response = await llm_manager.generate("Say hello and introduce yourself as JARVIS in a friendly way")
        print(f"LLM Response: {response.content}")
        
        print("\n3. Speaking LLM response...")
        await voice_interface.speak(response.content)
        
        print("\n✅ JARVIS voice integration test complete!")
        
        # Clean up
        for client in llm_manager.clients.values():
            if hasattr(client, 'close'):
                await client.close()
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_jarvis_voice())
