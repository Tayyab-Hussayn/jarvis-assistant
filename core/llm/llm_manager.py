#!/usr/bin/env python3
"""
LLM Integration System - Multiple LLM providers with switching capabilities
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
import json
import yaml
from abc import ABC, abstractmethod

class LLMProvider(Enum):
    """Supported LLM providers"""
    QWEN = "qwen"
    CLAUDE = "claude"
    GPT = "gpt"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"
    GROQ = "groq"
    DEEPSEEK = "deepseek"
    LLAMA_LOCAL = "llama_local"
    OLLAMA = "ollama"

@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class LLMConfig:
    """LLM configuration"""
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 30
    extra_params: Optional[Dict[str, Any]] = None

class BaseLLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.logger = logging.getLogger(f"llm.{config.provider.value}")
    
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> LLMResponse:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Chat with conversation history"""
        pass
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        return True

class QwenClient(BaseLLMClient):
    """Qwen LLM client with authentication token"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.session = None
    
    async def _get_session(self):
        """Get HTTP session"""
        if not self.session:
            import aiohttp
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> LLMResponse:
        """Generate response from Qwen"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        return await self.chat(messages, **kwargs)
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Chat with Qwen API"""
        try:
            session = await self._get_session()
            
            payload = {
                "model": self.config.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
            }
            
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            async with session.post(
                f"{self.config.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=self.config.timeout
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    return LLMResponse(
                        content=content,
                        model=self.config.model,
                        provider=self.config.provider.value,
                        tokens_used=data.get("usage", {}).get("total_tokens"),
                        metadata={"response_data": data}
                    )
                else:
                    error_text = await response.text()
                    raise Exception(f"Qwen API error {response.status}: {error_text}")
        
        except Exception as e:
            self.logger.error(f"Qwen API call failed: {e}")
            raise

class ClaudeClient(BaseLLMClient):
    """Anthropic Claude client"""
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> LLMResponse:
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic(api_key=self.config.api_key)
            
            response = await client.messages.create(
                model=self.config.model,
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return LLMResponse(
                content=response.content[0].text,
                model=self.config.model,
                provider=self.config.provider.value,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens
            )
        
        except Exception as e:
            self.logger.error(f"Claude API call failed: {e}")
            raise
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        # Convert system message if present
        system_prompt = ""
        chat_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                chat_messages.append(msg)
        
        if len(chat_messages) == 1 and chat_messages[0]["role"] == "user":
            return await self.generate(chat_messages[0]["content"], system_prompt, **kwargs)
        
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic(api_key=self.config.api_key)
            
            response = await client.messages.create(
                model=self.config.model,
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
                system=system_prompt,
                messages=chat_messages
            )
            
            return LLMResponse(
                content=response.content[0].text,
                model=self.config.model,
                provider=self.config.provider.value,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens
            )
        
        except Exception as e:
            self.logger.error(f"Claude API call failed: {e}")
            raise

class GPTClient(BaseLLMClient):
    """OpenAI GPT client"""
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> LLMResponse:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        return await self.chat(messages, **kwargs)
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        try:
            import openai
            
            client = openai.AsyncOpenAI(api_key=self.config.api_key)
            
            response = await client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens)
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=self.config.model,
                provider=self.config.provider.value,
                tokens_used=response.usage.total_tokens
            )
        
        except Exception as e:
            self.logger.error(f"GPT API call failed: {e}")
            raise

class GeminiClient(BaseLLMClient):
    """Google Gemini client"""
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> LLMResponse:
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.config.api_key)
            model = genai.GenerativeModel(self.config.model)
            
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            response = await model.generate_content_async(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get("temperature", self.config.temperature),
                    max_output_tokens=kwargs.get("max_tokens", self.config.max_tokens)
                )
            )
            
            return LLMResponse(
                content=response.text,
                model=self.config.model,
                provider=self.config.provider.value
            )
        
        except Exception as e:
            self.logger.error(f"Gemini API call failed: {e}")
            raise
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        # Convert to single prompt for Gemini
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        full_prompt = "\n\n".join(prompt_parts)
        return await self.generate(full_prompt, **kwargs)

class OllamaClient(BaseLLMClient):
    """Local Ollama client"""
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> LLMResponse:
        try:
            import aiohttp
            
            payload = {
                "model": self.config.model,
                "prompt": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "num_predict": kwargs.get("max_tokens", self.config.max_tokens)
                }
            }
            
            base_url = self.config.base_url or "http://localhost:11434"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/api/generate",
                    json=payload,
                    timeout=self.config.timeout
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return LLMResponse(
                            content=data["response"],
                            model=self.config.model,
                            provider=self.config.provider.value
                        )
                    else:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error {response.status}: {error_text}")
        
        except Exception as e:
            self.logger.error(f"Ollama API call failed: {e}")
            raise
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        try:
            import aiohttp
            
            payload = {
                "model": self.config.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "num_predict": kwargs.get("max_tokens", self.config.max_tokens)
                }
            }
            
            base_url = self.config.base_url or "http://localhost:11434"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/api/chat",
                    json=payload,
                    timeout=self.config.timeout
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return LLMResponse(
                            content=data["message"]["content"],
                            model=self.config.model,
                            provider=self.config.provider.value
                        )
                    else:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error {response.status}: {error_text}")
        
        except Exception as e:
            self.logger.error(f"Ollama API call failed: {e}")
            raise

class LLMManager:
    """Manages multiple LLM providers and switching"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger("llm_manager")
        self.clients: Dict[str, BaseLLMClient] = {}
        self.current_provider: Optional[str] = None
        
        # Use config manager for settings
        from core.config.config_manager import config_manager
        jarvis_config = config_manager.get_config()
        
        self.default_provider = jarvis_config.llm_provider
        self.default_model = jarvis_config.llm_model
        self.api_key = jarvis_config.llm_api_key
        self.max_tokens = jarvis_config.llm_max_tokens
        
        # Legacy config path support
        self.config_path = config_path or "/home/krawin/code/jarvis/config.yaml"
        
        # Client mapping
        self.client_classes = {
            LLMProvider.QWEN: QwenClient,
            LLMProvider.CLAUDE: ClaudeClient,
            LLMProvider.GPT: GPTClient,
            LLMProvider.GEMINI: GeminiClient,
            LLMProvider.OLLAMA: OllamaClient,
            LLMProvider.LLAMA_LOCAL: OllamaClient,  # Use Ollama for local Llama
        }
        
        self.load_config()
    
    def load_config(self):
        """Load LLM configurations"""
        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            llm_config = config_data.get('llm', {})
            
            # Load Qwen config from existing setup
            if llm_config.get('provider') == 'qwen':
                qwen_config = LLMConfig(
                    provider=LLMProvider.QWEN,
                    model=llm_config.get('qwen_model', 'qwen3-coder-plus'),
                    base_url=llm_config.get('qwen_base_url', 'https://portal.qwen.ai/v1'),
                    api_key=os.getenv('QWEN_API_KEY'),
                    temperature=llm_config.get('temperature', 0.4)
                )
                self.register_client('qwen', qwen_config)
                self.current_provider = 'qwen'
            
            # Load other providers from environment
            self._load_env_configs()
            
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            self._load_env_configs()
    
    def _load_env_configs(self):
        """Load configurations from environment variables"""
        
        # Claude
        if os.getenv('ANTHROPIC_API_KEY'):
            claude_config = LLMConfig(
                provider=LLMProvider.CLAUDE,
                model=os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022'),
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
            self.register_client('claude', claude_config)
        
        # GPT
        if os.getenv('OPENAI_API_KEY'):
            gpt_config = LLMConfig(
                provider=LLMProvider.GPT,
                model=os.getenv('GPT_MODEL', 'gpt-4o'),
                api_key=os.getenv('OPENAI_API_KEY')
            )
            self.register_client('gpt', gpt_config)
        
        # Gemini
        if os.getenv('GOOGLE_API_KEY'):
            gemini_config = LLMConfig(
                provider=LLMProvider.GEMINI,
                model=os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp'),
                api_key=os.getenv('GOOGLE_API_KEY')
            )
            self.register_client('gemini', gemini_config)
        
        # Ollama (local)
        ollama_config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model=os.getenv('OLLAMA_MODEL', 'llama3.2'),
            base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        )
        self.register_client('ollama', ollama_config)
        
        # Set default if none set
        if not self.current_provider and self.clients:
            self.current_provider = list(self.clients.keys())[0]
        
        # Add mock client for testing if no real clients available
        if not self.clients:
            self._add_mock_client()
    
    def _add_mock_client(self):
        """Add mock client for testing purposes"""
        try:
            from .mock_client import MockLLMClient
            
            mock_config = LLMConfig(
                provider=LLMProvider.OLLAMA,  # Use OLLAMA enum for mock
                model="mock-jarvis-v1",
                base_url="mock://localhost",
                temperature=0.7
            )
            
            mock_client = MockLLMClient(mock_config)
            self.clients["mock"] = mock_client
            
            if not self.current_provider:
                self.current_provider = "mock"
            
            self.logger.info("Added mock LLM client for testing")
            
        except Exception as e:
            self.logger.error(f"Failed to add mock client: {e}")
    
    def register_client(self, name: str, config: LLMConfig):
        """Register an LLM client"""
        try:
            client_class = self.client_classes.get(config.provider)
            if client_class:
                client = client_class(config)
                if client.validate_config():
                    self.clients[name] = client
                    self.logger.info(f"Registered LLM client: {name} ({config.provider.value})")
                else:
                    self.logger.warning(f"Invalid config for {name}")
            else:
                self.logger.error(f"Unknown provider: {config.provider}")
        except Exception as e:
            self.logger.error(f"Failed to register {name}: {e}")
    
    def switch_provider(self, provider_name: str) -> bool:
        """Switch to a different LLM provider"""
        if provider_name in self.clients:
            self.current_provider = provider_name
            self.logger.info(f"Switched to LLM provider: {provider_name}")
            return True
        else:
            self.logger.error(f"Provider {provider_name} not available")
            return False
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.clients.keys())
    
    def get_current_provider(self) -> Optional[str]:
        """Get current provider name"""
        return self.current_provider
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, 
                      provider: Optional[str] = None, **kwargs) -> LLMResponse:
        """Generate response using current or specified provider"""
        
        provider_name = provider or self.current_provider
        
        if not provider_name or provider_name not in self.clients:
            raise ValueError(f"No valid provider available. Current: {provider_name}")
        
        client = self.clients[provider_name]
        return await client.generate(prompt, system_prompt, **kwargs)
    
    async def chat(self, messages: List[Dict[str, str]], 
                  provider: Optional[str] = None, **kwargs) -> LLMResponse:
        """Chat using current or specified provider"""
        
        provider_name = provider or self.current_provider
        
        if not provider_name or provider_name not in self.clients:
            raise ValueError(f"No valid provider available. Current: {provider_name}")
        
        client = self.clients[provider_name]
        return await client.chat(messages, **kwargs)
    
    def get_status(self) -> Dict[str, Any]:
        """Get LLM manager status"""
        return {
            "current_provider": self.current_provider,
            "available_providers": self.get_available_providers(),
            "total_clients": len(self.clients)
        }

# Global LLM manager instance
llm_manager = LLMManager()
