#!/usr/bin/env python3
"""
Database Manager - Unified interface for PostgreSQL, Qdrant, and Redis
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import json
import uuid

@dataclass
class DatabaseConfig:
    """Database configuration"""
    postgres_url: str = "postgresql://jarvis:jarvis_secure_2024@localhost:5432/jarvis"
    qdrant_url: str = "http://localhost:6333"
    redis_url: str = "redis://:jarvis_redis_2024@localhost:6379"
    
class DatabaseManager:
    """Unified database manager for all JARVIS databases"""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self.logger = logging.getLogger("database_manager")
        
        # Connection pools
        self.postgres_pool = None
        self.qdrant_client = None
        self.redis_client = None
        
        # Connection status
        self.postgres_connected = False
        self.qdrant_connected = False
        self.redis_connected = False
    
    async def initialize(self):
        """Initialize all database connections"""
        self.logger.info("Initializing database connections...")
        
        # Initialize PostgreSQL
        await self._init_postgres()
        
        # Initialize Qdrant
        await self._init_qdrant()
        
        # Initialize Redis
        await self._init_redis()
        
        self.logger.info(f"Database status - PostgreSQL: {self.postgres_connected}, Qdrant: {self.qdrant_connected}, Redis: {self.redis_connected}")
    
    async def _init_postgres(self):
        """Initialize PostgreSQL connection"""
        try:
            import asyncpg
            
            self.postgres_pool = await asyncpg.create_pool(
                self.config.postgres_url,
                min_size=2,
                max_size=10,
                command_timeout=30
            )
            
            # Test connection
            async with self.postgres_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            
            self.postgres_connected = True
            self.logger.info("✅ PostgreSQL connected")
            
        except Exception as e:
            self.logger.error(f"❌ PostgreSQL connection failed: {e}")
            self.postgres_connected = False
    
    async def _init_qdrant(self):
        """Initialize Qdrant connection"""
        try:
            from qdrant_client import AsyncQdrantClient
            from qdrant_client.models import Distance, VectorParams
            
            self.qdrant_client = AsyncQdrantClient(url=self.config.qdrant_url)
            
            # Test connection and create collections
            collections = await self.qdrant_client.get_collections()
            
            # Create memory collection if not exists
            collection_names = [c.name for c in collections.collections]
            if "jarvis_memories" not in collection_names:
                await self.qdrant_client.create_collection(
                    collection_name="jarvis_memories",
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
                )
                self.logger.info("Created jarvis_memories collection")
            
            self.qdrant_connected = True
            self.logger.info("✅ Qdrant connected")
            
        except Exception as e:
            self.logger.error(f"❌ Qdrant connection failed: {e}")
            self.qdrant_connected = False
    
    async def _init_redis(self):
        """Initialize Redis connection"""
        try:
            import redis.asyncio as redis
            
            self.redis_client = redis.from_url(
                self.config.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            await self.redis_client.ping()
            
            self.redis_connected = True
            self.logger.info("✅ Redis connected")
            
        except Exception as e:
            self.logger.error(f"❌ Redis connection failed: {e}")
            self.redis_connected = False
    
    # PostgreSQL Operations
    async def save_conversation(self, session_id: str, user_message: str, 
                              assistant_response: str, tokens_used: int = None, 
                              model_used: str = None, metadata: Dict = None):
        """Save conversation to PostgreSQL"""
        if not self.postgres_connected:
            return None
        
        try:
            async with self.postgres_pool.acquire() as conn:
                result = await conn.fetchrow("""
                    INSERT INTO conversations (session_id, user_message, assistant_response, tokens_used, model_used, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id
                """, session_id, user_message, assistant_response, tokens_used, model_used, json.dumps(metadata or {}))
                
                return result['id']
        except Exception as e:
            self.logger.error(f"Failed to save conversation: {e}")
            return None
    
    async def get_conversation_history(self, session_id: str, limit: int = 10):
        """Get conversation history from PostgreSQL"""
        if not self.postgres_connected:
            return []
        
        try:
            async with self.postgres_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT user_message, assistant_response, timestamp, model_used
                    FROM conversations 
                    WHERE session_id = $1 
                    ORDER BY timestamp DESC 
                    LIMIT $2
                """, session_id, limit)
                
                return [dict(row) for row in reversed(rows)]
        except Exception as e:
            self.logger.error(f"Failed to get conversation history: {e}")
            return []
    
    async def save_task(self, title: str, description: str = None, 
                       priority: str = "medium", metadata: Dict = None):
        """Save task to PostgreSQL"""
        if not self.postgres_connected:
            return None
        
        try:
            async with self.postgres_pool.acquire() as conn:
                result = await conn.fetchrow("""
                    INSERT INTO tasks (title, description, priority, metadata)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id
                """, title, description, priority, json.dumps(metadata or {}))
                
                return result['id']
        except Exception as e:
            self.logger.error(f"Failed to save task: {e}")
            return None
    
    # Qdrant Operations (Vector Memory)
    async def save_memory_vector(self, content: str, vector: List[float], 
                               memory_type: str = "general", metadata: Dict = None):
        """Save memory with vector to Qdrant"""
        if not self.qdrant_connected:
            return None
        
        try:
            from qdrant_client.models import PointStruct
            
            point_id = str(uuid.uuid4())
            
            await self.qdrant_client.upsert(
                collection_name="jarvis_memories",
                points=[
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={
                            "content": content,
                            "memory_type": memory_type,
                            "timestamp": datetime.now().isoformat(),
                            **(metadata or {})
                        }
                    )
                ]
            )
            
            return point_id
        except Exception as e:
            self.logger.error(f"Failed to save memory vector: {e}")
            return None
    
    async def search_memories(self, query_vector: List[float], limit: int = 5):
        """Search similar memories using vector similarity"""
        if not self.qdrant_connected:
            return []
        
        try:
            results = await self.qdrant_client.search(
                collection_name="jarvis_memories",
                query_vector=query_vector,
                limit=limit
            )
            
            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "content": result.payload.get("content"),
                    "memory_type": result.payload.get("memory_type"),
                    "timestamp": result.payload.get("timestamp")
                }
                for result in results
            ]
        except Exception as e:
            self.logger.error(f"Failed to search memories: {e}")
            return []
    
    # Redis Operations (Caching)
    async def cache_set(self, key: str, value: Any, expire: int = 3600):
        """Set cache value in Redis"""
        if not self.redis_connected:
            return False
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            await self.redis_client.setex(key, expire, value)
            return True
        except Exception as e:
            self.logger.error(f"Failed to set cache: {e}")
            return False
    
    async def cache_get(self, key: str):
        """Get cache value from Redis"""
        if not self.redis_connected:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except:
                    return value
            return None
        except Exception as e:
            self.logger.error(f"Failed to get cache: {e}")
            return None
    
    async def cache_delete(self, key: str):
        """Delete cache key from Redis"""
        if not self.redis_connected:
            return False
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete cache: {e}")
            return False
    
    # Health Check
    async def health_check(self):
        """Check health of all databases"""
        status = {
            "postgres": self.postgres_connected,
            "qdrant": self.qdrant_connected,
            "redis": self.redis_connected,
            "overall": self.postgres_connected and self.qdrant_connected and self.redis_connected
        }
        
        return status
    
    async def close(self):
        """Close all database connections"""
        if self.postgres_pool:
            await self.postgres_pool.close()
        
        if self.qdrant_client:
            await self.qdrant_client.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        self.logger.info("All database connections closed")

# Global database manager instance
db_manager = DatabaseManager()
