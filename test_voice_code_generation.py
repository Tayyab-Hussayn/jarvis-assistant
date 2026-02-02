#!/usr/bin/env python3
"""
Test Voice Interface Code Generation - Verify clean code output
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm.smart_llm_wrapper import smart_llm

async def test_voice_code_generation():
    """Test that voice interface will generate clean code"""
    
    print("🎤 Testing Voice Interface Code Generation")
    print("=" * 50)
    
    # Simulate voice commands that would generate files
    test_commands = [
        "Create a simple portfolio website with HTML and CSS",
        "Generate a Python script that prints hello world",
        "Build a JavaScript function for user authentication",
        "Make a JSON configuration file for a web app"
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n🗣️ Test {i}: '{command}'")
        print("-" * 40)
        
        try:
            # This simulates what happens in voice_interface.py
            response = await smart_llm.generate(
                prompt=command,
                system_prompt="You are JARVIS, an AI assistant. Keep responses conversational and under 100 words for voice interaction."
            )
            
            print(f"📝 Response length: {len(response.content)} characters")
            
            # Check if content filtering was applied
            if hasattr(response, 'metadata') and response.metadata and response.metadata.get('content_filtered'):
                print("✅ Content filtering was applied!")
                print(f"   🎯 Reduction: {response.metadata['reduction_percent']:.1f}%")
                print(f"   📁 Detected type: {response.metadata['detected_file_type']}")
                print(f"   📊 Original: {response.metadata['original_length']} → Filtered: {response.metadata['filtered_length']}")
            else:
                print("ℹ️ No content filtering applied (not detected as file generation)")
            
            # Show first 150 characters of response
            preview = response.content[:150].replace('\n', ' ')
            print(f"📄 Preview: {preview}{'...' if len(response.content) > 150 else ''}")
            
            # Check if response starts with conversational text
            conversational_starts = ["I'll", "I will", "Let me", "Here's", "Sure", "I can"]
            starts_conversational = any(response.content.strip().startswith(start) for start in conversational_starts)
            
            if starts_conversational:
                print("⚠️ Response still starts with conversational text")
            else:
                print("✅ Response starts with clean content")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Voice interface code generation test completed!")
    
    # Cleanup
    await smart_llm.cleanup()

if __name__ == "__main__":
    asyncio.run(test_voice_code_generation())
