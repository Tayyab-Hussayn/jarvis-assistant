"""
Quota Management System for LLM providers
"""

import time
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

class QuotaStatus(Enum):
    AVAILABLE = "available"
    LIMITED = "limited"
    EXCEEDED = "exceeded"
    UNKNOWN = "unknown"

@dataclass
class QuotaInfo:
    """Quota information for a provider"""
    provider: str
    status: QuotaStatus
    requests_made: int = 0
    last_error_time: Optional[float] = None
    cooldown_until: Optional[float] = None
    error_count: int = 0

class QuotaManager:
    """Manages API quotas and provider fallbacks"""
    
    def __init__(self):
        self.logger = logging.getLogger("quota_manager")
        self.quotas: Dict[str, QuotaInfo] = {}
        self.provider_priority = ["qwen", "gemini", "ollama"]
        
    def get_quota_info(self, provider: str) -> QuotaInfo:
        """Get quota information for provider"""
        if provider not in self.quotas:
            self.quotas[provider] = QuotaInfo(provider, QuotaStatus.AVAILABLE)
        return self.quotas[provider]
    
    def record_success(self, provider: str):
        """Record successful API call"""
        quota = self.get_quota_info(provider)
        quota.requests_made += 1
        quota.status = QuotaStatus.AVAILABLE
        quota.error_count = 0
        quota.last_error_time = None
        quota.cooldown_until = None
    
    def record_quota_error(self, provider: str, error_message: str):
        """Record quota exceeded error"""
        quota = self.get_quota_info(provider)
        quota.error_count += 1
        quota.last_error_time = time.time()
        
        if "quota" in error_message.lower() or "429" in error_message:
            quota.status = QuotaStatus.EXCEEDED
            # Set cooldown for 5 minutes
            quota.cooldown_until = time.time() + 300
            self.logger.warning(f"⚠️ {provider} quota exceeded, cooldown until {time.ctime(quota.cooldown_until)}")
        else:
            quota.status = QuotaStatus.LIMITED
    
    def is_provider_available(self, provider: str) -> bool:
        """Check if provider is available for use"""
        quota = self.get_quota_info(provider)
        
        # Check cooldown
        if quota.cooldown_until and time.time() < quota.cooldown_until:
            return False
        
        # Reset status if cooldown expired
        if quota.cooldown_until and time.time() >= quota.cooldown_until:
            quota.status = QuotaStatus.AVAILABLE
            quota.cooldown_until = None
            quota.error_count = 0
        
        return quota.status in [QuotaStatus.AVAILABLE, QuotaStatus.LIMITED]
    
    def get_best_provider(self, available_providers: list) -> Optional[str]:
        """Get the best available provider"""
        for provider in self.provider_priority:
            if provider in available_providers and self.is_provider_available(provider):
                return provider
        
        # If no priority provider available, try any available
        for provider in available_providers:
            if self.is_provider_available(provider):
                return provider
        
        return None
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get quota status summary"""
        summary = {}
        for provider, quota in self.quotas.items():
            summary[provider] = {
                "status": quota.status.value,
                "requests_made": quota.requests_made,
                "error_count": quota.error_count,
                "cooldown_remaining": max(0, quota.cooldown_until - time.time()) if quota.cooldown_until else 0
            }
        return summary

# Global quota manager
quota_manager = QuotaManager()
