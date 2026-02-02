#!/usr/bin/env python3
"""
Simple voice test - just check if the system can record audio
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.voice.voice_interface import VoiceInterface

async def simple_voice_test():
    """Simple voice interface test"""
    
    print("🎤 Simple Voice Test")
    print("=" * 30)
    
    # Create voice interface
    voice = VoiceInterface()
    
    print("✅ Voice interface created")
    print("📊 STT Status:", voice.stt_engine.get_status())
    
    # Test TTS
    print("\n🔊 Testing Text-to-Speech...")
    await voice.speak("Hello! JARVIS voice system is working.")
    
    print("✅ Voice test complete!")

if __name__ == "__main__":
    asyncio.run(simple_voice_test())
