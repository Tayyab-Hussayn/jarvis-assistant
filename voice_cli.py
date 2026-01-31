#!/usr/bin/env python3
"""
Voice CLI - Command line interface for JARVIS voice capabilities
"""

import asyncio
import sys
import os
sys.path.append('/home/krawin/exp.code/jarvis')

from core.voice.voice_interface import voice_interface
from core.llm.llm_manager import llm_manager

async def main():
    """Main voice CLI interface"""
    
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "speak":
        if len(sys.argv) < 3:
            print("Usage: voice_cli.py speak <text>")
            return
        text = " ".join(sys.argv[2:])
        await test_speak(text)
    
    elif command == "listen":
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        await test_listen(duration)
    
    elif command == "conversation":
        await start_conversation()
    
    elif command == "test":
        await test_voice_system()
    
    else:
        print_help()

def print_help():
    """Print help information"""
    print("""
🎤 JARVIS Voice CLI

Commands:
  speak <text>         - Convert text to speech
  listen [duration]    - Listen for speech (default 5 seconds)
  conversation         - Start voice conversation with JARVIS
  test                 - Test voice system
  
Examples:
  python voice_cli.py speak "Hello, I am JARVIS"
  python voice_cli.py listen 10
  python voice_cli.py conversation
""")

async def test_speak(text: str):
    """Test text-to-speech"""
    print(f"🗣️  Speaking: {text}")
    
    try:
        result = await voice_interface.speak(text, save_file=True)
        if result:
            print(f"✅ Speech saved to: {result}")
        else:
            print("✅ Speech generated successfully")
    except Exception as e:
        print(f"❌ Speech failed: {e}")
        print("💡 Install dependencies: pip install edge-tts")

async def test_listen(duration: int):
    """Test speech-to-text"""
    print(f"🎤 Listening for {duration} seconds...")
    
    try:
        text = await voice_interface.listen(duration)
        if text.strip():
            print(f"✅ Heard: '{text}'")
        else:
            print("❌ No speech detected")
    except Exception as e:
        print(f"❌ Listening failed: {e}")
        print("💡 Install dependencies: pip install sounddevice soundfile")

async def start_conversation():
    """Start voice conversation"""
    print("🎙️  Starting voice conversation with JARVIS...")
    print("Say 'goodbye' or 'exit' to end conversation")
    
    try:
        await voice_interface.voice_conversation(llm_manager)
    except Exception as e:
        print(f"❌ Conversation failed: {e}")

async def test_voice_system():
    """Test entire voice system"""
    print("🧪 Testing JARVIS Voice System")
    print("=" * 40)
    
    # Test 1: TTS
    print("1. Testing Text-to-Speech...")
    try:
        await voice_interface.speak("Voice system test successful")
        print("   ✅ TTS working")
    except Exception as e:
        print(f"   ❌ TTS failed: {e}")
    
    # Test 2: STT (if available)
    print("\n2. Testing Speech-to-Text...")
    try:
        print("   Say something in the next 3 seconds...")
        text = await voice_interface.listen(3)
        if text.strip():
            print(f"   ✅ STT working: '{text}'")
        else:
            print("   ⚠️  STT available but no speech detected")
    except Exception as e:
        print(f"   ❌ STT failed: {e}")
    
    # Test 3: Integration
    print("\n3. Testing LLM Integration...")
    try:
        response = await llm_manager.generate("Say hello in a friendly way")
        print(f"   ✅ LLM integration: {response.content[:50]}...")
    except Exception as e:
        print(f"   ❌ LLM integration failed: {e}")
    
    print("\n🎉 Voice system test complete!")

if __name__ == "__main__":
    asyncio.run(main())
