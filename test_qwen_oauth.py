#!/usr/bin/env python3
"""
Test Qwen OAuth Authentication System
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm.qwen_auth import qwen_auth
from core.llm.llm_manager import llm_manager

async def test_qwen_oauth():
    """Test Qwen OAuth authentication and API call"""
    
    print("🔐 Testing Qwen OAuth Authentication")
    print("=" * 50)
    
    # Test authentication
    print("1. Testing OAuth token loading...")
    try:
        token = qwen_auth.load_token()
        if token:
            print(f"✅ Token loaded successfully")
            print(f"   Token type: {token.token_type}")
            print(f"   Resource: {token.resource_url}")
            print(f"   Expired: {token.is_expired}")
            
            if token.is_expired:
                print("⚠️  Token is expired - may need refresh")
            
        else:
            print("❌ Failed to load token")
            return
    except Exception as e:
        print(f"❌ Token loading error: {e}")
        return
    
    # Test authentication headers
    print("\n2. Testing authentication headers...")
    try:
        headers = qwen_auth.get_auth_headers()
        print("✅ Auth headers generated")
        print(f"   Authorization: {headers['Authorization'][:20]}...")
    except Exception as e:
        print(f"❌ Auth headers error: {e}")
        return
    
    # Test base URL
    print("\n3. Testing base URL...")
    try:
        base_url = qwen_auth.get_base_url()
        print(f"✅ Base URL: {base_url}")
    except Exception as e:
        print(f"❌ Base URL error: {e}")
        return
    
    # Test LLM integration
    print("\n4. Testing LLM integration...")
    try:
        # Check if Qwen provider is available
        providers = llm_manager.get_available_providers()
        print(f"Available providers: {providers}")
        
        if 'qwen' in providers:
            print("✅ Qwen provider registered")
            
            # Test simple generation
            print("\n5. Testing API call...")
            response = await llm_manager.generate(
                "Hello! Please respond with 'Qwen OAuth authentication working!'",
                provider="qwen"
            )
            
            print(f"✅ API call successful!")
            print(f"   Response: {response.content}")
            print(f"   Model: {response.model}")
            print(f"   Provider: {response.provider}")
            print(f"   Tokens: {response.tokens_used}")
            
        else:
            print("❌ Qwen provider not available")
            
    except Exception as e:
        print(f"❌ LLM integration error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    async def main():
        await test_qwen_oauth()
        
        # Clean up LLM manager sessions
        try:
            if hasattr(llm_manager, 'clients'):
                for client in llm_manager.clients.values():
                    if hasattr(client, 'close'):
                        await client.close()
        except:
            pass
    
    asyncio.run(main())
