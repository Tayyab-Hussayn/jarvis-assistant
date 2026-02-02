#!/usr/bin/env python3
"""
Test the new multi-provider STT system
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.voice.multi_stt import MultiProviderSTT, STTConfig, STTProvider

async def test_stt_system():
    """Test the multi-provider STT system"""
    
    print("🎤 Testing Multi-Provider STT System")
    print("=" * 50)
    
    # Create STT engine
    config = STTConfig(
        primary_provider=STTProvider.SPEECH_RECOGNITION,
        fallback_providers=[STTProvider.WHISPER_LOCAL, STTProvider.GOOGLE_CLOUD]
    )
    
    stt = MultiProviderSTT(config)
    
    # Show status
    status = stt.get_status()
    print(f"📊 STT Status:")
    print(f"   Primary: {status['primary_provider']}")
    print(f"   Available: {status['available_providers']}")
    print(f"   Working: {status['working_providers']}/{status['total_providers']}")
    print()
    
    if status['working_providers'] == 0:
        print("❌ No STT providers available!")
        print("💡 Install dependencies:")
        print("   pip install SpeechRecognition")
        print("   pip install openai-whisper  # for local Whisper")
        return
    
    # Test microphone transcription
    print("🎤 Testing microphone transcription...")
    print("   Say something in the next 3 seconds...")
    
    try:
        result = await stt.transcribe_microphone(duration=3)
        if result.strip():
            print(f"✅ Transcribed: '{result}'")
        else:
            print("⚠️  No speech detected or transcription failed")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_stt_system())
