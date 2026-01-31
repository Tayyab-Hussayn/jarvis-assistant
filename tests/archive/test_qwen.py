#!/usr/bin/env python3
"""
Test Qwen API Connection
"""

import asyncio
import sys
import os
sys.path.append('/home/krawin/exp.code/jarvis')

async def test_qwen_connection(api_key=None):
    """Test Qwen API with provided key"""
    
    if api_key:
        os.environ['QWEN_API_KEY'] = api_key
    
    if not os.getenv('QWEN_API_KEY'):
        print("❌ No QWEN_API_KEY found!")
        print("Usage: python test_qwen.py <your_api_key>")
        return False
    
    try:
        from core.llm.llm_manager import llm_manager
        
        # Force reload to pick up new API key
        llm_manager.load_config()
        
        print("🧪 Testing Qwen API connection...")
        print(f"Model: {llm_manager.clients['qwen'].config.model}")
        print(f"Base URL: {llm_manager.clients['qwen'].config.base_url}")
        print(f"API Key: {os.getenv('QWEN_API_KEY')[:10]}...")
        
        # Switch to Qwen
        llm_manager.switch_provider('qwen')
        
        # Test simple prompt
        response = await llm_manager.generate(
            prompt="Hello! Please respond with 'Qwen API is working correctly' if you can understand this message.",
            system_prompt="You are JARVIS, an AI assistant. Be concise and helpful."
        )
        
        print("✅ Qwen API Test Successful!")
        print(f"Response: {response.content}")
        print(f"Model: {response.model}")
        print(f"Tokens: {response.tokens_used}")
        
        return True
        
    except Exception as e:
        print(f"❌ Qwen API Test Failed: {e}")
        return False

if __name__ == "__main__":
    api_key = sys.argv[1] if len(sys.argv) > 1 else None
    success = asyncio.run(test_qwen_connection(api_key))
    
    if success:
        print("\n🎉 Qwen is ready to use with JARVIS!")
    else:
        print("\n💡 Please check your API key and try again.")
