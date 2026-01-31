#!/usr/bin/env python3
"""
LLM CLI Tool - Command line interface for LLM management and testing
"""

import asyncio
import sys
import os
sys.path.append('/home/krawin/exp.code/jarvis')

from core.llm.llm_manager import llm_manager

async def main():
    """Main CLI interface"""
    
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        await show_status()
    elif command == "list":
        await list_providers()
    elif command == "switch":
        if len(sys.argv) < 3:
            print("Usage: llm_cli.py switch <provider_name>")
            return
        await switch_provider(sys.argv[2])
    elif command == "test":
        provider = sys.argv[2] if len(sys.argv) > 2 else None
        await test_llm(provider)
    elif command == "chat":
        provider = sys.argv[2] if len(sys.argv) > 2 else None
        await interactive_chat(provider)
    else:
        print_help()

def print_help():
    """Print help information"""
    print("""
🤖 JARVIS LLM CLI Tool

Commands:
  status                    - Show current LLM status
  list                     - List available providers
  switch <provider>        - Switch to a provider
  test [provider]          - Test LLM with simple prompt
  chat [provider]          - Interactive chat session
  
Examples:
  python llm_cli.py status
  python llm_cli.py switch qwen
  python llm_cli.py test claude
  python llm_cli.py chat
""")

async def show_status():
    """Show LLM manager status"""
    status = llm_manager.get_status()
    
    print("🤖 JARVIS LLM Status")
    print("=" * 40)
    print(f"Current Provider: {status['current_provider'] or 'None'}")
    print(f"Available Providers: {len(status['available_providers'])}")
    print(f"Total Clients: {status['total_clients']}")
    
    if status['available_providers']:
        print("\nAvailable Providers:")
        for provider in status['available_providers']:
            marker = "→" if provider == status['current_provider'] else " "
            print(f"  {marker} {provider}")

async def list_providers():
    """List all available providers"""
    providers = llm_manager.get_available_providers()
    current = llm_manager.get_current_provider()
    
    print("📋 Available LLM Providers:")
    print("=" * 30)
    
    if not providers:
        print("No providers configured.")
        print("\nTo add providers, set environment variables:")
        print("  QWEN_API_KEY=your_key")
        print("  ANTHROPIC_API_KEY=your_key") 
        print("  OPENAI_API_KEY=your_key")
        print("  GOOGLE_API_KEY=your_key")
        return
    
    for provider in providers:
        marker = "→ CURRENT" if provider == current else ""
        print(f"  • {provider} {marker}")

async def switch_provider(provider_name: str):
    """Switch to a different provider"""
    success = llm_manager.switch_provider(provider_name)
    
    if success:
        print(f"✅ Switched to provider: {provider_name}")
    else:
        print(f"❌ Failed to switch to provider: {provider_name}")
        print("Available providers:")
        for p in llm_manager.get_available_providers():
            print(f"  • {p}")

async def test_llm(provider: str = None):
    """Test LLM with a simple prompt"""
    
    if not llm_manager.get_available_providers():
        print("❌ No LLM providers available. Please configure API keys.")
        return
    
    test_prompt = "Hello! Please respond with a brief greeting and confirm you're working correctly."
    
    try:
        print(f"🧪 Testing LLM{' (' + provider + ')' if provider else ''}...")
        print(f"Prompt: {test_prompt}")
        print("-" * 50)
        
        response = await llm_manager.generate(
            prompt=test_prompt,
            provider=provider
        )
        
        print(f"✅ Response from {response.provider} ({response.model}):")
        print(response.content)
        
        if response.tokens_used:
            print(f"\nTokens used: {response.tokens_used}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

async def interactive_chat(provider: str = None):
    """Interactive chat session"""
    
    if not llm_manager.get_available_providers():
        print("❌ No LLM providers available. Please configure API keys.")
        return
    
    current_provider = provider or llm_manager.get_current_provider()
    print(f"💬 Interactive Chat with {current_provider}")
    print("Type 'quit' to exit, 'switch <provider>' to change provider")
    print("=" * 50)
    
    messages = []
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            
            if user_input.lower().startswith('switch '):
                new_provider = user_input[7:].strip()
                if llm_manager.switch_provider(new_provider):
                    current_provider = new_provider
                    print(f"✅ Switched to {new_provider}")
                else:
                    print(f"❌ Provider {new_provider} not available")
                continue
            
            if not user_input:
                continue
            
            messages.append({"role": "user", "content": user_input})
            
            print(f"\n{current_provider}: ", end="", flush=True)
            
            response = await llm_manager.chat(
                messages=messages,
                provider=current_provider
            )
            
            print(response.content)
            messages.append({"role": "assistant", "content": response.content})
            
            # Keep conversation manageable
            if len(messages) > 20:
                messages = messages[-10:]
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
