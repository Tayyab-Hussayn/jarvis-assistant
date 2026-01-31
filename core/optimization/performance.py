"""
Performance Optimization - Caching and optimization systems
"""

import time
import asyncio
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from functools import wraps

@dataclass
class CacheEntry:
    value: Any
    timestamp: float
    ttl: float
    hit_count: int = 0

class SimpleCache:
    """Simple in-memory cache with TTL"""
    
    def __init__(self, default_ttl: float = 300):  # 5 minutes
        self.cache: Dict[str, CacheEntry] = {}
        self.default_ttl = default_ttl
        self.stats = {"hits": 0, "misses": 0}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry.timestamp < entry.ttl:
                entry.hit_count += 1
                self.stats["hits"] += 1
                return entry.value
            else:
                del self.cache[key]
        
        self.stats["misses"] += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        self.cache[key] = CacheEntry(value, time.time(), ttl)
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.stats = {"hits": 0, "misses": 0}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total if total > 0 else 0
        
        return {
            "entries": len(self.cache),
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": hit_rate
        }

def cached(ttl: float = 300):
    """Decorator for caching function results"""
    def decorator(func: Callable):
        cache = SimpleCache(ttl)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Execute function and cache result
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            cache.set(key, result)
            return result
        
        wrapper.cache = cache
        return wrapper
    return decorator

class PerformanceProfiler:
    """Simple performance profiler"""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
    
    def record(self, operation: str, duration: float):
        """Record operation duration"""
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(duration)
    
    def get_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for operation"""
        if operation not in self.metrics:
            return {}
        
        durations = self.metrics[operation]
        return {
            "count": len(durations),
            "avg": sum(durations) / len(durations),
            "min": min(durations),
            "max": max(durations),
            "total": sum(durations)
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get all operation statistics"""
        return {op: self.get_stats(op) for op in self.metrics.keys()}

def profile_performance(operation_name: str):
    """Decorator for profiling function performance"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                performance_profiler.record(operation_name, duration)
        
        return wrapper
    return decorator

class OptimizationEngine:
    """Main optimization engine"""
    
    def __init__(self):
        self.cache = SimpleCache()
        self.profiler = PerformanceProfiler()
        self.optimizations_applied = []
    
    def apply_caching(self, func: Callable, ttl: float = 300) -> Callable:
        """Apply caching to function"""
        cached_func = cached(ttl)(func)
        self.optimizations_applied.append(f"Caching applied to {func.__name__}")
        return cached_func
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get optimization report"""
        return {
            "cache_stats": self.cache.get_stats(),
            "performance_stats": self.profiler.get_all_stats(),
            "optimizations_applied": self.optimizations_applied,
            "recommendations": [
                "Consider increasing cache TTL for stable data",
                "Profile slow operations for further optimization",
                "Implement request batching for external APIs"
            ]
        }

# Global instances
performance_profiler = PerformanceProfiler()
optimization_engine = OptimizationEngine()
