#!/usr/bin/env python3
"""
Memory Integration - Connect database to JARVIS memory system
"""

import sys
sys.path.append('/home/krawin/exp.code/jarvis')

from core.database.database_manager import db_manager
from typing import List, Dict, Any, Optional
import json
import logging

class MemoryIntegration:
    """Integration layer between JARVIS and database memory"""
    
    def __init__(self):
        self.logger = logging.getLogger("memory_integration")
        self.db = db_manager
    
    async def initialize(self):
        """Initialize database connections"""
        await self.db.initialize()
        return await self.db.health_check()
    
    async def save_conversation_turn(self, session_id: str, user_input: str, 
                                   assistant_response: str, model_used: str = None,
                                   tokens_used: int = None):
        """Save a conversation turn to persistent memory"""
        
        try:
            # Save to PostgreSQL
            conv_id = await self.db.save_conversation(
                session_id=session_id,
                user_message=user_input,
                assistant_response=assistant_response,
                tokens_used=tokens_used,
                model_used=model_used
            )
            
            # Cache recent conversation in Redis
            cache_key = f"recent_conv:{session_id}"
            recent_turns = await self.db.cache_get(cache_key) or []
            
            recent_turns.append({
                "user": user_input,
                "assistant": assistant_response,
                "timestamp": conv_id
            })
            
            # Keep only last 10 turns in cache
            if len(recent_turns) > 10:
                recent_turns = recent_turns[-10:]
            
            await self.db.cache_set(cache_key, recent_turns, expire=3600)
            
            self.logger.info(f"Saved conversation turn for session {session_id}")
            return conv_id
            
        except Exception as e:
            self.logger.error(f"Failed to save conversation: {e}")
            return None
    
    async def get_conversation_context(self, session_id: str, limit: int = 5):
        """Get recent conversation context"""
        
        try:
            # Try cache first
            cache_key = f"recent_conv:{session_id}"
            cached = await self.db.cache_get(cache_key)
            
            if cached and len(cached) >= limit:
                return cached[-limit:]
            
            # Fallback to database
            history = await self.db.get_conversation_history(session_id, limit)
            return history
            
        except Exception as e:
            self.logger.error(f"Failed to get conversation context: {e}")
            return []
    
    async def save_task_memory(self, task_title: str, task_description: str,
                              priority: str = "medium", metadata: Dict = None):
        """Save task to memory"""
        
        try:
            task_id = await self.db.save_task(
                title=task_title,
                description=task_description,
                priority=priority,
                metadata=metadata
            )
            
            self.logger.info(f"Saved task: {task_title}")
            return task_id
            
        except Exception as e:
            self.logger.error(f"Failed to save task: {e}")
            return None
    
    async def cache_llm_response(self, prompt_hash: str, response: str, 
                               model: str, expire: int = 1800):
        """Cache LLM response to avoid duplicate calls"""
        
        cache_key = f"llm_cache:{model}:{prompt_hash}"
        cache_data = {
            "response": response,
            "model": model,
            "cached_at": "now"
        }
        
        return await self.db.cache_set(cache_key, cache_data, expire)
    
    async def get_cached_llm_response(self, prompt_hash: str, model: str):
        """Get cached LLM response"""
        
        cache_key = f"llm_cache:{model}:{prompt_hash}"
        return await self.db.cache_get(cache_key)
    
    async def get_memory_status(self):
        """Get memory system status"""
        
        db_status = await self.db.health_check()
        
        return {
            "database_status": db_status,
            "memory_ready": db_status["overall"],
            "features": {
                "conversation_memory": db_status["postgres"],
                "semantic_search": db_status["qdrant"],
                "response_caching": db_status["redis"]
            }
        }

# Global memory integration instance
memory_integration = MemoryIntegration()
