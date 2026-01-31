#!/usr/bin/env python3
"""
Test LLM Integration
"""

import asyncio
import sys
import os
sys.path.append('/home/krawin/exp.code/jarvis')

from core.llm.llm_manager import llm_manager
from core.engines.reasoning.reasoning_engine import ReasoningEngine

async def test_llm_integration():
    """Test LLM integration with JARVIS"""
    
    print("🧪 Testing LLM Integration with JARVIS")
    print("=" * 50)
    
    # Test 1: LLM Manager Status
    print("1. LLM Manager Status:")
    status = llm_manager.get_status()
    print(f"   Current Provider: {status['current_provider']}")
    print(f"   Available Providers: {status['available_providers']}")
    
    if not status['available_providers']:
        print("❌ No LLM providers available!")
        print("Please set environment variables:")
        print("   export QWEN_API_KEY=your_key")
        print("   export ANTHROPIC_API_KEY=your_key")
        print("   export OPENAI_API_KEY=your_key")
        return
    
    # Test 2: Basic LLM Call
    print("\n2. Testing Basic LLM Call:")
    try:
        response = await llm_manager.generate(
            prompt="Hello! Please respond with 'LLM integration working correctly' if you can understand this.",
            system_prompt="You are JARVIS, an AI assistant. Be concise and helpful."
        )
        print(f"   ✅ Response from {response.provider}: {response.content[:100]}...")
    except Exception as e:
        print(f"   ❌ Basic LLM call failed: {e}")
        return
    
    # Test 3: Reasoning Engine Integration
    print("\n3. Testing Reasoning Engine Integration:")
    try:
        reasoning_engine = ReasoningEngine()
        
        llm_response = await reasoning_engine.llm_reason(
            prompt="Analyze this task: 'Create a simple web application'. Break it down into 3 main steps.",
            system_prompt="You are a strategic planning AI. Provide clear, actionable steps."
        )
        
        print(f"   ✅ Reasoning Engine LLM call successful")
        print(f"   Response: {llm_response.content[:200]}...")
        
    except Exception as e:
        print(f"   ❌ Reasoning Engine integration failed: {e}")
        return
    
    # Test 4: Provider Switching
    print("\n4. Testing Provider Switching:")
    providers = llm_manager.get_available_providers()
    
    if len(providers) > 1:
        original_provider = llm_manager.get_current_provider()
        
        # Switch to different provider
        for provider in providers:
            if provider != original_provider:
                success = llm_manager.switch_provider(provider)
                if success:
                    print(f"   ✅ Switched to {provider}")
                    
                    # Test with new provider
                    response = await llm_manager.generate("Say 'Provider switch successful'")
                    print(f"   Response from {response.provider}: {response.content[:50]}...")
                    
                    # Switch back
                    llm_manager.switch_provider(original_provider)
                    print(f"   ✅ Switched back to {original_provider}")
                    break
    else:
        print("   ⚠️  Only one provider available, skipping switch test")
    
    # Test 5: Chat Functionality
    print("\n5. Testing Chat Functionality:")
    try:
        messages = [
            {"role": "system", "content": "You are JARVIS. Be helpful and concise."},
            {"role": "user", "content": "What's 2+2?"},
            {"role": "assistant", "content": "2+2 equals 4."},
            {"role": "user", "content": "What about 3+3?"}
        ]
        
        chat_response = await llm_manager.chat(messages)
        print(f"   ✅ Chat response: {chat_response.content[:100]}...")
        
    except Exception as e:
        print(f"   ❌ Chat functionality failed: {e}")
    
    print("\n🎉 LLM Integration Test Complete!")
    print("✅ JARVIS can now use real LLM reasoning capabilities")

if __name__ == "__main__":
    asyncio.run(test_llm_integration())
