#!/usr/bin/env python3
"""
Demo: JARVIS Natural Speech
"""

import asyncio
import sys
sys.path.append('/home/krawin/exp.code/jarvis')

from core.voice.voice_interface import voice_interface
from core.voice.speech_cleaner import speech_cleaner

async def demo_natural_speech():
    """Demo JARVIS speaking naturally"""
    
    print("🎤 JARVIS Natural Speech Demo")
    print("=" * 35)
    
    test_texts = [
        'Hello! I am JARVIS, your AI assistant.',
        'The function get_user_data() returns {"name": "John", "age": 30}',
        'Check the API documentation at https://docs.example.com/api',
        'Set the variable "user_name" to process user input.',
        'JARVIS can handle JSON/XML data with 95% accuracy!'
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. Original text:")
        print(f"   {text}")
        
        cleaned = speech_cleaner.clean_for_speech(text)
        print(f"   Cleaned for speech:")
        print(f"   {cleaned}")
        
        print(f"   🗣️  JARVIS speaking...")
        await voice_interface.speak(cleaned)
        print(f"   ✅ Speech generated")
    
    print(f"\n🎉 JARVIS now speaks naturally without technical symbols!")

if __name__ == "__main__":
    asyncio.run(demo_natural_speech())
