#!/usr/bin/env python3
"""
Mock LLM Client for Testing - Provides realistic responses without API calls
"""

import asyncio
import random
from typing import Dict, List, Optional
from core.llm.llm_manager import BaseLLMClient, LLMConfig, LLMResponse, LLMProvider

class MockLLMClient(BaseLLMClient):
    """Mock LLM client for testing and development"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        
        # Predefined responses for different types of prompts
        self.responses = {
            "greeting": [
                "Hello! I'm JARVIS, your AI assistant. I'm working correctly and ready to help you with any tasks.",
                "Greetings! JARVIS here, functioning properly and at your service.",
                "Hi there! This is JARVIS, and I'm operating normally. How can I assist you today?"
            ],
            "task_analysis": [
                "I'll analyze this task systematically. Let me break it down into manageable components and create a strategic approach.",
                "This task requires careful planning. I'll decompose it into logical steps and identify the key requirements.",
                "Let me examine this task from multiple angles to ensure we have a comprehensive execution plan."
            ],
            "planning": [
                "Based on my analysis, here's a structured approach:\n1. Initial setup and preparation\n2. Core implementation phase\n3. Testing and validation\n4. Final optimization and deployment",
                "I recommend this strategic breakdown:\n• Phase 1: Requirements gathering\n• Phase 2: Design and architecture\n• Phase 3: Implementation\n• Phase 4: Quality assurance",
                "Here's my recommended execution plan:\nStep 1: Foundation setup\nStep 2: Core development\nStep 3: Integration testing\nStep 4: Production deployment"
            ],
            "code_analysis": [
                "Looking at this code, I can see several areas for improvement in terms of structure, efficiency, and maintainability.",
                "This code demonstrates good practices in some areas, but there are opportunities for optimization and better error handling.",
                "The code architecture is solid, though I'd suggest some refactoring for better modularity and performance."
            ],
            "default": [
                "I understand your request. Let me provide a thoughtful and comprehensive response based on the information provided.",
                "Thank you for your question. I'll analyze this carefully and provide you with a detailed, helpful response.",
                "I'm processing your request and will provide you with accurate, relevant information to address your needs."
            ]
        }
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> LLMResponse:
        """Generate mock response based on prompt content"""
        
        # Simulate API delay
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Analyze prompt to choose appropriate response type
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["hello", "hi", "greeting", "working"]):
            response_type = "greeting"
        elif any(word in prompt_lower for word in ["task", "analyze", "break down", "decompose"]):
            response_type = "task_analysis"
        elif any(word in prompt_lower for word in ["plan", "strategy", "approach", "steps"]):
            response_type = "planning"
        elif any(word in prompt_lower for word in ["code", "function", "class", "implementation"]):
            response_type = "code_analysis"
        else:
            response_type = "default"
        
        # Select random response from appropriate category
        responses = self.responses.get(response_type, self.responses["default"])
        content = random.choice(responses)
        
        # Add context from system prompt if provided
        if system_prompt and "jarvis" in system_prompt.lower():
            content = f"As JARVIS, {content.lower()}"
        
        return LLMResponse(
            content=content,
            model=self.config.model,
            provider=self.config.provider.value,
            tokens_used=random.randint(50, 200),
            metadata={"mock": True, "response_type": response_type}
        )
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Handle chat conversation with context awareness"""
        
        # Simulate API delay
        await asyncio.sleep(random.uniform(0.8, 2.0))
        
        # Get the last user message
        user_messages = [msg for msg in messages if msg["role"] == "user"]
        if not user_messages:
            return await self.generate("Hello", **kwargs)
        
        last_message = user_messages[-1]["content"]
        
        # Check for conversation context
        conversation_context = ""
        if len(messages) > 2:
            conversation_context = " I see we're continuing our conversation. "
        
        # Generate response based on last message
        base_response = await self.generate(last_message, **kwargs)
        
        # Modify response to include conversation context
        content = conversation_context + base_response.content
        
        return LLMResponse(
            content=content,
            model=self.config.model,
            provider=self.config.provider.value,
            tokens_used=random.randint(75, 250),
            metadata={"mock": True, "conversation_length": len(messages)}
        )

# Function to add mock client to LLM manager
def add_mock_client():
    """Add mock client to LLM manager for testing"""
    from core.llm.llm_manager import llm_manager, LLMConfig, LLMProvider
    
    mock_config = LLMConfig(
        provider=LLMProvider.OLLAMA,  # Use OLLAMA enum for mock
        model="mock-jarvis-v1",
        base_url="mock://localhost",
        temperature=0.7
    )
    
    # Create mock client
    mock_client = MockLLMClient(mock_config)
    
    # Register with LLM manager
    llm_manager.clients["mock"] = mock_client
    
    # Set as current provider if no other is available
    if not llm_manager.current_provider or llm_manager.current_provider not in llm_manager.clients:
        llm_manager.current_provider = "mock"
    
    return mock_client
