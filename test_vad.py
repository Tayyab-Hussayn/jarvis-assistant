#!/usr/bin/env python3
"""
Test Voice Activity Detection System
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.voice.multi_stt import MultiProviderSTT, STTConfig, STTProvider

async def test_vad_system():
    """Test voice activity detection"""
    
    print("🎤 Testing Voice Activity Detection")
    print("=" * 40)
    print("Features:")
    print("- Starts listening when you speak")
    print("- Stops 2 seconds after you stop speaking")
    print("- Continues if you resume speaking during pause")
    print("- No time limit for total conversation")
    print()
    
    # Create STT with VAD
    config = STTConfig(primary_provider=STTProvider.SPEECH_RECOGNITION)
    stt = MultiProviderSTT(config)
    
    try:
        print("🗣️  Say something... (will auto-stop 2s after silence)")
        result = await stt.transcribe_microphone()
        
        if result.strip():
            print(f"✅ Transcribed: '{result}'")
        else:
            print("⚠️  No speech detected")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_vad_system())
