#!/usr/bin/env python3
"""
Mock Database Implementation for Testing
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

class MockDatabase:
    """Mock database for testing without real connections"""
    
    def __init__(self):
        self.logger = logging.getLogger("mock_database")
        
        # In-memory storage
        self.conversations = []
        self.tasks = []
        self.memories = []
        self.cache = {}
        self.vector_store = []
        
        self.connected = True
    
    async def save_conversation(self, session_id: str, user_message: str, 
                              assistant_response: str, tokens_used: int = None, 
                              model_used: str = None, metadata: Dict = None):
        """Mock save conversation"""
        
        conv_id = str(uuid.uuid4())
        conversation = {
            "id": conv_id,
            "session_id": session_id,
            "user_message": user_message,
            "assistant_response": assistant_response,
            "tokens_used": tokens_used,
            "model_used": model_used,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.conversations.append(conversation)
        self.logger.info(f"Mock: Saved conversation {conv_id}")
        return conv_id
    
    async def get_conversation_history(self, session_id: str, limit: int = 10):
        """Mock get conversation history"""
        
        session_convs = [c for c in self.conversations if c["session_id"] == session_id]
        return session_convs[-limit:] if session_convs else []
    
    async def save_task(self, title: str, description: str = None, 
                       priority: str = "medium", metadata: Dict = None):
        """Mock save task"""
        
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        self.tasks.append(task)
        self.logger.info(f"Mock: Saved task {task_id}")
        return task_id
    
    async def cache_set(self, key: str, value: Any, expire: int = 3600):
        """Mock cache set"""
        
        self.cache[key] = {
            "value": value,
            "expires_at": datetime.now().timestamp() + expire
        }
        return True
    
    async def cache_get(self, key: str):
        """Mock cache get"""
        
        if key in self.cache:
            item = self.cache[key]
            if datetime.now().timestamp() < item["expires_at"]:
                return item["value"]
            else:
                del self.cache[key]
        return None
    
    async def save_memory_vector(self, content: str, vector: List[float], 
                               memory_type: str = "general", metadata: Dict = None):
        """Mock save memory vector"""
        
        memory_id = str(uuid.uuid4())
        memory = {
            "id": memory_id,
            "content": content,
            "vector": vector,
            "memory_type": memory_type,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.vector_store.append(memory)
        self.logger.info(f"Mock: Saved memory vector {memory_id}")
        return memory_id
    
    async def search_memories(self, query_vector: List[float], limit: int = 5):
        """Mock search memories (simple random selection)"""
        
        import random
        
        # Simple mock: return random memories with fake scores
        results = []
        available_memories = self.vector_store[:limit]
        
        for memory in available_memories:
            results.append({
                "id": memory["id"],
                "score": random.uniform(0.7, 0.95),  # Mock similarity score
                "content": memory["content"],
                "memory_type": memory["memory_type"],
                "timestamp": memory["timestamp"]
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def get_stats(self):
        """Get mock database stats"""
        return {
            "conversations": len(self.conversations),
            "tasks": len(self.tasks),
            "memories": len(self.vector_store),
            "cache_items": len(self.cache),
            "connected": self.connected
        }

# Test the mock database
async def test_mock_database():
    print("🧪 Method 3: Mock Database Test")
    print("=" * 35)
    
    mock_db = MockDatabase()
    
    # Test conversation saving
    conv_id = await mock_db.save_conversation(
        session_id="test_session_1",
        user_message="Hello JARVIS!",
        assistant_response="Hello! How can I help you?",
        tokens_used=25,
        model_used="qwen3-coder-plus"
    )
    print(f"✅ Saved conversation: {conv_id[:8]}...")
    
    # Test task saving
    task_id = await mock_db.save_task(
        title="Test database integration",
        description="Verify all database operations work correctly",
        priority="high"
    )
    print(f"✅ Saved task: {task_id[:8]}...")
    
    # Test caching
    await mock_db.cache_set("test_key", {"message": "Cache works!"})
    cached_value = await mock_db.cache_get("test_key")
    print(f"✅ Cache test: {cached_value}")
    
    # Test vector memory
    fake_vector = [0.1] * 1536  # Mock 1536-dimensional vector
    memory_id = await mock_db.save_memory_vector(
        content="JARVIS can remember important information",
        vector=fake_vector,
        memory_type="system_knowledge"
    )
    print(f"✅ Saved memory vector: {memory_id[:8]}...")
    
    # Test memory search
    search_results = await mock_db.search_memories(fake_vector, limit=3)
    print(f"✅ Memory search: Found {len(search_results)} results")
    
    # Test conversation history
    history = await mock_db.get_conversation_history("test_session_1")
    print(f"✅ Conversation history: {len(history)} messages")
    
    # Get stats
    stats = mock_db.get_stats()
    print(f"\n📊 Mock Database Stats:")
    print(f"   Conversations: {stats['conversations']}")
    print(f"   Tasks: {stats['tasks']}")
    print(f"   Memories: {stats['memories']}")
    print(f"   Cache Items: {stats['cache_items']}")
    print(f"   Connected: {stats['connected']}")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_mock_database())
    print(f"\n🎯 Mock Database Test: {'PASS' if result else 'FAIL'}")
