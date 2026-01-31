#!/usr/bin/env python3
"""
LLM Configuration Manager - Easy API and model management
"""

import sys
sys.path.append('/home/krawin/exp.code/jarvis')

from core.llm.llm_manager import llm_manager, LLMConfig, LLMProvider
import os

class LLMConfigurator:
    """Simple interface for LLM configuration"""
    
    def __init__(self):
        self.manager = llm_manager
    
    def add_provider(self, name: str, provider_type: str, model: str, api_key: str, base_url: str = None):
        """Add new LLM provider"""
        
        provider_enum = LLMProvider(provider_type)
        config = LLMConfig(
            provider=provider_enum,
            model=model,
            api_key=api_key,
            base_url=base_url
        )
        
        self.manager.register_client(name, config)
        print(f"✅ Added {name} ({provider_type}) with model {model}")
    
    def set_default(self, provider_name: str):
        """Set default provider"""
        success = self.manager.switch_provider(provider_name)
        if success:
            print(f"✅ Set {provider_name} as default")
        else:
            print(f"❌ Provider {provider_name} not found")
        return success
    
    def list_providers(self):
        """List all configured providers"""
        providers = self.manager.get_available_providers()
        current = self.manager.get_current_provider()
        
        print("📋 Available LLM Providers:")
        for provider in providers:
            marker = "→ DEFAULT" if provider == current else ""
            client = self.manager.clients[provider]
            print(f"  • {provider}: {client.config.model} {marker}")
    
    def quick_setup(self):
        """Interactive setup for common providers"""
        print("🚀 Quick LLM Setup")
        print("=" * 30)
        
        # Check existing providers
        self.list_providers()
        
        print("\nAdd new provider? (y/n): ", end="")
        if input().lower() == 'y':
            self._interactive_add()
    
    def _interactive_add(self):
        """Interactive provider addition"""
        print("\nSelect provider type:")
        print("1. Claude (Anthropic)")
        print("2. GPT (OpenAI)")
        print("3. Gemini (Google)")
        print("4. Qwen")
        print("5. Custom")
        
        choice = input("Choice (1-5): ")
        
        if choice == "1":
            api_key = input("Anthropic API Key: ")
            model = input("Model (default: claude-3-5-sonnet-20241022): ") or "claude-3-5-sonnet-20241022"
            self.add_provider("claude", "claude", model, api_key)
        
        elif choice == "2":
            api_key = input("OpenAI API Key: ")
            model = input("Model (default: gpt-4o): ") or "gpt-4o"
            self.add_provider("gpt", "gpt", model, api_key)
        
        elif choice == "3":
            api_key = input("Google API Key: ")
            model = input("Model (default: gemini-2.0-flash-exp): ") or "gemini-2.0-flash-exp"
            self.add_provider("gemini", "gemini", model, api_key)
        
        elif choice == "4":
            api_key = input("Qwen API Key: ")
            model = input("Model (default: qwen3-coder-plus): ") or "qwen3-coder-plus"
            base_url = input("Base URL (default: https://portal.qwen.ai/v1): ") or "https://portal.qwen.ai/v1"
            self.add_provider("qwen", "qwen", model, api_key, base_url)
        
        # Set as default?
        if input("Set as default? (y/n): ").lower() == 'y':
            providers = list(self.manager.clients.keys())
            if providers:
                self.set_default(providers[-1])

# Usage examples
if __name__ == "__main__":
    config = LLMConfigurator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "setup":
            config.quick_setup()
        elif command == "list":
            config.list_providers()
        elif command == "default" and len(sys.argv) > 2:
            config.set_default(sys.argv[2])
        else:
            print("Usage:")
            print("  python llm_config.py setup     # Interactive setup")
            print("  python llm_config.py list      # List providers")
            print("  python llm_config.py default <provider>  # Set default")
    else:
        config.quick_setup()
